#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""博客页面的handlers"""
from ..base.handlers import BaseHandler
from ..models.post import Post, Category
from ..models.sys_config import SysConfig


class HomepageHandler(BaseHandler):
    """首页"""

    def prepare(self):
        super(HomepageHandler, self).prepare()
        self._page_num = self.get_query_argument('page', 1)

    def get(self, *args, **kwargs):
        """

        context变量介绍:

        :param archive_info(list):

            归档信息: (月份，该月发布的文章数量)，倒序排列(最近的日期在前)

        :param post_data(dict):

            博客文章信息: 包含已分页的文章对象列表，以及分页相关信息，倒序排列

        :param category_data(ResultList):

            分类信息: 所有创建的文章分类对象列表
        """
        _post_obj_list = Post.get_published_post(self.db)
        post_data = self.handle_object_list(
            _post_obj_list,
            page_num=self._page_num,
            per_page=SysConfig.get(**SysConfig.blog_per_page),
        )
        category_data = Category.get_object_list(self.db)
        archive_info = Post.get_archive_month(self.db)
        self.render(
            "homepage.html",
            post_data=post_data,
            category_data=category_data,
            archive_info=archive_info
        )


