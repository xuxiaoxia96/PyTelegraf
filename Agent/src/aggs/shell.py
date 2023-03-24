# -*- coding:utf-8 -*-
from loguru import logger

from . import AggsPlugin
from ..libs.metric import Metric


class Shell(AggsPlugin):

    name = 'shell'

    async def alarm(self, metric):
        """报警"""
        print(">>>>>>>" + metric.as_json) 
        logger.debug('shell: {}', metric.as_json)

        self.out_queue.put_nowait(metric)

        return metric
