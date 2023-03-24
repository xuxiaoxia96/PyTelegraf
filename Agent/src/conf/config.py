# -*- coding:utf-8 -*-
"""
    config.py

"""
import os
import os.path
import sys
import time
from hashlib import md5
from typing import Any, Callable, Union
import socket
from envcrypto import get_environ, set_environ
from loguru import logger
from yaml import safe_dump, safe_load

from .plugins import PLUGINS
from ..libs.helper import extend_dict, get_dict_value, get_hash
from ..libs.net import request


class Config:
    """系统配置"""
    debug = False
    reload_sec = 300

    # 主配置
    main = {}

    # 服务器信息
    info = {}

    # 插件配置
    input = {}
    processor = {}
    aggs = {}
    output = {}

    # 插件集
    plugins = {}
    
    ip_map = {
        "9.135.93.3": "devcloud",
        "11.177.154.33": "trunk",
        "11.177.154.132": "smoke",
        "11.177.155.9": "test1_1",
        "11.177.155.86": "test1_2",

        "11.177.154.194": "test1_3",
        "11.177.155.130": "test1_4",
        "11.177.155.168": "test1_5",
        "11.177.154.240": "test1_6",
        "11.181.33.188": "clientprof" ,
        "11.177.154.224": "client_engine",
        "11.181.32.180": "weak_network",
        "11.177.159.161": "dev1",
        "11.177.159.237": "dev2_1",
        "11.177.159.183": "dev2_2",
        "11.177.159.47": "dev2_3",
        "11.177.159.254": "dev2_4",
        "11.177.159.254": "dev2_5",
        "11.177.159.196": "dev2_6",
        "11.177.159.236": "dev2_7",
        "11.181.33.75": "test2",
        "11.181.32.185": "test3",
        "11.177.155.252": "test4",
        "11.177.155.254": "test5",
        "11.154.164.43": "ss1",
        "11.154.164.49": "ss2",
        "11.154.169.184": "test_branch",
        "49.51.244.143": "na_test",
    }

    # 工作中, 公共的, 开启的插件名称
    plugins_working = set()
    plugins_common = set()
    plugins_open = set()

    # 模块
    modules = ['input', 'processor', 'aggs', 'output', 'common']

    # 日志配置签名
    _logger_conf_md5 = ''

    def __init__(self) -> None:
        # 运行根目录
        self.root_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        # 脚本文件根目录
        self.src_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        # 配置文件目录
        self.etc_dir = os.path.join(self.root_dir, 'etc')
        # 默认主配置文件路径
        self.main_yaml = os.path.join(self.etc_dir, 'main.yaml')
        # 主机专属主配置文件路径
        self.host_yaml = os.path.join(self.etc_dir, 'host.yaml')

        # 初始化配置
        self.reload()

        # 初始化插件(扫描目录, 自动发现)
        # self.plugins = {x: self.get_plugins(x) for x in self.modules}
        # 初始化插件(打包使用, 需要静态注册到 plugins.py)
        self.plugins = PLUGINS

    async def update(self):
        """从配置中心获取并更新 main.yaml, host.yaml"""
        
        timestamp = int(time.time())
        # token = get_hash(f'{timestamp}{api_key}')
        # server端拉取最新的配置
        new_conf = await request('http://9.134.167.143:1234/update_config', 'GET')
        print(new_conf)
        print(type(new_conf))
        
        # main_conf = get_dict_value(new_conf, 'data|main', {})
        host_conf = get_dict_value(new_conf, 'data|host', {})
        if not new_conf:
            logger.warning(f'配置更新失败, 默认主配置有误: {new_conf.get("msg")}')
            return

        # 更新默认主配置文件
        self.dump_yaml_file(new_conf, self.main_yaml)
        # 更新主机配置文件

    def reload(self):
        """
        重新加载所有配置
        配置优先级: 各插件目录(input/processor/aggs/output) > host.yaml > main.yaml
        """
        # 加载主配置
        host = self.load_yaml_file(self.host_yaml)
        host['info']['node_ip'] = self.get_ip()
        host['info']['host_name'] = self.ip_map[host['info']['node_ip']]
        self.dump_yaml_file(host, self.host_yaml)    
        host = self.load_yaml_file(self.host_yaml)
        # 加载通用配置
        main = self.load_yaml_file(self.main_yaml)
        if not main or get_dict_value(main, 'interval', 0) <= 0:
            logger.warning('配置加载失败, 默认主配置有误')
            return


        # 扩展合并主配置
        self.main = extend_dict(main, host)
        self.debug = self.get_conf_value('main|debug', False)
        self.info = self.get_conf_value('main|info', {})
        self.reload_sec = max(self.get_conf_value('main|reload_sec', 300), 1)
        self.plugins_open = get_dict_value(self.main, 'open', set())

        # 配置的组织方式
        print(self.modules)
        for module in self.modules:
            conf = {'default': {}}
            # 主配置中的公共插件
            plugins_common = get_dict_value(self.main, f'common_{module}', set())
            self.plugins_common.update(plugins_common)
            # 开启的插件 + 公共插件
            plugins = plugins_common | self.plugins_open
            for name in plugins:
                # 初始化插件配置
                conf.update({name: {}})
                # 主配置中的插件配置
                main_plugin_conf = self.get_conf_value(f'main|{module}|{name}', {})
                main_plugin_conf and isinstance(main_plugin_conf, dict) and conf[name].update(main_plugin_conf)
                # 插件配置文件
                plugin_conf = self.get_conf(module, name)
                plugin_conf and conf[name].update(plugin_conf)
            setattr(self, module, conf)

        # 初始化日志
        self.init_logger()

    def get_conf_value(
            self,
            key_path: str,
            default: Any = None,
            *,
            fix_type: bool = True
    ) -> Any:
        """
        按路径字符串获取配置项值
        默认转换为默认值相同类型, None 除外

        :param key_path: str, e.g. input|demo|interval
        :param default:
        :param fix_type: 是否强制修正为 default 相同类型
        :return:
        """
        keys = key_path.split('|')
        if not hasattr(self, keys[0]):
            return default

        # 配置项: self.main, self.input...
        dt = getattr(self, keys[0])

        if len(keys) == 1:
            return dt

        value = dt
        for key in keys[1:]:
            try:
                value = value.get(key, None)
                if value is None:
                    return default
            except Exception:  
                return default

        if fix_type:
            return self.get_same_type(default, value)

        return value

    @staticmethod
    def get_same_type(src: Any, dst: Any) -> Any:
        """将 dst 的类型转换为 src 相同的类型"""
        if src is None:
            return dst

        if isinstance(src, bool):
            return str(dst) in ('1', 't', 'T', 'true', 'TRUE', 'True')

        try:
            return type(src)(dst)
        except Exception:
            return src

    def get_conf(
            self, conf_module: str, conf_name: str
    ) -> dict:
        """按模块和名称获取配置"""
        return self.load_yaml_file(os.path.join(self.etc_dir, conf_module, f'{conf_name}.yaml'))

    @staticmethod
    def dump_yaml_file(data: dict, yaml_file: str) -> Union[str, bytes]:
        """写入 YAML 配置文件"""
        try:
            with open(yaml_file, 'w', encoding='utf-8') as f:
                return safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            logger.warning(f'配置文件写入失败: {e}')
            return ''

    @staticmethod
    def load_yaml_file(yaml_file: str) -> dict:
        """读取 YAML 配置文件"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                conf = safe_load(f)
                return conf if isinstance(conf, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def load_yaml(yaml_conf: str) -> dict:
        """读取 YAML 配置"""
        try:
            conf = safe_load(yaml_conf)
            return conf if isinstance(conf, dict) else {}
        except Exception:
            return {}
        
    def get_ip(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('10.0.0.1',8080))
        ip = s.getsockname()[0]
        return ip
    

    def get_plugin_obj(
            self, module: str, name: str, default: Any = None
    ) -> Callable:
        """获取插件对象"""
        return self.plugins.get(module, {}).get(name, default)

    def get_plugins(self, module: str) -> dict:
        """获取插件列表"""
        plugins = {}
        path = os.path.join(self.src_dir, module)
        for _, _, files in os.walk(path):
            for f in files:
                name, ext = os.path.splitext(f)
                cls_name = name.title()
                if ext == '.py':
                    mod = __import__(f'src.{module}.{name}', fromlist=[__name__])
                    hasattr(mod, cls_name) and plugins.update({name: getattr(mod, cls_name)})

        return plugins

    def init_logger(self) -> None:
        """初始化日志"""
        logger_conf_md5 = md5('{}.{}'.format(self.get_conf_value('main|log'), self.debug).encode()).hexdigest()
        if logger_conf_md5 == self._logger_conf_md5:
            return

        self._logger_conf_md5 = logger_conf_md5
        logger.remove()

        if self.debug:
            # 控制台日志
            logger.add(
                sys.stderr,
                level='DEBUG',
                format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                       '<level>{level}</level> | '
                       '<cyan>{name}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
                       '<level>{message}</level>',
            )

        # 文件日志
        logger.add(
            self.get_conf_value('main|log|file', os.path.join(self.root_dir, 'log', 'pyagent.log')),
            level=self.get_conf_value('main|log|level', 'INFO'),
            rotation=self.get_conf_value('main|log|rotation', '50 MB'),
            retention=self.get_conf_value('main|log|retention', '10 days'),
            compression=self.get_conf_value('main|log|compression', 'zip'),
            format=self.get_conf_value('main|log|format',
                                       '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}.{function}:{line} | {message}'),
            enqueue=True,
        )
        logger.debug('日志初始化完成')
    


    def __str__(self) -> str:
        return str(self.__dict__)
