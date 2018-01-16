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
    expire_time = {
        'key': 'expire_time',
        'default': 60 * 60 * 1
    }
    per_page = {
        'key': 'per_page',
        'default': 100
    }

    @classmethod
    def get(cls, key, default=None):
        redis_key = "{0}:{1}".format(cls._prefix, key)
        value = redis_cli.get(redis_key)
        if not value:
            return default
        return value

    @classmethod
    def set(cls, key, value):
        redis_key = "{0}:{1}".format(cls._prefix, key)
        redis_cli.set(redis_key, value)

