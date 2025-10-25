# -*- coding:utf-8 -*-
"""
    app.py
    主文件
"""
from asyncio import Queue, create_task, sleep
from typing import Callable, Optional

from loguru import logger

from .conf.settings import CONF
import sys

class Worker:
    """
    插件工作单元
    以插件为单位进行协程的调度
    """

    def __init__(self, name: str):
        # 插件名称
        self.name = name
        # 数据通道
        self.q_input = Queue()
        self.q_aggs = Queue()
        # 任务集合，用于跟踪创建的协程任务
        self.tasks = set()

    async def run(self, cls_input: Callable):
        """启动插件"""
        try:
            logger.info(f'启动插件工作单元: {self.name}')
            
            # 数据收集，启动协程任务，加入事件循环中
            task = create_task(cls_input(self._conf, None, self.q_input).run())
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)

            # 汇聚/报警
            self.create_tasks('aggs', self.q_input, self.q_aggs)

            # 数据输出
            self.create_tasks('output', self.q_aggs, None)
            
        except Exception as e:
            logger.error(f'插件工作单元启动失败: {self.name}, 错误: {str(e)}')

    def create_tasks(self, module: str, in_queue: Queue, out_queue: Optional[Queue]):
        """启动插件"""
        try:
            current_queue = in_queue
            
            # 启动系统配置的公共插件, 比如多个公共输出插件
            for cls_name in self._conf.get_conf_value(f'main|common_{module}', []):
                cls = self._conf.get_plugin_obj(module, cls_name)
                if cls:
                    out_queue_next = Queue()
                    cls_obj = cls(self._conf, current_queue, out_queue_next)
                    cls_obj.alias = self.name
                    task = create_task(cls_obj.run())
                    self.tasks.add(task)
                    task.add_done_callback(self.tasks.discard)
                    current_queue = out_queue_next

            # 启动插件本身
            cls = self._conf.get_plugin_obj(module, self.name)
            if cls:
                cls_obj = cls(self._conf, current_queue, out_queue)
                cls_obj.alias = self.name
                coro = cls_obj.run()
            else:
                # 克隆 default 插件
                default_cls = self._conf.get_plugin_obj(module, 'default')
                if default_cls:
                    cls_obj = default_cls(self._conf, current_queue, out_queue)
                    cls_obj.alias = self.name
                    coro = cls_obj.run()
                else:
                    logger.warning(f'插件 {module}.{self.name} 和默认插件都不存在')
                    return

            task = create_task(coro)
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)
            
        except Exception as e:
            logger.error(f'创建{module}模块任务失败: {self.name}, 错误: {str(e)}')
            
    @property
    def _conf(self):
        """获取配置实例"""
        return CONF

async def main():
    """程序入口"""
    logger.info('Agent 开始工作')

    try:
        while True:
            # 热更配置
            await CONF.update()
            
            # 重载配置
            CONF.reload()
            
            # 启动插件
            await start_plugins()
            
            # 等待下次热更
            logger.debug(f'等待下次配置热更，间隔 {CONF.reload_sec} 秒')
            await sleep(CONF.reload_sec)
            
    except KeyboardInterrupt:
        logger.info('接收到中断信号，Agent 正在停止')
    except Exception as e:
        logger.error(f'Agent 运行出错: {str(e)}')
    finally:
        logger.info('Agent 已停止')


async def start_plugins():
    """
    启动插件
    开启的插件 - 工作中插件
    """
    try:
        # 计算需要启动的插件（开启但未工作的）
        plugins_to_start = CONF.plugins_open - CONF.plugins_working
        
        if not plugins_to_start:
            logger.debug('没有新的插件需要启动')
            return
            
        logger.info(f'准备启动 {len(plugins_to_start)} 个插件')
        
        for name in plugins_to_start:
            # 获取插件对象，数据采集插件
            cls_input = CONF.get_plugin_obj('input', name)
            if not cls_input:
                logger.error(f'插件 {name} 不存在')
                continue

            # create_task创建协程任务，加入事件循环，启动插件
            create_task(Worker(name).run(cls_input))
            CONF.plugins_working.add(name)
            logger.info(f'插件 {name} 开始工作')

        if not CONF.plugins_working:
            logger.warning('没有插件在工作')
            
    except Exception as e:
        logger.error(f'启动插件失败: {str(e)}')
