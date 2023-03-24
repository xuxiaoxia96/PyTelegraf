# -*- coding:utf-8 -*-
"""
    psutil.py
"""


def to_dict(obj):
    """对象转字典"""
    if hasattr(obj, '_asdict'):
        return obj._asdict()

    if hasattr(obj, '_fields'):
        return dict(zip(obj._fields, obj))

    try:
        return dict(obj)
    except BaseException:
        pass

    return {}
