#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .base.handlers import *

urlpatterns = [
    ('/', HomePageHandler, (), "homepage"),
]