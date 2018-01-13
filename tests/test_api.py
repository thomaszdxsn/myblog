#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from tornado.testing import AsyncHTTPTestCase

from app.models import *
from app import create_app
from .base import ModelTestMixin

__all__ = ['APIV1TestCase']

# ========================================================
# api_v1 testing =========================================
# ========================================================


class APIV1TestCase(ModelTestMixin, AsyncHTTPTestCase):
    def get_app(self):
        return create_app('test')

    def reverse_url(self, *args, **kwargs):
        return self._app.reverse_url(*args, **kwargs)

    def test_get_user_object_list(self):
        u1 = User(email='user1')
        u2 = User(email='user2')
        self.db.add_all([
            u1, u2
        ])
        self.db.commit()

        response = self.fetch(self.reverse_url('api:v1:user:list'))
        print(response)