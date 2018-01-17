#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .api_v1 import handlers as api_v1_handlers
from .admin import handlers as admin_handlers
from .blog import handlers as blog_handlers

urlpatterns = [
    # 博客页面
    
    # 首页
    (r"/", blog_handlers.HomepageHandler,
     {}, "homepage"),
    

    # 后台页面

    # 后台登入/登出页面
    (r'/fake-admin/login', admin_handlers.AdminLoginHandler,
     {}, "admin:login"),
    (r'/fake-admin/logout', admin_handlers.AdminLogoutHandler,
     {}, "admin:logout"),

    # 后台文章分类管理
    (r"/fake-admin/category",
     admin_handlers.CategoryListHandler,
     {}, "admin:category:list"),
    (r"/fake-admin/category/(?P<id>\d+)",
     admin_handlers.CategoryDetailHandler,
     {}, "admin:category:detail"),
    (r"/fake-admin/category/create",
     admin_handlers.CategoryCreateHandler,
     {}, "admin:category:create"),

    # 后台文章管理
    (r"/fake-admin/post", admin_handlers.PostListHandler,
     {}, "admin:post:list"),
    (r"/fake-admin/post/(?P<id>\d+)",
     admin_handlers.PostDetailHandler,
     {}, "admin:post:detail"),
    (r"/fake-admin/post/create",
     admin_handlers.PostCreateHandler,
     {}, "admin:post:create"),

    # 后台图片管理
    (r"/fake-admin/image", admin_handlers.ImageListHandler,
     {}, "admin:image:list"),
    (r"/fake-admin/image/(?P<id>\d+)", admin_handlers.ImageDetailHandler,
     {}, "admin:image:detail"),
    (r"/fake-admin/image/create", admin_handlers.ImageCreateHandler,
     {}, "admin:image:create"),

    # 后台系统配置
    (r"/fake-admin/sys-config", admin_handlers.SysConfigHandler,
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