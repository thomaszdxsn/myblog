#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import contextlib

from tornado.log import gen_log
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.baked import bakery

from config import CommonConfig
from ..libs.utils import DateEncoder


Base = declarative_base()
metadata = Base.metadata
Session = sessionmaker()
sql_bakery = bakery()


@contextlib.contextmanager
def session_context(uri=CommonConfig.SQLALCHEMY_URI):
    engine = create_engine(uri)
    try:
        session = Session(engine)
        yield session
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
    def update(cls, session, obj, **kwargs):
        """更新一个对象"""
        for k, v in kwargs.items():
            if v is not None:
                setattr(obj, k, v)
        session.add(obj)

    @staticmethod
    def jsonify(data):
        return json.dumps(data, cls=DateEncoder, ensure_ascii=False)

