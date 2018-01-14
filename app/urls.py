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

    # 文章(post)API
    (r"/api/v1/post", api_v1_handler.PostListHandler,
     {}, "api:v1:post:list"),
    (r"/api/v1/post/(?P<id>\d+)", api_v1_handler.PostDetailHandler,
     {}, "api:v1:post:detail"),

    # 评论API
    (r"/api/v1/comment", api_v1_handler.CommentListHandler,
     {}, "api:v1:comment:list"),
    (r"/api/v1/comment/(?P<id>\d+)", api_v1_handler.CommentDetailHandler,
     {}, "api:v1:comment:detail"),

    # 标签(tag)API
    (r'/api/v1/tag', api_v1_handler.TagListHandler,
     {}, "api:v1:tag:list"),
    (r"/api/v1/tag/(?P<id>\d+)", api_v1_handler.TagDetailHandler,
     {}, "api:v1:tag:detail"),

    # 图片API
    (r'/api/v1/image', api_v1_handler.ImageListHandler,
     {}, "api:v1:image:list"),
    (r"/api/v1/image/(?P<id>\d+)", api_v1_handler.ImageDetailHandler,
     {}, "api:v1:image:detail"),
]