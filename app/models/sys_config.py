#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import redis

from config import CommonConfig

redis_cli = redis.StrictRedis(
    host=CommonConfig.REDIS_HOST,
    port=CommonConfig.REDIS_PORT,
    password=CommonConfig.REDIS_PASSWORD
)


class SysConfig(object):
    _prefix = 'sysconfig'
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
        redis_key = "{0}:{1}".format(cls._prefix, key)
        if type:
            if type == bool:
                value = int(value)
            else:
                value = type(value)
        redis_cli.set(redis_key, value)

