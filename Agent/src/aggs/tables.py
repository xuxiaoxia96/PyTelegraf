# -*- coding:utf-8 -*-
from loguru import logger

from . import AggsPlugin
from ..libs.metric import Metric


class Tables(AggsPlugin):

    name = 'tables'

    async def alarm(self, metric):
        """报警"""
        logger.debug('tables文件: {}', metric.as_json)

        self.out_queue.put_nowait(metric)

        return metric
