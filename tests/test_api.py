#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado import gen

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

    def api_fetch(self, url, *args, **kwargs):
        response = self.fetch(url, *args, **kwargs)
        data = json.loads(response.body)
        return data

    def test_get_user_object_list(self):
        u1 = User(email='user1', password='123')
        u2 = User(email='user2', password='123')
        self.db.add_all([
            u1, u2
        ])
        self.db.commit()
        data = self.api_fetch(self.reverse_url("api:v1:user:list"))
        self.assertTrue(data['count'] == 2)
        self.assertIn(json.loads(data['object_list'])[0]['email'],
                      ['user1', 'user2'])

    def test_user_object_list_can_pagination(self):
        user_list = []
        for i in range(101):
            user_list.append(User(email='user{}'.format(i), password=123))
        self.db.add_all(user_list)
        self.db.commit()
        data = self.api_fetch(self.reverse_url('api:v1:user:list'))
        self.assertTrue(data['count'] == 101)
        self.assertTrue(data['total_pages'] == 3)

    def test_user_create_invalid_arg_get_400_response(self):
        response = self.fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=''
        )
        self.assertTrue(response.code, 400)

    def test_user_create_without_required_field(self):
        data = self.api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({'nothing': 1})
        )
        self.assertIn('required', ''.join(data['password']))
        self.assertIn('required', ''.join(data['email']))
        self.assertEqual(1, data['error'])

    def test_user_create_invalid_password_input(self):
        data1 = self.api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({
                'email': 'example@qq.com',
                'password': 'short'
            })
        )
        data2 = self.api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({
                'email': 'example@qq.com',
                'password': 'thispasswordtoolongsoitisinvalidyetbeacausethan32'
            })
        )
        self.assertEqual(1, data1['error'])
        self.assertEqual(1, data2['error'])
        self.assertIn('Invalid', ''.join(data1['password']))
        self.assertIn('Invalid', ''.join(data2['password']))

    def test_user_create_successful(self):
        data = self.api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({'email': '123qwe@qq.com', 'password': 'a1234521'})
        )
        self.assertEqual(0, data['error'])

        obj = self.db.query(User).get(1)
        self.assertTrue(obj.verify_password('a1234521'))


