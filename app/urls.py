#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .base import handlers as base_handlers
from .api_v1 import handlers as api_v1_handlers
from .admin import handlers as admin_handers

urlpatterns = [
    # 首页
    (r'/', base_handlers.HomePageHandler,
     {}, "homepage"),

    # 后台页面
    
    # 后台登入/登出页面
    (r'/fake-admin/login', admin_handers.AdminLoginHandler,
     {}, "admin:login"),
    (r'/fake-admin/logout', admin_handers.AdminLogoutHandler,
     {}, "admin:logout"),

    # 后台文章分类管理
    (r"/fake-admin/category",
     admin_handers.CategoryListHandler,
     {}, "admin:category:list"),
    (r"/fake-admin/category/(?P<id>\d+)",
     admin_handers.CategoryDetailHandler,
     {}, "admin:category:detail"),
    (r"/fake-admin/category/create",
     admin_handers.CategoryCreateHandler,
     {}, "admin:category:create"),


    # 后台文章管理
    (r"/fake-admin/post", admin_handers.PostListHandler,
     {}, "admin:post:list"),
    (r"/fake-admin/post/(?P<id>\d+)",
     admin_handers.PostDetailHandler,
     {}, "admin:post:detail"),
    (r"/fake-admin/post/create",
     admin_handers.PostCreateHandler,
     {}, "admin:post:create"),

    # 后台系统配置
    (r"/fake-admin/sys-config", admin_handers.SysConfigHandler,
     {}, "admin:sys-config"),


    # API -- version1.0

    # 用户API
    (r'/api/v1/user', api_v1_handlers.UserListHandler,
     {}, "api:v1:user:list"),
    (r'/api/v1/user/(?P<id>\d+)', api_v1_handlers.UserDetailHandler,
     {}, "api:v1:user:detail"),
    # sessionid API
    (r"/api/v1/user/session-id", api_v1_handlers.SessionIDHandler,
     {}, "api:v1:user:session_id"),

    # 分类API
    (r'/api/v1/category', api_v1_handlers.CategoryListHandler,
     {}, 'api:v1:category:list'),
    (r'/api/v1/category/(?P<id>\d+)', api_v1_handlers.CategoryDetailHandler,
     {}, "api:v1:category:detail"),

    # 文章(post)API
    (r"/api/v1/post", api_v1_handlers.PostListHandler,
     {}, "api:v1:post:list"),
    (r"/api/v1/post/(?P<id>\d+)", api_v1_handlers.PostDetailHandler,
     {}, "api:v1:post:detail"),

    # 评论API
    (r"/api/v1/comment", api_v1_handlers.CommentListHandler,
     {}, "api:v1:comment:list"),
    (r"/api/v1/comment/(?P<id>\d+)", api_v1_handlers.CommentDetailHandler,
     {}, "api:v1:comment:detail"),

    # 标签(tag)API
    (r'/api/v1/tag', api_v1_handlers.TagListHandler,
     {}, "api:v1:tag:list"),
    (r"/api/v1/tag/(?P<id>\d+)", api_v1_handlers.TagDetailHandler,
     {}, "api:v1:tag:detail"),

    # 图片API
    (r'/api/v1/image', api_v1_handlers.ImageListHandler,
     {}, "api:v1:image:list"),
    (r"/api/v1/image/(?P<id>\d+)", api_v1_handlers.ImageDetailHandler,
     {}, "api:v1:image:detail"),
]