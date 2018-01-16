#! /usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import types

from tornado.web import RequestHandler


def login_required(handler):
    """为RequestHandler加入一个身份验证，要求这个端点必须登录才允许访问"""
    if not issubclass(handler, RequestHandler):
        raise TypeError("must decorate RequestHandler")

    @functools.wraps
    def wrapper(*args, **kwargs):
        def prepare(self):
            if not self.current_user:
                return self.write_error(401)
            super().prepare()
        handler.prepare = types.MethodType(prepare, handler)
        instance = handler(*args, **kwargs)
        return instance
    return wrapper