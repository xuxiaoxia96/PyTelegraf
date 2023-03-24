# -*- coding:utf-8 -*-
"""
    DsFile.py
    文件收集插件
"""
import os, time, socket, json
from . import InputPlugin
import requests


class DsFile(InputPlugin):
    """文件收集插件"""

    # 模块名称
    name = "dsfile"
    
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
                    "DSLOG_DIR" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Logs/",
                    "DSREPLAYLOG_DIR" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Demos/",
                    "HTTPREPLAYLOG_DIR" : "/data/home/user00/replays/",
                    "DSSTAT_DIR" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Profiling/UnrealStats/",
                    "DSNPROF_DIR" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Profiling/",
                    "DSMEMREPORT_DIR" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/Profiling/MemReports/",
                    "DSGASDEBUGGER_DIR" : "/data/home/user00/panguds/LinuxServer/CodeV/Saved/GASDebugger/",
                    "LBLOG_DIR" : "/data/home/user00/pangusvr/bin/log/",
            }
        
        fileReturn = {}
                
        for dir_name, dir_path in log_map.items():
            Files = sorted(os.listdir(dir_path))
            if Files is None:
                continue
            file_ = []
            try:
                fileQuantity = len(Files)
                for i in Files:
                    try:
                        i = os.path.join(path, i)
                        if not os.path.isdir(i):
                            if os.path.islink(i):
                                fileLinkPath = os.readlink(i)
                                file_.append({
                                    'filename': str(os.path.split(i)[1]),
                                    'fileType':'file'
                                })
                            else:
                                file_.append({
                                    'filename': str(os.path.split(i)[1]),
                                    'fileType':'file'
                                })                     
                            
                    except Exception as e:
                        continue
                    
                
                
                fileReturn = {
                    'path': path,
                    'fileQuantity': fileQuantity,
                    'files': file_,
                    'dir' : dir_name
                }
                
                print(fileReturn)
        
        
                metric = self.metric({
                "fileReturn": fileReturn,
                })
            
                metric = self.metric({
                    "fileReturn": fileReturn,
                })
                
                self.out_queue.put_nowait(metric)

            except:
                pass
            
            
