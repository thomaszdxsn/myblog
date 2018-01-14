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
        self.assertEqual(response.code, 400)

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

    def test_get_user_detail_404(self):
        response = self.fetch(
            self.reverse_url('api:v1:user:detail', 1),
        )
        self.assertEqual(response.code, 404)

    def test_get_user_detail_by_id(self):
        u1 = User(email='user1', password=123)
        self.db.add(u1)
        self.db.commit()

        data = self.api_fetch(
            self.reverse_url('api:v1:user:detail', 1)
        )
        self.assertTrue(data['email'] == 'user1')

    def test_delete_user_404(self):
        response = self.fetch(
            self.reverse_url('api:v1:user:detail', 1),
            method='DELETE'
        )
        self.assertEqual(404, response.code)

    def test_delete_user_successful(self):
        u1 = User(email='user1', password=123)
        self.db.add(u1)
        self.db.commit()
        self.fetch(
            self.reverse_url('api:v1:user:detail', 1),
            method='DELETE'
        )
        response = self.fetch(
            self.reverse_url('api:v1:user:detail', 1),
        )
        self.assertEqual(404, response.code)

    def test_update_user_404(self):
        response = self.fetch(
            self.reverse_url('api:v1:user:detail', 1),
            method='PUT',
            body=json.dumps({'email': 'user1'})
        )
        self.assertEqual(404, response.code)

    def test_update_user_fail_by_duplicate(self):
        u1 = User(email='example1@qq.com', password='a1234567')
        u2 = User(email='example2@qq.com', password='a1234567')
        self.db.add_all([u1, u2])
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:user:detail', 1),
            method='PUT',
            body=json.dumps({'email': 'example2@qq.com'})
        )
        self.assertEqual(2, data['error'])
        self.assertIn('exists', data['msg'])

    def test_update_user_fail_by_invalid_arg(self):
        u1 = User(email='example1@qq.com', password='a1234567')
        self.db.add(u1)
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:user:detail', 1),
            method='PUT',
            body=json.dumps({'email': 'invalid email'})
        )
        self.assertEqual(1, data['error'])
        self.assertIn('Invalid', ''.join(data['email']))

    def test_update_user_fail_by_no_arg_400_status_code(self):
        u1 = User(email='example1@qq.com', password='a1234567')
        self.db.add(u1)
        self.db.commit()
        response = self.fetch(
            self.reverse_url('api:v1:user:detail', 1),
            method='PUT',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_create_category_obj(self):
        data = self.api_fetch(
            self.reverse_url('api:v1:category:list'),
            method='POST',
            body=json.dumps({"name": 'category1'})
        )
        self.assertEqual(0, data['error'])

        obj = self.db.query(Category).get(1)
        self.assertEqual(obj.name, 'category1')

    def test_category_create_without_arg_400_code(self):
        response = self.fetch(
            self.reverse_url('api:v1:category:list'),
            method='POST',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_category_create_fail_by_duplicate_name(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:category:list'),
            method='POST',
            body=json.dumps({"name": "category1"})
        )
        self.assertIn('exists', data['msg'])
        self.assertTrue(data['error'] != 0)

    def test_category_delete_fail_by_404(self):
        response = self.fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='DELETE',
        )
        self.assertEqual(404, response.code)

    def test_category_delete_successful(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='DELETE',
        )
        self.assertEqual(0, data['error'])
        self.assertFalse(Category.exists('category1', self.db))

    def test_category_update_fail_by_without_arg(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        response = self.fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='PUT',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_category_update_fail_by_404(self):
        response = self.fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='PUT',
            body=json.dumps({"name": "valid name"})
        )
        self.assertEqual(404, response.code)

    def test_category_update_fail_by_duplicate_name(self):
        c1 = Category(name='category1')
        c2 = Category(name='category2')
        self.db.add_all([
            c1, c2
        ])
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='PUT',
            body=json.dumps({"name": 'category2'})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn("exists", data['msg'])

    def test_tag_crate_fail_by_no_arg_400(self):
        response = self.fetch(
            self.reverse_url('api:v1:tag:list'),
            method='POST',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_tag_create_fail_by_duplicate_name(self):
        t1 = Tag(name='tag1')
        self.db.add(t1)
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:tag:list'),
            method='POST',
            body=json.dumps({"name": 'tag1'})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('exists', data['msg'])

    def test_tag_create_successful(self):
        data = self.api_fetch(
            self.reverse_url('api:v1:tag:list'),
            method='POST',
            body=json.dumps({"name": 'tag1'})
        )
        self.assertTrue(data['error'] == 0)
        self.assertTrue(Tag.exists("tag1", self.db))

    def test_tag_delete_fail_by_404(self):
        response = self.fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='DELETE',
        )
        self.assertEqual(404, response.code)

    def test_tag_delete_successful(self):
        t1 = Tag(name='tag1')
        self.db.add(t1)
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='DELETE'
        )
        self.assertTrue(data['error'] == 0)
        self.assertFalse(Tag.exists('tag1', self.db))

    def test_tag_update_fail_by_404(self):
        response = self.fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='PUT',
            body=json.dumps({"name": 'tag1'})
        )
        self.assertEqual(404, response.code)

    def test_tag_update_fail_by_400_no_arg(self):
        t1 = Tag(name='tag1')
        self.db.add(t1)
        self.db.commit()
        response = self.fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='PUT',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_tag_update_fail_by_duplicate_name(self):
        t1 = Tag(name='tag1')
        t2 = Tag(name='tag2')
        self.db.add_all([t1, t2])
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='PUT',
            body=json.dumps({"name": 'tag2'})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('exists', data['msg'])

    def test_tag_update_successful(self):
        t1 = Tag(name='tag1')
        self.db.add(t1)
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='PUT',
            body=json.dumps({"name": 'tag2'})
        )
        self.assertTrue(data['error'] == 0)
        self.assertTrue(Tag.exists('tag2', self.db))