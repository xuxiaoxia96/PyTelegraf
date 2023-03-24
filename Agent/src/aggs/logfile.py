# -*- coding:utf-8 -*-
from loguru import logger

from . import AggsPlugin
from ..libs.metric import Metric


class LogFile(AggsPlugin):

    name = 'logfile'

    async def alarm(self, metric):
        """报警"""
        print(">>>>>>>" + metric.as_json) 
        logger.debug('DS日志文件: {}', metric.as_json)

        self.out_queue.put_nowait(metric)

        return metric
