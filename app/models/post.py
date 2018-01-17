#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        bindparam, Text, Boolean, func, text)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from .base import Base, sql_bakery, ModelAPIMixin

__all__ = ['Category', 'Image', 'Post', 'Comment', 'Tag', 'PostTag']

# ========================================================
# models =================================================
# ========================================================


class Category(ModelAPIMixin, Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(36), index=True, nullable=False, unique=True)

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

    def to_list_json(self):
        data = {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "parent": self.parent.name if self.parent else None,
            "created_time": self.created_time
        }
        return self.jsonify(data)

    def to_detail_json(self):
        data = {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "parent": self.parent.name,
            "created_time": self.created_time
        }
        return self.jsonify(data)


class Image(ModelAPIMixin, Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    key = Column(String(128))
    url = Column(String(256))  # TODO: URL写死是有问题的，在更换七牛domain的时候不能自动切换

    def thumbnail(self, width, height):
        """七牛云的缩略图功能"""
        return self.url + "?imageMogr2/thumbnail/{0}x{1}".format(
            width, height
        )


class Tag(ModelAPIMixin, Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True)

    @classmethod
    def exists(cls, name, session):
        baked_query = sql_bakery(lambda session: session.query(Tag.id))
        baked_query += lambda q: q.filter(Tag.name == bindparam('name'))
        result = baked_query(session).params(name=name).scalar()
        return result is not None

    @classmethod
    def create_by_string(cls, session, string, sep=','):
        """通过解析一个`tag1,tag2,tag3`的字符串来创建若干Tag对象"""
        tag_list = []
        tag_str_list = string.split(sep)
        for tag_str in tag_str_list:
            tag_str = tag_str.strip()
            obj = session.query(Tag).filter(
                Tag.name == tag_str
            ).one_or_none()
            if obj is None:
                obj = Tag(name=tag_str)
            tag_list.append(obj)
        return tag_list

    def to_list_json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'created_time': self.created_time
        }
        return self.jsonify(data)

    def to_detail_json(self):
        return self.to_list_json()


class PostTag(Base):
    __tablename__ = 'post_tag'

    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'), primary_key=True)
    tag = relationship('Tag', lazy='joined')

    def __init__(self, tag):
        self.tag = tag


class Post(ModelAPIMixin, Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(64), index=True, nullable=False)
    slug = Column(String(128), nullable=False)
    meta_description = Column(String(128))
    meta_keywords = Column(String(128))
    brief = Column(String(512))
    content = Column(Text)
    status = Column(Boolean, default=True)
    publish_time = Column(DateTime, default=datetime.now, index=True)
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
        backref=backref('post_set',
                        lazy='dynamic',
                        cascade='all, delete-orphan'
                        ),
    )

    @staticmethod
    def get_published_post(session):
        result = session.query(Post).filter(
            Post.publish_time <= datetime.now() + timedelta(minutes=1),
            Post.status == True
        ).order_by(Post.publish_time.desc())
        return result

    @staticmethod
    def exists(title, session):
        """根据标题判断文章是否存在"""
        baked_query = sql_bakery(lambda  session: session.query(Post.id))
        baked_query += lambda q: q.filter(
            Post.title == bindparam('title')
        )
        result = baked_query(session).params(title=title).scalar()
        return result is not None

    @staticmethod
    def slug_exists(slug, session):
        """判断slug是否存在"""
        baked_query = sql_bakery(lambda session: session.query(Post.id))
        baked_query += lambda q: q.filter(
            Post.slug == bindparam('slug')
        )
        result = baked_query(session).params(slug=slug).scalar()
        return result is not None

    @classmethod
    def create(cls, session, **kwargs):
        """创建Post对象，但是会判断slug是非存在再自动为它追加后缀，防止重复"""
        raw_slug = kwargs.pop('slug')
        tags = kwargs.pop("tags", None)
        slug = raw_slug
        index = 1
        while True:
            if cls.slug_exists(slug, session):
                slug = raw_slug + "-" + str(index)
                index += 1
            else:
                slug = raw_slug
                break
        obj = cls(slug=slug, **kwargs)
        if tags:
            obj.tags = tags
        session.add(obj)
        return obj

    @classmethod
    def get_archive_month(cls, session):
        """获取所有有文章发布的月份和这个月份发布的文章数量，用于显示归档(archive)信息

        :return: 返回二维元组(month, article_count)的列表
        """

        final_result = []
        # 获取所有发布过文章的月份
        month_baked_sql = sql_bakery(
            lambda session: session.query(
                func.DATE_FORMAT(Post.publish_time, "%Y%m")
                    .distinct()
                    .label("publish_month")
            )
        )
        month_baked_sql += lambda q: q.filter(
            Post.publish_time < bindparam('now')
        ).order_by(text("publish_month desc"))
        # 获取特定月份发布的文章数量
        article_count_query = sql_bakery(
            lambda session: session.query(
                func.COUNT(Post.id)
            )
        )
        article_count_query += lambda q: q.filter(
            func.DATE_FORMAT(Post.publish_time, "%Y%m") == bindparam('month')
        )

        month_results = month_baked_sql(session).\
            params(now=datetime.now()).all()
        for result in month_results:
            article_count = article_count_query(session).\
                                params(month=result.publish_month).scalar()
            final_result.append(
                (datetime.strptime(result.publish_month, "%Y%m"),
                 article_count)
            )
        return final_result

    def to_list_json(self):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'status': self.status,
            'image': self.image.url,
            'category': self.category.name,
            'publish_time': self.publish_time
        }
        return self.jsonify(data)

    def to_detail_json(self):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'status': self.status,
            'image': self.image.url,
            'category': self.category.name,
            'publish_time': self.publish_time,
            'created_time': self.created_time,
            'modified_time': self.modified_time
        }
        return self.jsonify(data)


class Comment(ModelAPIMixin, Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    email = Column(String(64))
    title = Column(String(128))
    content = Column(Text)
    floor = Column(Integer)
    status = Column(Boolean, default=True)

    # 关联post
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    post = relationship(
        'Post',
        cascade='all',
        backref=backref(
            'comment_set',
            order_by='Comment.floor',
            collection_class=ordering_list('floor', count_from=1),
        ),
    )
    # 回复的comment
    reply_id = Column(Integer, ForeignKey('comment.id'), nullable=True)
    comment_set = relationship(
        'Comment',
        backref=backref('reply', remote_side=id)
    )


