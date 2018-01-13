#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ..models import User
from ..base.handlers import BaseHandler, ListAPIMixin
from .forms import UserCreateForm


class UserListHandler(ListAPIMixin, BaseHandler):
    """用户列表API"""
    model = User
    fields = ['id', 'email', 'created_time']
    post_form = UserCreateForm


class UserDetailHandler(BaseHandler):
    """用户细节API"""

    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass