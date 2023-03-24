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

    ## Callable 作为函数参数使用，其实只是做一个类型检查的作用，检查传入的参数值 get_func 是否为可调用对象
    async def run(self, cls_input: Callable):
        """启动插件"""
        # 数据收集，启动协程任务，加入事件循环中
        create_task(cls_input(CONF, None, self.q_input).run())

        # 汇聚/报警
        self.create_tasks('aggs', self.q_input, self.q_aggs)

        # 数据输出
        self.create_tasks('output', self.q_aggs, None)

    def create_tasks(self, module: str, in_queue: Queue, out_queue: Optional[Queue]):
        """启动插件"""
        # 启动系统配置的公共插件, 比如多个公共输出插件
        for cls_name in CONF.get_conf_value(f'main|common_{module}', []):
            cls = CONF.get_plugin_obj(module, cls_name)
            if cls:
                out_queue_next = Queue()
                cls_obj = cls(CONF, in_queue, out_queue_next)
                cls_obj.alias = self.name
                create_task(cls_obj.run())
                in_queue = out_queue_next

        # 启动插件本身
        cls = CONF.get_plugin_obj(module, self.name)
        if cls:
            cls_obj = cls(CONF, in_queue, out_queue)
            cls_obj.alias = self.name
            coro = cls_obj.run()
        else:
            # 克隆 default 插件
            cls_obj = CONF.get_plugin_obj(module, 'default')(CONF, in_queue, out_queue)
            cls_obj.alias = self.name
            coro = cls_obj.run()

        create_task(coro)

async def main():
    """程序入口"""
    logger.info('Agent start working')

    while True:
        # 热更
        await CONF.update()
        # # 重载配置
        CONF.reload()
        # 启动插件
        await start_plugins()
        # 热更时间
        await sleep(CONF.reload_sec)


async def start_plugins():
    """
    启动插件
    开启的插件 - 工作中插件
    """
    plugins = CONF.plugins_open - CONF.plugins_working
    for name in plugins:
        # 获取插件对象，数据采集插件
        cls_input = CONF.get_plugin_obj('input', name)
        if not cls_input:
            logger.error(f'Plugin {name} does not exist')
            continue

        # create_task创建协程任务，加入事件循环，启动插件
        create_task(Worker(name).run(cls_input))
        CONF.plugins_working.add(name)
        logger.info(f'Plugin {name} start working')

    CONF.plugins_working or logger.warning('No plugins are working')
