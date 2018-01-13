#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ..models import User
from ..base.handlers import BaseHandler, ListAPIMixin


class UserListHandler(ListAPIMixin, BaseHandler):
    """用户列表API"""
    model = User


class UserDetailHandler(BaseHandler):
    """用户细节API"""

    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass