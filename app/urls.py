#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .base import handlers as base_handler
from .api_v1 import handlers as api_v1_handler

urlpatterns = [
    # 首页
    ('/', base_handler.HomePageHandler,
     {}, "homepage"),

    # API -- version1.0

    # 用户API
    (r'/api/v1/user', api_v1_handler.UserListHandler,
     {}, "api:v1:user:list"),
    (r'/api/v1/user/(?P<id>\d+)', api_v1_handler.UserDetailHandler,
     {}, "api:v1:user:detail"),

    # 分类API
    (r'/api/v1/category', api_v1_handler.CategoryListHandler,
     {}, 'api:v1:category:list'),
    (r'/api/v1/category/(?P<id>\d+)', api_v1_handler.CategoryDetailHandler,
     {}, "api:v1:category:detail"),

    # 标签(tag)API
    (r'/api/v1/tag', api_v1_handler.TagListHandler,
     {}, "api:v1:tag:list"),
    (r"/api/v1/tag/(?P<id>\d+)", api_v1_handler.TagDetailHandler,
     {}, "api:v1:tag:detail"),
]