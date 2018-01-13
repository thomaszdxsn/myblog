#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""基础Handler模块
包括Handler基类`BaseHandler`的定义，以及首页handler等通用页面的handler定义
"""

from tornado import web, gen

from sqlalchemy import create_engine

from ..libs.paginator import Paginator
from ..middlewares import MiddlewareProcess
from ..models import Session


class BaseHandler(web.RequestHandler):
    """Handler的基类"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = Session(bind=create_engine(self.config.SQLALCHEMY_URI))
        return self._db

    def prepare(self):
        # web中间件的prepare处理
        self._middleware_list = self.config.MIDDLEWARES
        MiddlewareProcess.prepare(self, self._middleware_list)

    def on_finish(self):
        # web中间件的on_finish处理
        MiddlewareProcess.on_finish(self, self._middleware_list)
        # clean工作
        if self._db:
            self._db.close()

    @property
    def config(self):
        return self.application.settings['config']


class ListAPIMixin(object):
    """列表API接口的mixin"""
    model = None
    object_list = None
    post_form = None
    unique_field = None
    paginate_by = 50            # TODO: 使用系统配置

    def prepare(self):
        """获取一些参数，进行一些准备工作"""
        super().prepare()
        self._page = int(self.get_query_argument('page', 1))

    def handle_object_list(self, object_list):
        """根据参数来筛选对象列表，默认进行分页"""
        paginator = Paginator(object_list, self.paginate_by)
        page = paginator.page(self._page)
        return {
            "object_list": [obj._as_dict() for obj in page.object_list],
            "count": page.paginator.count,
            "total_pages": page.paginator.total_pages,
            "has_prev": page.has_previous(),
            "has_next": page.has_next()
        }

    def get(self, *args, **kwargs):
        """获取对象列表"""
        if not self.object_list:
            self.object_list = self.model.get_object_list(self.db)
        data = self.handle_object_list(self.object_list)
        self.write(data)

    def post(self, *args, **kwargs):
        """新增对象"""
        pass


class DetailAPIMixin(object):
    """详情API接口的mixin"""
    model = None
    put_form = None
    unique_field = None

    def get(self, *args, **kwargs):
        """获取对象详情"""
        pass

    def put(self, *args, **kwargs):
        """更新该对象"""
        pass

    def delete(self, *args, **kwargs):
        """删除该对象"""
        pass


class HomePageHandler(BaseHandler):
    """首页handler"""

    async def get(self, *args, **kwargs):
        # await gen.sleep(1)
        self.write("hello world")

    def post(self):
        pass