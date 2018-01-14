#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ..models import User, Post, Category, Tag, Image, Comment
from ..base.handlers import BaseHandler, ListAPIMixin, DetailAPIMixin
from .forms import (UserCreateForm, UserUpdateForm, CategoryForm,
                    PostCreateForm, PostUpdateForm, TagForm,
                    ImageCreateForm, CommentCreateForm, CommentUpdateForm)

__all__ = ['UserListHandler', 'UserDetailHandler', 'CategoryListHandler',
           'CategoryDetailHandler', 'TagListHandler', 'TagDetailHandler']
# TODO: 在对User修改时需要权限验证


class UserListHandler(ListAPIMixin, BaseHandler):
    """用户列表API"""
    model = User
    post_form = UserCreateForm
    unique_field = 'email'


class UserDetailHandler(DetailAPIMixin, BaseHandler):
    """用户细节API"""
    model = User
    put_form = UserUpdateForm
    unique_field = 'email'


class CategoryListHandler(ListAPIMixin, BaseHandler):
    model = Category
    post_form = CategoryForm
    unique_field = 'name'


class CategoryDetailHandler(DetailAPIMixin, BaseHandler):
    model = Category
    put_form = CategoryForm
    unique_field = 'name'


class PostListHandler(ListAPIMixin, BaseHandler):
    model = Post
    post_form = PostCreateForm
    unique_field = 'title'


class PostDetailHandler(DetailAPIMixin, BaseHandler):
    model = Post
    put_form = PostUpdateForm
    unique_field = 'title'


class CommentListHandler(ListAPIMixin, BaseHandler):
    model = Comment
    post_form = CommentCreateForm


class CommentDetailHandler(DetailAPIMixin, BaseHandler):
    model = Comment
    put_form = CommentUpdateForm


class TagListHandler(ListAPIMixin, BaseHandler):
    model = Tag
    post_form = TagForm
    unique_field = 'name'


class TagDetailHandler(DetailAPIMixin, BaseHandler):
    model = Tag
    put_form = TagForm
    unique_field = 'name'


# TODO: 稍后实验如何使用Vue+Axious来上传
class ImageListHandler(ListAPIMixin, BaseHandler):
    model = Image
    post_form = ImageCreateForm

    def post(self, *args, **kwargs):
        print(self.request.files)
        form = self.post_form(self.request.body)
        print(form.data)


class ImageDetailHandler(DetailAPIMixin, BaseHandler):
    model = Image


