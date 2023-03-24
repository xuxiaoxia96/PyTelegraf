# -*- coding:utf-8 -*-
from loguru import logger

from . import AggsPlugin
from ..libs.metric import Metric


class Process(AggsPlugin):

    name = 'process'

    async def alarm(self, metric):
        """报警"""
        logger.debug('进程列表: {}', metric.as_json)

        self.out_queue.put_nowait(metric)

        return metric
