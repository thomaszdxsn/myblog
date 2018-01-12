#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import unittest

from sqlalchemy import create_engine
from tornado.testing import AsyncTestCase

from config import TestingConfig
from app.models import *

__all__ = ['AuthModelTestCase', 'BlogPostModelTestCase']
# 测试专用engine
test_engine = create_engine(TestingConfig.SQLALCHEMY_URI)


class ModelTestMixin(object):
    def setUp(self):
        Base.metadata.create_all(test_engine)
        self.db = Session(bind=test_engine)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(test_engine)

# ========================================================
# auth-model testing =====================================
# ========================================================


class AuthModelTestCase(ModelTestMixin, unittest.TestCase):

    def test_user_email_check_duplicate(self):
        u = User(email='user1')
        self.db.add(u)
        self.db.commit()
        self.assertTrue(User.email_exists('user1', self.db))

    def test_user_passwd_cant_read(self):
        u = User(email='user1')
        with self.assertRaises(AttributeError):
            u.password

    def test_user_passwd_generate_hash_and_salt(self):
        u = User(email='user1')
        u.password = 'password'
        self.assertTrue(u.salt is not None)
        self.assertTrue(u.encrypt_password is not None)

    def test_user_passwd_can_verify(self):
        u = User(email='user1')
        u.password = 'password'
        self.assertTrue(u.verify_password('password'))

    def test_user_create_role_relationship(self):
        u = User(email='user1')
        r = Role(name='role1')
        u.roles.append(r)
        self.assertIn(r, u.roles)


# ========================================================
# blog-post testing ======================================
# ========================================================


class BlogPostModelTestCase(ModelTestMixin, unittest.TestCase):

    def test_category_can_related_category(self):
        c1 = Category(name='category1')
        c2 = Category(name='category2')
        c1.children.append(c2)
        self.assertIn(c2, c1.children)
        self.assertEqual(c2.parent, c1)

    def test_category_cant_duplicate_name(self):
        c1 = Category(name='category1')
        self.db.add(c1)
        self.db.commit()
        self.assertTrue(Category.exists('category1', self.db))