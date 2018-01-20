#! /usr/bin/env python
"""中间件模块

缓存中间件
"""
import types

from app.libs.utils import import_object
from app.models.sys_config import SysConfig
from app.models.stats import SiteStats


class BaseMiddleware(object):
    """实现基础的中间件API"""

    def __init__(self, handler, **kwargs):
        self.handler = handler
        for key, value in kwargs.items():
            setattr(self, key, value)

    def before_request(self):
        """一个请求到达时的钩子函数，

        这个钩子函数将会在`RequestHandler.prepare()`中触发
        """
        raise NotImplemented

    def after_request(self):
        """一个请求处理完毕后(已经返回响应)时的钩子函数

        这个钩子函数将会在`RequestHandler.on_finish()`中触发
        """
        raise NotImplemented


class CacheMiddleware(BaseMiddleware):
    """缓存中间件"""

    def __init__(self, handler, cache,
                 no_get_flush=True):
        """初始化缓存配置

        :param handler: RequestHandler的实例
        :param cache:

            缓存类的引入字符串。

            比如想要`from cache import RedisCache`，等价于字符串"cache.RedisCache".

        :param expire: 缓存的过期时间
        :param no_get_flush:

            一个标识参数，决定是否在非GET方法请求时将缓存清空.

        :param host: 缓存后端的host
        :param port: 缓存后端的port
        :param password: 缓存后端的密码
        """
        self.handler = handler
        self.no_get_flush = no_get_flush
        self.request = handler.request
        self.cache = import_object(cache)

    def before_request(self):
        """在请求刚到达时的缓存策略处理流程

        使用request.uri作为缓存键.

        在请求方法是'GET'的情况下,使用monkey-patch技术来修改response过程.
        """
        redis_key = self.request.uri
        if self.request.method.upper() != 'GET':
            if self.no_get_flush:
                self.cache.delete(redis_key)
        else:
            cache_content = self.cache.get(redis_key, None)
            # 如果有相应的缓存内容则直接使用`.finish()`输出
            # 注意，使用`.finish()`以后这个handler的生命周期就结束了
            # 所以缓存中间件一般应该放在中间件列表的最后位置
            if cache_content is not None:
                if cache_content.startswith('{') \
                        and cache_content.endswith('}'):
                    self.handler.set_header(
                        "Content-Type",
                        "application/json; charset=UTF-8"
                    )
                this = self
                def _get(self, *args, **kwargs):
                    this.handler.finish(cache_content)
                this.handler.get = types.MethodType(_get, this.handler)
            else:
                # 如果没有缓存内容,
                # 我们需要使用monkey-patch来改造`.flush()`方法,
                # 为它加入缓存的功能
                this = self
                # instance-level monkey-patch
                def _flush(self, *args, **kwargs):
                    # 如果是304状态码就不会包含body数据
                    if self._status_code != 304:
                        chunk = b"".join(self._write_buffer)
                        this.cache.set(
                            redis_key, chunk,
                            expire=SysConfig.get(**SysConfig.cache_expire)
                        )
                    super(self.__class__, self).flush(*args, **kwargs)
                this.handler.flush = types.MethodType(_flush, this.handler)


class StatsMiddleware(BaseMiddleware):
    """数据统计中间件"""

    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request

    def before_request(self):
        # 增量UV数据
        SiteStats.incr_uv(self.request.remote_ip)
        # 增量PV数据
        SiteStats.incr_pv()
        # 存储访问者的UA
        SiteStats.save_access_ua(self.request.headers['User-Agent'],
                                 self.request.remote_ip)
        # 存储访问者的IP
        SiteStats.save_access_ip(self.request.remote_ip)


class MiddlewareProcess(object):
    """中间件处理方法"""

    @staticmethod
    def prepare(handler, middleware_dicts):
        """嵌入到`prepare()`的处理流程中"""
        for middleware, kwds in middleware_dicts.items():
            middleware_cls = import_object(middleware)
            middleware_obj = middleware_cls(handler, **kwds)
            if 'cache' in middleware.lower():
                if SysConfig.get(**SysConfig.cache_enable) is False:
                    # 没有开启缓存，跳过缓存中间件
                    middleware_obj.cache.flush_all()
                    continue
            try:
                middleware_obj.before_request()
            except NotImplemented:
                pass

    @staticmethod
    def on_finish(handler, middleware_dicts):
        """嵌入到`on_finish()`的处理流程中"""
        for middleware, kwds in middleware_dicts.items():
            if 'cache' in middleware.lower():
                if SysConfig.get(**SysConfig.cache_enable) is False:
                    # 没有开启缓存，跳过缓存中间件
                    continue
            middleware_cls = import_object(middleware)
            middleware_obj = middleware_cls(handler, **kwds)
            try:
                middleware_obj.after_request()
            except Exception:
                pass

