#! /usr/bin/env python
"""缓存模块

使用redis|memcache|...实现web应用的缓存组件
"""
from .models.base import redis_cli


class BaseCache(object):
    """实现Web缓存组件的API"""
    __slots__ = ['client']
    key = 'cache'   # 为了键名的唯一性，加入一个前缀

    @classmethod
    def get(cls, key, default=None):
        """获取缓存资源"""
        raise NotImplemented

    @classmethod
    def set(cls, key, value, expire=None):
        """设置缓存资源"""
        raise NotImplemented

    @classmethod
    def delete(cls, key):
        """删除缓存资源"""
        raise NotImplemented

    @classmethod
    def exists(cls, key):
        raise NotImplemented

    @classmethod
    def expire(cls, key, seconds):
        """设置缓存过期时间"""
        raise NotImplemented

    @classmethod
    def flush_all(cls):
        """刷新所有缓存"""
        raise NotImplemented


class RedisCache(BaseCache):
    """Redis实现的缓存组件"""
    client = redis_cli

    @classmethod
    def get(cls, key, default=None):
        cache_key = "{0}:{1}".format(cls.key, key)
        value = cls.client.get(cache_key)
        if not value:
            return default
        return value

    @classmethod
    def set(cls, key, value, expire=None):
        cache_key = "{0}:{1}".format(cls.key, key)
        cls.client.set(cache_key, value)
        if expire:
            cls.expire(key, expire)

    @classmethod
    def delete(cls, key):
        cache_key = "{0}:{1}".format(cls.key, key)
        cls.client.delete(cache_key)

    @classmethod
    def exists(cls, key):
        cache_key = "{0}:{1}".format(cls.key, key)
        return cls.client.exists(cache_key)

    @classmethod
    def expire(cls, key, seconds):
        cache_key = "{0}:{1}".format(cls.key, key)
        cls.client.expire(cache_key, seconds)

    @classmethod
    def flush_all(cls):
        keys = cls.client.keys("http*")
        if keys:
            cls.client.delete(*keys)


