#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime

from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        bindparam)
from sqlalchemy.orm import relationship, backref

from .base import Base, sql_bakery

__all__ = ['Category']


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String(36), index=True, nullable=False, unique=True)
    created_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, onupdate=datetime.now)

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

