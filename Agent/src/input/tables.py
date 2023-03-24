# -*- coding:utf-8 -*-
"""
    tables.py
    tables配置文件收集插件
"""
import os, time, socket, json
from . import InputPlugin
import requests


class Tables(InputPlugin):
    """配置文件收集插件"""

    # 模块名称
    name = "tables"
    
    def getFileSize(self, filePath):
        filesizes = ''
        filesizeK = os.stat(filePath).st_size/1024
        if filesizeK>1024:
            filesizeM = filesizeK/1024
            if filesizeM>1024:
                filesizeG = str(round(filesizeM/1024,2))
                filesizes = filesizeG + 'G'
            else:
                filesizes = str(round(filesizeM,2)) + 'M'
        else:
            filesizes = str(round(filesizeK,2)) + 'K'
        return filesizes

    async def gather(self):
        """文件收集"""
        # 6个文件目录
        path = []
        
        file_id = 0
        path = '/data/home/user00/shaoshenxu/vgserver_proj/trunk/bin/tables/'
        Files = sorted(os.listdir(path))
        file_ = []
        try:
            fileQuantity = len(Files)
            for i in Files:
                try:
                    file_id = file_id + 1
                    i = os.path.join(path, i)
                    if not os.path.isdir(i):
                        file_.append({
                                'filename': str(os.path.split(i)[1]),
                                'fileType':'file',
                                'fileModifyTime': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(i).st_mtime)),
                                'fileSize': self.getFileSize(i),
                                'fileId': file_id,
                        })                     
                        
                except Exception as e:
                    continue
            
            fileReturn = {
                'path': path,
                'fileQuantity': fileQuantity,
                'files': file_,
            }
                        
            metric = self.metric({
                "fileReturn": fileReturn,
            })
            
            print(metric.as_json)
            
            self.out_queue.put_nowait(metric)

        except:
            pass
            
            
