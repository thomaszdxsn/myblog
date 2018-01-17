#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from .base import redis_cli


class SysConfig(object):
    _prefix = '_sysconfig'
    session_expire = {
        'key': 'expire_time',
        'default': 60 * 60 * 1,
        'type': int,
        'desc': "session过期时间"
    }
    per_page = {
        'key': 'per_page',
        'default': 100,
        'type': int,
        "desc": "每页显示的条目数量"
    }
    cache_enable = {
        'key': 'cache_enable',
        'default': False,
        'type': bool,
        'desc': "是否开启缓存"
    }
    cache_expire = {
        'key': 'cache_expire',
        'default': 60 * 60 * 1,
        'type': int,
        "desc": "缓存过期的时间"
    }

    @classmethod
    def get(cls, key, default=None, type=None, **kwargs):
        """获取系统配置

        :param key: 系统配置"键"
        :param default: 当系统配置不存在时使用的默认值
        :param type:
            用于对系统配置值作类型转换的可调用对象,
            如果type==bool，就会先将它转换为整数再转换为布尔值
        :return: 返回最终的系统配置值
        """
        redis_key = "{0}:{1}".format(cls._prefix, key)
        value = redis_cli.get(redis_key)
        if not value:
            return default
        if type:
            if type == bool:
                value = int(value)
            value = type(value)
        return value

    @classmethod
    def set(cls, key, value, type=None, **kwargs):
        """设置系统配置值

        :param key: 系统配置"键"
        :param value: 系统配置"值"
        :param type:
            用于对系统配置值作类型转换的可调用对象,
            如果type==bool，将这个值转换为整数类型
        """
        redis_key = "{0}:{1}".format(cls._prefix, key)
        if type:
            if type == bool:
                value = int(value)
            else:
                value = type(value)
        redis_cli.set(redis_key, value)

