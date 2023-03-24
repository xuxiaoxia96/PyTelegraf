# -*- coding:utf-8 -*-
import os, sys


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
        
for dir_name, dir_path in log_map.items():
    print(dir_name)