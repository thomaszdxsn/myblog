#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""基础Handler模块
包括Handler基类`BaseHandler`的定义，以及首页handler等通用页面的handler定义
"""

from tornado import web, gen

from ..middlewares import MiddlewareProcess


class BaseHandler(web.RequestHandler):
    """Handler的基类"""

    def prepare(self):
        # web中间件的prepare处理
        self._middleware_list = self.config.MIDDLEWARES
        MiddlewareProcess.prepare(self, self._middleware_list)

    def on_finish(self):
        # web中间件的on_finish处理
        MiddlewareProcess.on_finish(self, self._middleware_list)

    @property
    def config(self):
        return self.application.settings['config']


class HomePageHandler(BaseHandler):
    """首页handler"""

    async def get(self, *args, **kwargs):
        # await gen.sleep(1)
        self.write("hello world")

    def post(self):
        pass