#! /usr/bin/env python
"""缓存模块

使用redis|memcache|...实现web应用的缓存组件
"""
import redis


class BaseCache(object):
    """实现Web缓存组件的API"""
    __slots__ = ['client']
    key = 'cache'   # 为了键名的唯一性，加入一个前缀

    def get(self, key, default=None):
        """获取缓存资源"""
        raise NotImplemented

    def set(self, key, value, expire=None):
        """设置缓存资源"""
        raise NotImplemented

    def delete(self, key):
        """删除缓存资源"""
        raise NotImplemented

    def exists(self, key):
        raise NotImplemented

    def expire(self, key, seconds):
        """设置缓存过期时间"""
        raise NotImplemented


class RedisCache(BaseCache):
    """Redis实现的缓存组件"""
    # TODO: 可使用元类来生成client，而不用每次都实例化这个类

    def __init__(self, host="localhost", port=6379, password=None):
        self.client = redis.StrictRedis(host, port,
                                        password=password,
                                        decode_responses=True)

    def get(self, key, default=None):               # TODO: 删除debugging信息
        cache_key = "{0}:{1}".format(self.key, key)
        value = self.client.get(cache_key)
        print("cache get key{} content:{}".format(key, value))
        if not value:
            return default
        return value

    def set(self, key, value, expire=None):
        print("cache set key{} content:{}".format(key, value))
        cache_key = "{0}:{1}".format(self.key, key)
        self.client.set(cache_key, value)
        if expire:
            self.expire(key, expire)

    def delete(self, key):
        cache_key = "{0}:{1}".format(self.key, key)
        self.client.delete(cache_key)

    def exists(self, key):
        cache_key = "{0}:{1}".format(self.key, key)
        print("cache exists key{} {}".format(key, self.client.exists(cache_key)))
        return self.client.exists(cache_key)

    def expire(self, key, seconds):
        cache_key = "{0}:{1}".format(self.key, key)
        self.client.expire(cache_key, seconds)



