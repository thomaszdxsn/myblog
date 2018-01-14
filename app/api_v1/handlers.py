#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ..models import User, Post, Category, Tag
from ..base.handlers import BaseHandler, ListAPIMixin, DetailAPIMixin
from .forms import (UserCreateForm, UserUpdateForm, CategoryForm,
                    PostCreateForm, PostUpdateForm, TagForm)

__all__ = ['UserListHandler', 'UserDetailHandler', 'CategoryListHandler',
           'CategoryDetailHandler', 'TagListHandler', 'TagDetailHandler']
# TODO: 在对User修改时需要权限验证


class UserListHandler(ListAPIMixin, BaseHandler):
    """用户列表API"""
    model = User
    fields = ['id', 'email', 'created_time']
    post_form = UserCreateForm
    unique_field = 'email'


class UserDetailHandler(DetailAPIMixin, BaseHandler):
    """用户细节API"""
    model = User
    fields = ['id', 'email', 'created_time']
    put_form = UserUpdateForm
    unique_field = 'email'


class CategoryListHandler(ListAPIMixin, BaseHandler):
    model = Category
    fields = ['id', 'parent_id', 'parent_id', 'created_time']
    post_form = CategoryForm
    unique_field = 'name'


class CategoryDetailHandler(DetailAPIMixin, BaseHandler):
    model = Category
    fields = ['id', 'parent_id', 'name', 'created_time']
    put_form = CategoryForm
    unique_field = 'name'


class PostListHandler(ListAPIMixin, BaseHandler):
    model = Post
    fields = ['id', 'title', 'status', 'created_time', 'publish_time']
    post_form = PostCreateForm
    unique_field = 'title'

    def post(self, *args, **kwargs):
        """创建post时需要对tags单独作处理"""


class PostDetailHandler(DetailAPIMixin, BaseHandler):
    model = Post
    fields = ['id', 'category_id', 'title', 'content', 'status', 'created_time',
              'slug', 'publish_time', 'modified_time']
    put_form = PostUpdateForm
    unique_field = 'title'

    def put(self, *args, **kwargs):
        """更新post时需要对tags单独作处理"""


class TagListHandler(ListAPIMixin, BaseHandler):
    model = Tag
    fields = ['id', 'name', 'created_time']
    post_form = TagForm
    unique_field = 'name'


class TagDetailHandler(DetailAPIMixin, BaseHandler):
    model = Tag
    fields = ['id', 'name', 'created_time']
    put_form = TagForm
    unique_field = 'name'
