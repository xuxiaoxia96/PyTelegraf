# -*- coding:utf-8 -*-
"""
    plugins.py
    插件集注册
"""
# from ..common import converter, discard
from ..input import demo as input_demo , logfile as input_logfile, mem as input_mem, shell as input_shell, process as input_process, tables as input_tables
from ..aggs import demo as aggs_demo, logfile as aggs_logfile, mem as aggs_mem, shell as aggs_shell, process as aggs_process, tables as aggs_tables
from ..output import default as output_default

PLUGINS = {
    'common': {
        # 'converter': converter.Converter,
        # 'discard': discard.Discard,
    },
    'input': {
        'demo': input_demo.Demo,
        'logfile': input_logfile.LogFile,
        'mem': input_mem.Mem,
        'process': input_process.Process,
        'tables': input_tables.Tables,
    },
    'aggs': {
        'demo': aggs_demo.Demo,
        'logfile': aggs_logfile.LogFile,
        'mem': aggs_mem.Mem,
        'process': aggs_process.Process,
        'tables': aggs_tables.Tables,
    },
    'output': {
        'default': output_default.Default,
        # 'console': output_console.Console,
        # 'tcp': output_tcp.Tcp
    }
}
