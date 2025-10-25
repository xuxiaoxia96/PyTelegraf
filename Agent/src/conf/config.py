# -*- coding:utf-8 -*-
"""
    config.py
"""
import os
import os.path
import sys
import json
from hashlib import md5
from typing import Any
import socket

# 移除envcrypto导入，因为它无法解析
# 可以根据需要添加替代实现

# 尝试导入第三方库，如果失败则提供基本功能
try:
    from loguru import logger
except ImportError:
    # 简单的日志替代实现
    def logger_func(level, msg):
        """打印日志信息"""
        print(f'[{level}] {msg}')

    class MockLogger:
        """模拟日志类，当loguru不可用时使用"""

        def debug(self, msg):
            """打印调试日志"""
            logger_func('DEBUG', msg)

        def info(self, msg):
            """打印信息日志"""
            logger_func('INFO', msg)

        def warning(self, msg):
            """打印警告日志"""
            logger_func('WARNING', msg)

        def error(self, msg):
            """打印错误日志"""
            logger_func('ERROR', msg)

        def remove(self):
            """移除日志处理器"""
            # 空实现，无需pass

        def add(self, *args, **kwargs):
            """添加日志处理器"""
            # 空实现，无需pass

    logger = MockLogger()

try:
    from yaml import safe_dump, safe_load
    # 修复类型注解问题 - 直接使用原始函数，无需包装
    # 导入时就已经解决了类型问题
except ImportError:
    # 简单的YAML替代实现
    def safe_dump(data, stream):
        """使用JSON替代实现YAML序列化"""
        stream.write(json.dumps(data, ensure_ascii=False))

    def safe_load(stream):
        """使用JSON替代实现YAML反序列化"""
        try:
            return json.load(stream)
        except (ValueError, TypeError):
            return {}

from .plugins import PLUGINS
from ..libs.helper import extend_dict, get_dict_value
from ..libs.net import request


