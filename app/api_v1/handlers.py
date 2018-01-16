#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json

from ..models import User, Post, Category, Tag, Image, Comment
from ..base.handlers import BaseHandler, ListAPIMixin, DetailAPIMixin
from .forms import (UserCreateForm, UserUpdateForm, CategoryForm,
                    PostCreateForm, PostUpdateForm, TagForm,
                    ImageCreateForm, CommentCreateForm, CommentUpdateForm,
                    UserLoginForm)

__all__ = ['UserListHandler', 'UserDetailHandler', 'CategoryListHandler',
           'CategoryDetailHandler', 'TagListHandler', 'TagDetailHandler',
           'SessionIDHandler']
# TODO: 加入一些权限的验证


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


class SessionIDHandler(BaseHandler):
    """获取session_id，用户必须登录"""

    def get(self, *args, **kwargs):
        """以登录用户可以直接获取"""
        if not self.current_user:
            return self.write_error(401)
        self.write({
            'session_id': self.session._id
        })

    def post(self, *args, **kwargs):
        """需要用户登录来下发一个新的session_id"""
        # TODO: 加入一些登录次数限制的功能
        try:
            json_data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return self.write_error(400)

        form = UserLoginForm(data=json_data)
        if not form.validate():
            error_msg = {"error": 1}
            error_msg.update(form.errors)
            return self.write(error_msg)

        if User.exists(form.email.data, self.db) is False:
            error_msg = {
                'error': 2,
                'msg': 'email or password error'    # 错误信息不能明确对方该邮箱不存在
            }
            return self.write(error_msg)

        user_obj = self.db.query(User).filter(
            User.email == form.email.data
        ).one()
        if user_obj.verify_password(form.password.data) is False:
            error_msg = {
                'error': 2,
                'msg': 'email or password error'
            }
            return self.write(error_msg)

        # session_id创建成功
        self.session.user_id = user_obj.id
        self.set_status(201)
        self.write({"error": 0})

    def put(self):
        if not self.current_user:
            return self.write_error(401)
        self.session.init_session()
        self.set_status(201)

    def delete(self):
        if not self.current_user:
            return self.write_error(401)
        self.session.logout()
        self.set_status(204)