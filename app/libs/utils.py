#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime


def import_object(name):
    """通过name这个字符串来import一个对象

    import_object("x")等同于"import x"
    import_object("x.y.z")等同于"from x.y import z"
    >>> import tornado.escape
    >>> import_object('tornado.escape') is tornado.escape
    True
    >>> import_object('tornado.escape.utf8') is tornado.escape.utf8
    True
    >>> import_object('tornado') is tornado
    True
    >>> import_object('tornado.missing_module')
    Traceback (most recent call last):
        ...
    ImportError: No module named missing_module
    """
    if not isinstance(name, str):
        name = name.encode('utf-8')
    if name.count('.') == 0:
        return __import__(name, None, None)

    parts = name.split(".")
    obj = __import__(".".join(parts[:-1]), None, None, [parts[-1]], 0)
    try:
        return getattr(obj, parts[-1])
    except AttributeError:
        raise ImportError("No module named %s" % parts[-1])


class DateEncoder(json.JSONEncoder):
    """json的一个解码handler，遇到时间对象时将它自动格式化为字符串"""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return super().default(obj)


def aggregate_errors(errors):
    """将错误信息(字典)转换为字符串"""
    error_string = ''
    for key, value in errors.items():
        error_string += "{0} ".format(",".join(value))
    return error_string