class Config:
    """系统配置管理类"""
    # 基础配置
    debug = False
    reload_sec = 300

    # 模块定义
    modules = ['input', 'processor', 'aggs', 'output', 'common']

    # IP映射表
    ip_map = {
        "9.135.93.3": "devcloud",
    }

    def __init__(self) -> None:
        """初始化配置管理器"""
        # 使用内部字典存储所有配置和状态，减少类属性数量
        root_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        src_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        etc_dir = os.path.join(root_dir, 'etc')

        self._state = {
            # 路径配置
            'paths': {
                'root_dir': root_dir,
                'src_dir': src_dir,
                'etc_dir': etc_dir,
                'conf_dir': os.path.join(root_dir, 'conf'),
                'main_yaml': os.path.join(etc_dir, 'main.yaml'),
                'host_yaml': os.path.join(etc_dir, 'host.yaml')
            },
            # 插件存储
            'plugins': {},
            # 主配置
            'main': {},
            # 主机信息
            'info': {},
            # 日志配置MD5
            'logger_conf_md5': '',
            # 插件状态
            'plugins_working': set(),
            'plugins_common': set(),
            'plugins_open': set()
        }

        # 各模块配置
        for module in self.modules:
            self._state[module] = {'default': {}}

        # 初始化配置
        self.reload()

        # 初始化插件(打包使用, 需要静态注册到 plugins.py)
        self._state['plugins'] = PLUGINS

    async def update(self):
        """从配置中心获取并更新 main.yaml, host.yaml"""
        try:
            # 从配置中心拉取最新配置
            new_conf = await request(
                'http://9.134.167.143:1234/update_config', 'GET')
            logger.debug('配置获取')

            # 检查配置是否有效
            if not new_conf or not isinstance(new_conf, dict):
                logger.warning('配置更新失败: 从配置中心获取的配置无效')
                return
            # 更新主配置文件
            # 主配置
            m = get_dict_value(new_conf, 'data|main', {})
            if isinstance(m, dict):
                self.dump_yaml_file(m, self._state['paths']['main_yaml'])
                logger.debug('1')
            # 主机配置
            h = get_dict_value(new_conf, 'data|host', {})
            if isinstance(h, dict):
                self.dump_yaml_file(h, self._state['paths']['host_yaml'])
                logger.debug('2')
        except (OSError, RuntimeError, ValueError) as e:
            logger.error(f'配置更新失败: {str(e)}')

    def reload(self):
        """
        重新加载所有配置
        配置优先级: 各插件目录(input/processor/aggs/output) > host.yaml > main.yaml
        """
        try:
            logger.debug('开始重新加载配置')
            # 加载主机配置
            host = self.load_yaml_file(self._state['paths']['host_yaml'])
            if not isinstance(host, dict):
                host = {}
            # 设置主机信息
            host.setdefault('info', {})
            host['info']['node_ip'] = self.get_ip()
            ip = host['info']['node_ip']
            host['info']['host_name'] = self.ip_map.get(ip, 'unknown')
            # 保存更新后的主机配置
            self.dump_yaml_file(host, self._state['paths']['host_yaml'])
            # 重新加载更新后的主机配置
            host = self.load_yaml_file(self._state['paths']['host_yaml'])

            # 加载主配置
            main = self.load_yaml_file(self._state['paths']['main_yaml'])
            if not main or not isinstance(main, dict):
                logger.warning('配置加载失败')
                return
            interval_value = get_dict_value(main, 'interval', 0)
            valid = isinstance(interval_value, (int, float))
            if valid and interval_value <= 0:
                logger.warning('配置')
                return

            # 扩展合并主配置
            self._state['main'] = extend_dict(main, host)
            self.debug = self.get_conf_value('main|debug', False)
            self._state['info'] = self.get_conf_value('main|info', {})
            # 重新加载间隔
            reload_sec = self.get_conf_value('main|reload_sec', 300)
            # 确保reload_sec是整数
            if reload_sec is None:
                reload_sec = 300
            self.reload_sec = max(int(reload_sec), 1)

            # 安全地将配置转换为集合
            open_plugins = get_dict_value(self._state['main'], 'open', set())
            if isinstance(open_plugins, (list, set)):
                self._state['plugins_open'] = set(open_plugins)
            else:
                self._state['plugins_open'] = set()

            # 初始化各模块配置
            for module in self.modules:
                conf = {'default': {}}
                # 主配置中的公共插件
                plugins_common = get_dict_value(
                    self._state['main'], f'common_{module}', set())
                if isinstance(plugins_common, (list, set)):
                    self._state['plugins_common'].update(plugins_common)
                # 合并
                # 合并插件
                plugins = (self._state['plugins_common'] |
                           self._state['plugins_open'])

                for name in plugins:
                    # 初始化插件配置
                    conf.update({name: {}})
                    # 主配置中的插件配置
                    main_plugin_conf = self.get_conf_value(
                        f'main|{module}|{name}', {})
                    if isinstance(main_plugin_conf, dict):
                        conf[name].update(main_plugin_conf)
                    # 插件配置文件
                    plugin_conf = self.get_conf(module, name)
                    if isinstance(plugin_conf, dict):
                        conf[name].update(plugin_conf)

                self._state[module] = conf

            # 初始化日志
            self.init_logger()
            logger.debug('配置重载完成')

        except (OSError, RuntimeError, ValueError) as e:
            logger.error(f'配置重载失败: {str(e)}')

    def get_conf_value(self, key_path, default=None, *, fix_type=True):
        """获取配置值"""
        if not key_path or not isinstance(key_path, str):
            return default
        keys = key_path.split('|')
        if keys[0] not in self._state and not hasattr(self, keys[0]):
            return default

        # 配置项: self._state['main'], self._state['input']...
        dt = self._state.get(keys[0], getattr(self, keys[0], {}))

        if len(keys) == 1:
            return dt

        value = dt
        for key in keys[1:]:
            try:
                value = value.get(key, None)
                if value is None:
                    return default
            except (AttributeError, KeyError, TypeError) as e:
                logger.debug(f'获取配置项失败: {key}, 错误: {str(e)}')
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
        except (ValueError, TypeError) as e:
            logger.debug(f'类型转换失败: {str(e)}')
            return src

    def get_conf(self, conf_module: str, conf_name: str) -> dict:
        """按模块和名称获取配置"""
        yaml_path = os.path.join(
                self._state['paths']['etc_dir'],
                conf_module,
                f'{conf_name}.yaml')
        return self.load_yaml_file(yaml_path)

    @staticmethod
    def dump_yaml_file(data, file_path):
        """写入配置"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                from yaml import safe_dump
                safe_dump(data, f)
                return True
        except Exception as e:
            logger.warning(f'配置文件写入失败: {e}')
            return ''

    @staticmethod
    def load_yaml_file(file_path):
        """加载配置"""
        if not file_path or not isinstance(file_path, str):
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conf = safe_load(f)
                return conf if isinstance(conf, dict) else {}
        except (OSError, IOError, ValueError) as e:
            logger.debug(f'加载配置文件失败: {file_path}, 错误: {str(e)}')
            return {}

    @staticmethod
    def load_yaml(yaml_conf):
        """读取 YAML 配置字符串"""
        try:
            conf = safe_load(yaml_conf)
            return conf if isinstance(conf, dict) else {}
        except ValueError as e:
            logger.debug(f'解析YAML配置失败: {str(e)}')
            return {}

    def get_ip(self):
        """获取本机IP地址"""
        ip = '127.0.0.1'  # 默认值
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 使用一个不会实际连接的地址来获取本机IP
            s.connect(('10.0.0.1', 8080))
            ip = s.getsockname()[0]
        except (OSError, socket.error) as e:
            logger.error(f'获取本机IP失败: {str(e)}')
        finally:
            # 确保关闭socket
            if s:
                try:
                    s.close()
                except OSError as e:
                    logger.debug(f'关闭socket失败: {str(e)}')
        return ip

    def get_plugin_obj(self, module, name, default=None):
        """获取插件对象"""
        return self._state['plugins'].get(module, {}).get(name, default)

    def get_plugins(self, module: str) -> dict:
        """获取插件列表"""
        plugins = {}
        path = os.path.join(self._state['paths']['src_dir'], module)
        for _, _, files in os.walk(path):
            for f in files:
                name, ext = os.path.splitext(f)
                cls_name = name.title()
                if ext == '.py':
                    try:
                        mod_path = f'src.{module}.{name}'
                        mod = __import__(mod_path, fromlist=[__name__])
                        if hasattr(mod, cls_name):
                            plugins.update({name: getattr(mod, cls_name)})
                    except ImportError:
                        logger.debug(f'{module}.{name}')

        return plugins

    def init_logger(self):
        """初始化日志系统"""
        log_config = self.get_conf_value('main|log')
        m = md5(f'{log_config}.{self.debug}'.encode()).hexdigest()
        logger_conf_md5 = m
        if logger_conf_md5 == self._state['logger_conf_md5']:
            return

        self._state['logger_conf_md5'] = logger_conf_md5
        logger.remove()

        if self.debug:
            # 控制台日志
            logger.add(
                sys.stderr,
                level='DEBUG',
                format="<green>{time}</green> | <level>{level}</level> | "
                "<cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>")

            # 文件日志
            log_path = self.get_conf_value('main|log|path', '../../log/')
            log_level = self.get_conf_value('main|log|level', 'INFO') \
                or 'INFO'
            log_file = os.path.join(log_path, 'pyagent.log')
            logger.add(
                log_file,
                level=log_level,
                rotation=self.get_conf_value('main|log|rotation', '50 MB'),
                retention='10 days',
                compression='zip',
                format="{time} | {level} | {message}",
                enqueue=True
            )
        logger.debug('日志初始化完成')

    def __str__(self):
        """返回配置对象的字符串表示"""
        return str(self.__dict__)
