#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        bindparam, Text, Boolean)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

from .base import Base, sql_bakery, ModelAPIMixin

__all__ = ['Category', 'Image', 'Post', 'Comment', 'Tag', 'PostTag']

# ========================================================
# models =================================================
# ========================================================


class Category(ModelAPIMixin, Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(36), index=True, nullable=False, unique=True)
    created_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, onupdate=datetime.now)

    parent_id = Column(Integer, ForeignKey('category.id'))
    children = relationship(
        'Category',
        cascade='all, delete-orphan',
        # 必须使用`remote_side=`关键字参数
        backref=backref('parent', remote_side=id),
    )

    @staticmethod
    def exists(name, session):
        """检查分类名是否已经存在"""
        exists_query = sql_bakery(lambda session: session.query(Category.id))
        exists_query += lambda q: q.filter(
            Category.name == bindparam('name')
        )
        result = exists_query(session).params(name=name).scalar()
        return result is not None


class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    key = Column(String(128))
    url = Column(String(256))
    created_time = Column(DateTime, default=datetime.now)


class Tag(ModelAPIMixin, Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True)
    created_time = Column(DateTime, default=datetime.now)

    @classmethod
    def exists(cls, name, session):
        baked_query = sql_bakery(lambda session: session.query(Tag.id))
        baked_query += lambda q: q.filter(Tag.name == bindparam('name'))
        result = baked_query(session).params(name=name).scalar()
        return result is not None


class PostTag(Base):
    __tablename__ = 'post_tag'

    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'), primary_key=True)
    tag = relationship('Tag', lazy='joined')

    def __init__(self, tag):
        self.tag = tag


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(64), index=True, nullable=False)
    slug = Column(String(128), nullable=False)
    content = Column(Text)
    status = Column(Boolean)
    publish_time = Column(DateTime, default=datetime.now, index=True)
    created_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, onupdate=datetime.now)
    image_id = Column(Integer, ForeignKey('image.id'))
    category_id = Column(Integer, ForeignKey('category.id'))

    post_tags = relationship(
        'PostTag',
        cascade='all, delete-orphan',
        backref='post'
    )
    tags = association_proxy('post_tags', 'tag')
    image = relationship(
        'Image',
        backref='post_set'
    )
    category = relationship(
        'Category',
        backref='post_set'
    )

    @staticmethod
    def get_published_post(session):
        baked_query = sql_bakery(lambda session: session.query(Post))
        baked_query += lambda q: q.filter(
            Post.publish_time <= bindparam('now')
        ).order_by(Post.publish_time)
        result = baked_query(session).params(
            now=datetime.now() + timedelta(minutes=5),  # 测试时有延迟
        )
        return result


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    email = Column(String(64))
    title = Column(String(128))
    content = Column(Text)
    floor = Column(Integer)
    status = Column(Boolean)

    # 关联post
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    post = relationship(
        'Post',
        cascade='all',
        backref=backref('comment_set',
                        lazy='dynamic'),
    )
    # 回复的comment
    reply_id = Column(Integer, ForeignKey('comment.id'), nullable=True)
    comment_set = relationship(
        'Comment',
        backref=backref('reply', remote_side=id)
    )


