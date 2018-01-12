#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata
Session = sessionmaker()