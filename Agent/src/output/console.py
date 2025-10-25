# -*- coding:utf-8 -*-
"""
    console.py
    数据发布插件 - 输出到控制台
"""
import socket
import time
from loguru import logger

from . import OutputPlugin
from ..libs.metric import Metric


class Console(OutputPlugin):
    """数据发布 - 输出到控制台"""

    name = 'console'

    def __init__(self, conf, in_queue, out_queue):
        super().__init__(conf, in_queue, out_queue)
        # TCP发送配置
        self.tcp_enabled = self.get_plugin_conf_value('tcp_enabled', False)
        self.tcp_server = self.get_plugin_conf_value('tcp_server', '9.134.167.143')
        self.tcp_port = self.get_plugin_conf_value('tcp_port', 4561)
        self.tcp_timeout = self.get_plugin_conf_value('tcp_timeout', 5)
        
        logger.debug(f'控制台插件初始化: TCP发送={self.tcp_enabled}, 服务器={self.tcp_server}:{self.tcp_port}')

    async def write(self, metric: Metric):
        """写入数据"""
        try:
            # 始终输出到控制台
            print('>>>', metric.as_json)
            
            # 如果启用了TCP发送
            if self.tcp_enabled and not metric.is_closed:
                await self._send_via_tcp(metric)
                
        except Exception as e:
            logger.error(f'控制台插件处理数据失败: {str(e)}')
    
    async def _send_via_tcp(self, metric: Metric):
        """通过TCP发送数据"""
        tcp_socket = None
        try:
            # 创建TCP连接
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(self.tcp_timeout)
            tcp_socket.connect((self.tcp_server, self.tcp_port))
            
            # 转换数据格式并发送
            send_data = metric.as_text
            tcp_socket.send(send_data.encode('utf-8'))
            logger.debug(f'TCP数据发送成功: {len(send_data)} 字节')
            
        except socket.timeout:
            logger.warning(f'TCP发送超时: {self.tcp_server}:{self.tcp_port}')
        except ConnectionRefusedError:
            logger.warning(f'TCP连接被拒绝: {self.tcp_server}:{self.tcp_port}')
        except Exception as e:
            logger.error(f'TCP发送失败: {str(e)}')
        finally:
            # 确保关闭连接
            if tcp_socket:
                try:
                    tcp_socket.close()
                except:
                    pass
        