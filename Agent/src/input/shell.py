# -*- coding:utf-8 -*-
"""
    shell.py
    脚本收集插件
"""
import os, time, socket, json, sys
from . import InputPlugin
import requests
import subprocess


class Shell(InputPlugin):
    """脚本插件"""

    # 模块名称
    name = "shell"

    async def gather(self):
        
        script = "sh /data/home/user00/shaoshenxu/toolsdev/Agent/agent_dev/scripts/hello.sh"
        err = 0
        try:
            ret = subprocess.check_output(script, stderr=subprocess.STDOUT, shell=True)
        except:
            ret = 0
            err = 1
            
        print(str(ret))
        print(type(str(ret)))
        
        metric = self.metric({
            "ret": ret,
            "err": err
        })
        
        print(metric.as_text)
        
        self.out_queue.put_nowait(metric)
