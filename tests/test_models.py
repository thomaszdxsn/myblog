#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import unittest
from datetime import datetime, timedelta

from sqlalchemy import create_engine

from app.models import *
from .base import ModelTestMixin

__all__ = ['AuthModelTestCase', 'BlogPostModelTestCase']


# ========================================================
# auth-model testing =====================================
# ========================================================


class AuthModelTestCase(ModelTestMixin, unittest.TestCase):

    def test_user_email_check_duplicate(self):
        u = User(email='user1', password=123)
        self.db.add(u)
        self.db.commit()
        self.assertTrue(User.exists('user1', self.db))

    def test_user_passwd_cant_read(self):
        u = User(email='user1', password=123)
        with self.assertRaises(AttributeError):
            u.password

    def test_user_passwd_generate_hash_and_salt(self):
        u = User(email='user1', password=123)
        u.password = 'password'
        self.assertTrue(u.salt is not None)
        self.assertTrue(u.encrypt_password is not None)

    def test_user_passwd_can_verify(self):
        u = User(email='user1', password=123)
        u.password = 'password'
        self.assertTrue(u.verify_password('password'))

    def test_user_create_role_relationship(self):
        u = User(email='user1', password=123)
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

    def test_post_can_own_by_category(self):
        p1 = Post(title='post1', slug='post1')
        c1 = Category(name='category1')
        p1.category = c1
        self.assertIn(p1, c1.post_set)

    def test_get_published_post(self):
        self.db.add_all([
            Post(title='post1', slug='post1', publish_time=datetime.now()),
            Post(title='post2', slug='post2', publish_time=datetime.now()),
            Post(
                title='post3',
                slug='post3',
                publish_time=(datetime.now() + timedelta(days=1))
            )
        ])
        self.db.commit()
        self.assertEqual(Post.get_published_post(self.db).count(), 2)

    def test_comment_can_comment_self(self):
        p1 = Post(title='post1', slug='post1')
        c1 = Comment(post=p1, title='comment1')
        c2 = Comment(post=p1, title='comment2', reply=c1)
        self.assertTrue(c2.reply == c1)
        self.assertIn(c2, c1.comment_set)

    def test_post_tag_add(self):
        p1 = Post(title='post1', slug='post1')
        t1 = Tag(name='tag1')
        t2 = Tag(name='tag2')
        p1.tags.extend([t1, t2])
        self.assertEqual([t1, t2], p1.tags)

    def test_comment_can_automatic_add_floor(self):
        p1 = Post(title='post1', slug='post1')
        c1 = Comment(post=p1, title='comment1')
        c2 = Comment(post=p1, title='comment2', reply=c1)
        self.db.add(p1)
        self.db.commit()
        self.assertEqual(c1.floor, 1)
        self.assertEqual(c2.floor, 2)

    def test_post_type_choices(self):
        p1 = Post(title='post1', slug='post1')
        p1.type = 'origin'
        self.db.add(p1)
        self.db.commit()

        obj = self.db.query(Post).get(1)
        self.assertEqual(obj.type.code, 'origin')
        self.assertNotEqual(obj.type.value, 'origin')
        self.assertEqual(obj.type.value, '原创')

