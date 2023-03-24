# -*- coding:utf-8 -*-
from loguru import logger

from . import AggsPlugin
from ..libs.metric import Metric
from yaml import safe_load, safe_dump


class Demo(AggsPlugin):

    name = 'demo'
    
    def remove_plugin(self):
        with open('/data/home/user00/shaoshenxu/toolsdev/Agent/agent_dev/etc/main.yaml', 'r', encoding='utf-8') as f:
            conf = safe_load(f)
            cfg = conf if isinstance(conf, dict) else {}
            print(cfg['open'])
            try:
                cfg['open'].remove(self.name)
            except:
                pass
            print(cfg)
            
        with open('/data/home/user00/shaoshenxu/toolsdev/Agent/agent_dev/etc/main.yaml', 'w', encoding='utf-8') as f:
            print(cfg)
            safe_dump(cfg, f)            
            

    async def alarm(self, metric: Metric) -> Metric:
        """报警"""
        # print(metric.as_json)
        # if metric.get('random', 0) >= self.get_plugin_conf_value('alarm|limit', 0):
        #     return metric
        
        logger.debug('触发报警: {}', metric.as_json)
        
        self.remove_plugin()

        # 附加报警数据
        metric = metric.clone()
        metric.set(type='alarm~~~~~~~~~')
        metric.set(**{'a': True, 'b': 123})
        self.out_queue.put_nowait(metric)
        logger.debug('触发报警了: {}', metric.as_json)

        # 新生成报警数据
        # self.put_alarm_metric('示例报警数据', more='报警附加消息')

        return metric
