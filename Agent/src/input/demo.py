# -*- coding:utf-8 -*-
"""
    demo.py
    示例数据收集插件
"""
from random import randint, random

from . import InputPlugin


class Demo(InputPlugin):
    """示例数据收集插件"""

    # 模块名称
    name = 'demo'

    async def gather(self):
        """获取数据"""
        metric = self.metric({
            'random': randint(6, 30),
            'test': 'test'
        })
        
        self.out_queue.put_nowait(metric)
