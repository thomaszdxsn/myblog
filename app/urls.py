#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .base import handlers as base_handler
from .api_v1 import handlers as apiv1_handler

urlpatterns = [
    # 首页
    ('/', base_handler.HomePageHandler,
     {}, "homepage"),

    # API -- version1

    # 用户API
    (r'/api/v1/user', apiv1_handler.UserListHandler,
     {}, "api:v1:user:list"),
    (r'/api/v1/user/(?P<id>\d+)', apiv1_handler.UserDetailHandler,
     {}, "api:v1:user:detail"),

    # 角色API

]