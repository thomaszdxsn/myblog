#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
from io import BytesIO

from tornado.testing import AsyncHTTPTestCase

from app.models import *
from app import create_app
from .base import ModelTestMixin
from app.models.sys_config import redis_cli

__all__ = ['APIV1TestCase']

# ========================================================
# api_v1 testing =========================================
# ========================================================


class APIV1TestCase(ModelTestMixin, AsyncHTTPTestCase):

    def tearDown(self):
        super().tearDown()
        # 清理所有的session-id
        session_keys = redis_cli.keys("session:*")
        for key in session_keys:
            redis_cli.delete(key)

    def get_app(self):
        return create_app('test')

    def reverse_url(self, *args, **kwargs):
        return self._app.reverse_url(*args, **kwargs)
    
    def login(self):
        u = self.db.query(User).filter_by(
            email='dont-duplicate@qq.com'
        ).one_or_none()
        if u is None:
            u = User(email='dont-duplicate@qq.com', password='a1234567')
            self.db.add(u)
            self.db.commit()
        login_response = self.fetch(
            self.reverse_url('api:v1:user:session_id'),
            method='POST',
            body=json.dumps({
                "email": "dont-duplicate@qq.com",
                'password': 'a1234567'
            })
        )
        session_id = login_response.headers['Session-ID']
        return session_id

    def api_fetch(self, url, *args, **kwargs):
        response = self.fetch(url, *args, **kwargs)
        data = json.loads(response.body)
        return data
    
    def auth_api_fetch(self, url, *args, **kwargs):
        response = self.auth_fetch(url, *args, **kwargs)
        data = json.loads(response.body)
        return data

    def auth_fetch(self, url, *args, **kwargs):
        session_id = self.login()
        return self.fetch(url, *args,
                          headers={"Session-ID": session_id},
                          **kwargs)
        
    def test_session_id_create_successful(self):
        u = User(email='example@qq.com', password='a1234567')
        self.db.add(u)
        self.db.commit()
        login_response = self.fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='POST',
            body=json.dumps({
                'email': "example@qq.com",
                'password': 'a1234567'
            })
        )
        session_id = login_response.headers.get('Session-ID', None)
        self.assertTrue(session_id is not None)
        self.assertEqual(201, login_response.code)
        data = self.api_fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='GET',
            headers={"Session-ID": session_id}
        )
        self.assertEqual(session_id, data['session_id'])

    def test_session_id_create_fail_400_by_no_arg(self):
        login_response = self.fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='POST',
            body='invalid json'
        )
        self.assertEqual(400, login_response.code)

    def test_session_id_create_fail_by_invalid_arg(self):
        data = self.api_fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='POST',
            body=json.dumps({"email": "invalidemail", "password": "short"})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('email', data)
        self.assertIn("password", data)

    def test_session_id_create_fail_by_not_email(self):
        data = self.api_fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='POST',
            body=json.dumps({
                'email': "example@qq.com",
                'password': 'a1234567'
            })
        )
        self.assertTrue(data['error'] != 0)
        self.assertEqual(data['msg'], 'email or password error')

    def test_session_id_cerate_fail_by_mismatch_password(self):
        u = User(email='example@qq.com', password='a7654321')
        self.db.add(u)
        self.db.commit()
        data = self.api_fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='POST',
            body=json.dumps({
                'email': "example@qq.com",
                'password': 'a1234567'
            })
        )
        self.assertTrue(data['error'] != 0)
        self.assertEqual(data['msg'], 'email or password error')

    def test_get_session_id_fail_401_by_not_login(self):
        response = self.fetch(
            self.reverse_url("api:v1:user:session_id"),
        )
        self.assertEqual(401, response.code)

    def test_delete_session_fail_401_by_not_login(self):
        response = self.fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='DELETE'
        )
        self.assertEqual(401, response.code)

    def test_delete_session_success(self):
        u = User(email='example@qq.com', password='a1234567')
        self.db.add(u)
        self.db.commit()
        login_response = self.fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='POST',
            body=json.dumps({
                'email': "example@qq.com",
                'password': 'a1234567'
            })
        )
        session_id = login_response.headers.get('Session-ID', None)
        self.assertTrue(session_id is not None)
        self.assertEqual(201, login_response.code)

        logout_response = self.fetch(
            self.reverse_url("api:v1:user:session_id"),
            method='DELETE',
            headers={"Session-ID": session_id}
        )
        self.assertEqual(204, logout_response.code)

        response = self.fetch(
            self.reverse_url("api:v1:user:session_id"),
            headers={"Session-ID": session_id}
        )
        self.assertEqual(401, response.code)

    def test_get_user_object_list(self):
        u1 = User(email='user1', password='123')
        u2 = User(email='user2', password='123')
        self.db.add_all([
            u1, u2
        ])
        self.db.commit()
        data = self.auth_api_fetch(self.reverse_url("api:v1:user:list"))
        # 在api验证时新增了一个user对象
        self.assertTrue(data['count'] == 3)
        self.assertIn(json.loads(data['object_list'][1])['email'],
                      ['user1', 'user2'])

    def test_user_create_invalid_arg_get_400_response(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=''
        )
        self.assertEqual(response.code, 400)

    def test_user_create_without_required_field(self):
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({'nothing': 1})
        )
        self.assertIn('required', ''.join(data['password']))
        self.assertIn('required', ''.join(data['email']))
        self.assertEqual(1, data['error'])

    def test_user_create_invalid_password_input(self):
        data1 = self.auth_api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({
                'email': 'example2@qq.com',
                'password': 'short'
            })
        )
        data2 = self.auth_api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({
                'email': 'example2@qq.com',
                'password': 'thispasswordtoolongsoitisinvalidyetbeacausethan32'
            })
        )
        self.assertEqual(1, data1['error'])
        self.assertEqual(1, data2['error'])
        self.assertIn('Invalid', ''.join(data1['password']))
        self.assertIn('Invalid', ''.join(data2['password']))

    def test_user_create_successful(self):
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:user:list'),
            method='POST',
            body=json.dumps({'email': '123qwe@qq.com', 'password': 'a1234521'})
        )
        self.assertEqual(0, data['error'])

        obj = self.db.query(User).filter_by(email='123qwe@qq.com').one()
        self.assertTrue(obj.verify_password('a1234521'))

    def test_get_user_detail_404(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:user:detail', 2),
        )
        self.assertEqual(response.code, 404)

    def test_get_user_detail_by_id(self):
        u1 = User(email='user1', password=123)
        self.db.add(u1)
        self.db.commit()

        data = self.auth_api_fetch(
            self.reverse_url('api:v1:user:detail', 1)
        )
        self.assertTrue(data['email'] == 'user1')

    def test_delete_user_404(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:user:detail', 2),
            method='DELETE'
        )
        self.assertEqual(404, response.code)

    def test_delete_user_successful(self):
        u1 = User(email='user1', password=123)
        self.db.add(u1)
        self.db.commit()
        self.auth_fetch(
            self.reverse_url('api:v1:user:detail', 2),
            method='DELETE'
        )
        response = self.auth_fetch(
            self.reverse_url('api:v1:user:detail', 2),
        )
        self.assertEqual(404, response.code)

    def test_update_user_404(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:user:detail', 2),
            method='PUT',
            body=json.dumps({'email': 'user1'})
        )
        self.assertEqual(404, response.code)

    def test_update_user_fail_by_duplicate(self):
        u1 = User(email='example1@qq.com', password='a1234567')
        u2 = User(email='example2@qq.com', password='a1234567')
        self.db.add_all([u1, u2])
        self.db.commit()
        data = self.auth_api_fetch(
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
        data = self.auth_api_fetch(
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
        response = self.auth_fetch(
            self.reverse_url('api:v1:user:detail', 1),
            method='PUT',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_create_category_obj(self):
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:category:list'),
            method='POST',
            body=json.dumps({"name": 'category1'})
        )
        self.assertEqual(0, data['error'])

        obj = self.db.query(Category).get(1)
        self.assertEqual(obj.name, 'category1')

    def test_category_create_without_arg_400_code(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:category:list'),
            method='POST',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_category_create_fail_by_duplicate_name(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:category:list'),
            method='POST',
            body=json.dumps({"name": "category1"})
        )
        self.assertIn('exists', data['msg'])
        self.assertTrue(data['error'] != 0)

    def test_category_delete_fail_by_404(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='DELETE',
        )
        self.assertEqual(404, response.code)

    def test_category_delete_successful(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        response = self.auth_fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='DELETE',
        )
        self.assertEqual(204, response.code)
        self.assertFalse(Category.exists('category1', self.db))

    def test_category_update_fail_by_without_arg(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        response = self.auth_fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='PUT',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_category_update_fail_by_404(self):
        response = self.auth_fetch(
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
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:category:detail', 1),
            method='PUT',
            body=json.dumps({"name": 'category2'})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn("exists", data['msg'])

    def test_tag_crate_fail_by_no_arg_400(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:tag:list'),
            method='POST',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_tag_create_fail_by_duplicate_name(self):
        t1 = Tag(name='tag1')
        self.db.add(t1)
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:tag:list'),
            method='POST',
            body=json.dumps({"name": 'tag1'})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('exists', data['msg'])

    def test_tag_create_successful(self):
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:tag:list'),
            method='POST',
            body=json.dumps({"name": 'tag1'})
        )
        self.assertTrue(data['error'] == 0)
        self.assertTrue(Tag.exists("tag1", self.db))

    def test_tag_delete_fail_by_404(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='DELETE',
        )
        self.assertEqual(404, response.code)

    def test_tag_delete_successful(self):
        t1 = Tag(name='tag1')
        self.db.add(t1)
        self.db.commit()
        response = self.auth_fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='DELETE'
        )
        self.assertTrue(204, response.code)
        self.assertFalse(Tag.exists('tag1', self.db))

    def test_tag_update_fail_by_404(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='PUT',
            body=json.dumps({"name": 'tag1'})
        )
        self.assertEqual(404, response.code)

    def test_tag_update_fail_by_400_no_arg(self):
        t1 = Tag(name='tag1')
        self.db.add(t1)
        self.db.commit()
        response = self.auth_fetch(
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
        data = self.auth_api_fetch(
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
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:tag:detail', 1),
            method='PUT',
            body=json.dumps({"name": 'tag2'})
        )
        self.assertTrue(data['error'] == 0)
        self.assertTrue(Tag.exists('tag2', self.db))

    def test_post_create_invalid_arg(self):
        data = self.auth_api_fetch(
            self.reverse_url("api:v1:post:list"),
            method='POST',
            body=json.dumps({"title": "justtitle"})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('required', "".join(data['category_id']))
        self.assertIn("required", "".join(data['slug']))

    def test_post_create_error_by_400_without_arg(self):
        response = self.auth_fetch(
            self.reverse_url("api:v1:post:list"),
            method='POST',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_post_create_error_by_duplicate_arg(self):
        c1 = Category(name='category1')
        p1 = Post(title='post1', slug='post1')
        p1.category = c1
        self.db.add(p1)
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url("api:v1:post:list"),
            method='POST',
            body=json.dumps({"title": "post1", 'slug': "post1", "category_id":1})
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('exists', data['msg'])

    def test_post_create_successful(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url("api:v1:post:list"),
            method='POST',
            body=json.dumps(
                {"title": "post1", 'slug': "post1", "category_id": 1})
        )
        self.assertTrue(data['error'] == 0)

        obj = Post.get_object_by_id(self.db, 1)
        self.assertEqual(obj.category, c1)
        self.assertTrue(obj.title == 'post1')

    def test_post_update_error_400_by_without_arg(self):
        c1 = Category(name='category1')
        p1 = Post(title='post1', slug='post1')
        p1.category = c1
        self.db.add(p1)
        self.db.commit()
        response = self.auth_fetch(
            self.reverse_url("api:v1:post:detail", 1),
            method='PUT',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_post_update_error_404_by_no_obj(self):
        response = self.auth_fetch(
            self.reverse_url("api:v1:post:detail", 1),
            method='PUT',
            body=json.dumps({
                'title': 'post1', 'slug': 'slug1', 'category_id': 1
            })
        )
        self.assertEqual(404, response.code)

    def test_post_update_error_by_duplicate_title(self):
        c1 = Category(name='category1')
        p1 = Post(title='post1', slug='post1')
        p2 = Post(title='post2', slug='post2')
        p1.category = c1
        p2.category = c1
        self.db.add_all([p1, p2, c1])
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url("api:v1:post:detail", 1),
            method='PUT',
            body=json.dumps({
                'title': 'post2', 'slug': 'slug1', 'category_id': 1
            })
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('exists', data['msg'])

    def test_post_update_successful(self):
        c1 = Category(name='category1')
        p1 = Post(title='post1', slug='post1')
        p1.category = c1
        self.db.add(p1)
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url("api:v1:post:detail", 1),
            method='PUT',
            body=json.dumps({
                "title": 'post2'
            })
        )
        self.assertTrue(data['error'] == 0)
        self.assertTrue(Post.exists('post2', self.db))

    def test_delete_error_by_404(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:post:detail', 1),
            method='DELETE',
        )
        self.assertEqual(404, response.code)

    def test_delete_successful(self):
        c1 = Category(name='category1')
        p1 = Post(title='post1', slug='post1')
        p1.category = c1
        self.db.add(p1)
        self.db.commit()
        response = self.auth_fetch(
            self.reverse_url('api:v1:post:detail', 1),
            method='DELETE',
        )
        self.assertTrue(204, response.code)
        self.assertFalse(Post.exists('post1', self.db))

    def test_create_comment_error_400_by_without_arg(self):
        response = self.auth_fetch(
            self.reverse_url("api:v1:comment:list"),
            method='POST',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_create_comment_error_by_invalid_arg(self):
        data = self.auth_api_fetch(
            self.reverse_url("api:v1:comment:list"),
            method='POST',
            body=json.dumps({
                'notthisarg': 1
            })
        )
        self.assertTrue(data['error'] != 0)
        self.assertIn('required', "".join(data['post_id']))
        self.assertIn("required", "".join(data['email']))
        self.assertIn('required', "".join(data['title']))
        self.assertIn('required', "".join(data['content']))

    def test_create_comment_successful(self):
        p1 = Post(title='post1', slug='post1')
        self.db.add(p1)
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url("api:v1:comment:list"),
            method='POST',
            body=json.dumps({
                "post_id": 1,
                "email": "example@qq.com",
                "title": "comment1",
                "content": "comment1"
            })
        )
        self.assertTrue(data['error'] == 0)

        obj = self.db.query(Comment).get(1)
        self.assertEqual(obj.title, 'comment1')
        self.assertIn(obj, p1.comment_set)

    def test_update_comment_fail_400_by_no_arg(self):
        p1 = Post(title='post1', slug='post1')
        c1 = Comment(title='post1')
        c1.post = p1
        self.db.add(c1)
        self.db.commit()
        response = self.auth_fetch(
            self.reverse_url('api:v1:comment:detail', 1),
            method='PUT',
            body='invalid json'
        )
        self.assertEqual(400, response.code)

    def test_update_comment_fail_404_by_no_object(self):
        response = self.auth_fetch(
            self.reverse_url("api:v1:comment:detail", 1),
            method='PUT',
            body='no sense'
        )
        self.assertEqual(404, response.code)

    def test_update_comment_successful(self):
        p1 = Post(title='post1', slug='post1')
        c1 = Comment(title='post1')
        c1.post = p1
        self.db.add(c1)
        self.db.commit()
        data = self.auth_api_fetch(
            self.reverse_url('api:v1:comment:detail', 1),
            method='PUT',
            body=json.dumps({"title": "post2"})
        )
        self.assertTrue(data['error'] == 0)
        obj = self.db.query(Comment).get(1)
        self.assertEqual(obj.title, 'post2')

    def test_delete_comment_fail_404_by_no_object(self):
        response = self.auth_fetch(
            self.reverse_url('api:v1:comment:detail', 1),
            method='DELETE'
        )
        self.assertEqual(404, response.code)

    def test_delete_comment_successful(self):
        p1 = Post(title='post1', slug='post1')
        c1 = Comment(title='post1')
        c1.post = p1
        self.db.add(c1)
        self.db.commit()
        response = self.auth_fetch(
            self.reverse_url('api:v1:comment:detail', 1),
            method='DELETE',
        )
        self.assertTrue(204, response.code)
        obj = self.db.query(Comment).get(1)
        self.assertEqual(obj, None)