#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tornado import web
from tornado.log import app_log

from .urls import urlpatterns
from config import config_dict


def create_app(mode='dev'):
    """app实例的工厂函数"""
    config_cls = config_dict[mode]
    app = web.Application(
        urlpatterns,
        config=config_cls,
        **config_cls.APP_SETTINGS
    )
    app.logger = app_log
    return app