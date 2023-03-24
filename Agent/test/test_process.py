import psutil
import sys

ps = ['SFTP-SERVER', 'LOGIN', 'NM-DISPATCHER', 'IRQBALANCE', 'QMGR', 'WPA_SUPPLICANT', 
'LVMETAD', 'AUDITD', 'MASTER', 'DBUS-DAEMON', 'TAPDISK', 'SSHD', 'INIT', 'KSOFTIRQD', 
'KWORKER', 'KMPATHD', 'KMPATH_HANDLERD', 'PYTHON', 'KDMFLUSH', 'BIOSET', 'CROND', 'KTHREADD', 
'MIGRATION', 'RCU_SCHED', 'KJOURNALD', 'IPTABLES', 'SYSTEMD', 'NETWORK', 'DHCLIENT', 
'SYSTEMD-JOURNALD', 'NETWORKMANAGER', 'SYSTEMD-LOGIND', 'SYSTEMD-UDEVD', 'POLKITD', 'TUNED', 'RSYSLOGD',
'BASH','YDSERVICE','SYSTEMD']


Pids = psutil.pids()
processList = []
for pid in Pids:
    try:
        tmp = {}
        p = psutil.Process(pid)
        # print(p)        
        tmp['name'] = p.name()                             #进程名称
        if tmp['name'].upper() in ps:
            continue
        
        tmp['pid'] = pid
        tmp['memory_percent'] = str(round(p.memory_percent(),3))+'%' #进程占用的内存比例
        processList.append(tmp)
        print(processList)
        del(p)
        del(tmp)
    except:
        continue
processList = sorted(processList, key=lambda x : x['memory_percent'], reverse=True)

print(processList)    