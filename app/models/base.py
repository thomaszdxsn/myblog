#! /usr/bin/env python
# -*- coding: utf-8 -*-
import contextlib

from tornado.log import gen_log
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.baked import bakery

from config import CommonConfig


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

    @classmethod
    def get_object_list(cls, session):
        """返回该model的对象列表"""
        object_list = session.query(cls)
        return object_list

