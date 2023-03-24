# -*- coding:utf-8 -*-
"""
    LogFile.py
    文件收集插件
"""
import os, time, socket, json
from . import InputPlugin
import requests


class LogFile(InputPlugin):
    """文件收集插件"""

    # 模块名称
    name = "logfile"
    
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
        log_map = {
                    "dslog" : "/data/home/user00/log/panguds/",
                    # "dsreplaylog" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Demos/",
                    # "httpreplaylog" : "/data/home/user00/replays/",
                    # "dsstats" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Profiling/UnrealStats/",
                    # "dsnprof" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Profiling/",
                    # "dsmemreport" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Profiling/MemReports/",
                    # "dsgasdebugger" : "/data/home/user00/log/GASDebugger/",
                    # "lblog" : "/data/home/user00/pangusvr/bin/log/",
            }
        
        metric = self.metric()

                        
        for dir_name, dir_path in log_map.items():
            Files = sorted(os.listdir(dir_path))
            if Files is None:
                continue
            file_ = []
            print(Files)
            try:
                fileQuantity = len(Files)
                for i in Files:
                    try:
                        i = os.path.join(dir_path, i)
                        if not os.path.isdir(i):
                            file_.append({
                                'filename': str(os.path.split(i)[1]),
                                'fileType':'file'
                            })                     
                            
                    except Exception as e:
                        continue
                
                fileReturn = {
                    'path': dir_path,
                    'fileQuantity': fileQuantity,
                    'files': file_,
                    'dir' : dir_name,
                }
                
                print(fileReturn)
                
                metric.add(dir_name, fileReturn)
            except:
                pass
            
        self.out_queue.put_nowait(metric)

            
            
