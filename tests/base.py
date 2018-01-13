#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from sqlalchemy import create_engine

from config import TestingConfig
from app.models import *


test_engine = create_engine(TestingConfig.SQLALCHEMY_URI)


class ModelTestMixin(object):
    def setUp(self):
        super().setUp()
        Base.metadata.create_all(test_engine)
        self.db = Session(bind=test_engine)

    def tearDown(self):
        super().tearDown()
        self.db.close()
        Base.metadata.drop_all(test_engine)