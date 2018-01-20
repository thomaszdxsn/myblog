#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from app.models.stats import SiteStats
from app.models.post import Post
from app.models import session_context
from .celery import app


@app.task
def sync_post_view():
    """同步所有文章的点击量数据"""
    with session_context() as session:
        all_post = session.query(Post).all()

        for post_obj in all_post:
            view_num = SiteStats.get_post_view(post_obj.slug)
            post_obj.view_num = view_num
            session.add(post_obj)


