#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import contextlib
import datetime
import redis


from tornado.log import gen_log
from sqlalchemy import create_engine, Column, DateTime, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.baked import bakery

from config import CommonConfig
from ..libs.utils import DateEncoder


class BaseCls(object):
    created_time = Column(DateTime, default=datetime.datetime.now)
    modified_time = Column(DateTime,
                           onupdate=datetime.datetime.now,
                           default=datetime.datetime.now)


# 各种要多次使用的客户端，基类
Base = declarative_base(cls=BaseCls)        # 继承了2个时间字段的Base
NativeBase = declarative_base()             # 原生Base
metadata = Base.metadata
Session = sessionmaker()
sql_bakery = bakery()
redis_cli = redis.StrictRedis(
    host=CommonConfig.REDIS_HOST,
    port=CommonConfig.REDIS_PORT,
    password=CommonConfig.REDIS_PASSWORD
)


@contextlib.contextmanager
def session_context(uri=CommonConfig.SQLALCHEMY_URI):
    engine = create_engine(uri)
    session = Session(bind=engine)
    yield session
    try:
        session.commit()
    except:
        gen_log.error('session_context() commit error', exc_info=True)
        session.rollback()
    finally:
        session.close()


class ModelAPIMixin(object):
    """这个mixin为model提供操作方法，包括常见的增删查改..."""

    @classmethod
    def get_object_list(cls, session, field_list=None):
        """返回该model的对象列表"""
        if field_list:
            fields = [getattr(cls, field) for field in field_list]
            object_list = session.query(*fields)
        else:
            object_list = session.query(cls)
        object_list = object_list.order_by(cls.id.desc())
        return object_list

    @classmethod
    def create(cls, session, **kwargs):
        """创建一个对象"""
        data = {k: v for k, v in kwargs.items() if v is not None}
        obj = cls(**data)
        session.add(obj)
        return obj

    @classmethod
    def get_object_by_id(cls, session, id, field_list=None):
        """根据id来获取对象"""
        if field_list:
            fields = [getattr(cls, field) for field in field_list]
            obj = session.query(*fields).filter_by(id=id).one_or_none()
        else:
            obj = session.query(cls).get(id)
        return obj

    @classmethod
    def delete(cls, session, obj):
        """删除一个对象，注意传入对象而不是id"""
        session.delete(obj)

    @classmethod
    def update(cls, session, obj, patch=True, **kwargs):
        """更新一个对象, patch允许部分更新"""
        for k, v in kwargs.items():
            if patch:
                # TODO: wtforms有个问题，对于没有输入的值仍然会带有None值，
                # TODO: 所以暂时使用这个办法
                if v is not None:
                    setattr(obj, k, v)
            else:
                setattr(obj, k, v)
        session.add(obj)

    @staticmethod
    def jsonify(data):
        return json.dumps(data, cls=DateEncoder, ensure_ascii=False)

