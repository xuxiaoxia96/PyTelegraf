# -*- coding:utf-8 -*-
"""
    console.py
    数据发布插件 - 输出到控制台
"""
from . import OutputPlugin
from ..libs.metric import Metric
import socket
import requests,json
import time
from loguru import logger
import sys

from xmlrpc.server import SimpleXMLRPCServer
class Console(OutputPlugin):
    """数据发布 - 输出到控制台"""

    name = 'console'

    async def write(self, metric):
        """写入数据"""
        # try:
        #     tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     server_addr = ("9.134.167.143", 4561)
        #     tcp_socket.connect(server_addr)
            
        #     # 字典转换Json
        #     send_data = metric.as_text
        #     logger.debug("encode: {}", send_data.encode('utf-8'))
        #     # print(send_data.encode())
        #     # sys.exit()
        #     # 二进制发送
        #     tcp_socket.send(send_data.encode())
            
        #     tcp_socket.close()
        # except:
        #     logger.debug('无法连接服务器: {}', time.time())


        print('>>>', metric.as_json)
        # print(type(metric.as_json))
        