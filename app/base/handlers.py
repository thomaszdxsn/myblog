#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""基础Handler模块
包括Handler基类`BaseHandler`的定义，以及首页handler等通用页面的handler定义
"""
import json

from tornado import web, gen

from sqlalchemy import create_engine

import redis

from ..libs.paginator import Paginator
from ..middlewares import MiddlewareProcess
from ..models import Session as DBSession
from ..models import User
from ..models.sys_config import SysConfig
from ..session import Session


class BaseHandler(web.RequestHandler):
    """Handler的基类"""
    _db = None
    _redis_cli = None
    _session = None

    @property
    def session(self):
        if self._session is None:
            self._session = Session(self)
        return self._session

    @property
    def db(self):
        if self._db is None:
            self._db = DBSession(bind=create_engine(self.config.SQLALCHEMY_URI,
                                                    pool_size=500,
                                                    pool_recycle=3600))
        return self._db

    @property
    def redis_cli(self):
        if self._redis_cli is None:
            self._redis_cli = redis.StrictRedis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                password=self.config.REDIS_PASSWORD
            )
        return self._redis_cli

    def get_current_user(self):
        if self.session.user_id:
            self.session.init_session()         # 保持登入状态
            return User.get_object_by_id(self.db,
                                         self.session.user_id)

    def write_error(self, status_code, **kwargs):
        """重写write_error()，现在可以自动加上状态码转化了"""
        self.set_status(status_code)
        super().write_error(status_code, **kwargs)

    def prepare(self):
        # web中间件的prepare处理
        self._middleware_list = self.config.MIDDLEWARES
        MiddlewareProcess.prepare(self, self._middleware_list)

    def on_finish(self):
        # web中间件的on_finish处理
        try:
            MiddlewareProcess.on_finish(self, self._middleware_list)
        except AttributeError:
            # 有可能没有设定middleware_list
            pass
        # clean工作
        if self._db:
            try:
                self._db.commit()
            except Exception as e:
                self.application.logger.error(
                    "database error", exc_info=True
                )
                self._db.rollback()
            finally:
                self._db.close()

    @property
    def config(self):
        return self.application.settings['config']

    def handle_object_list(self, object_list, page_num, to_json=False):
        """根据参数来筛选对象列表，默认进行分页"""
        paginator = Paginator(
            object_list,
            int(SysConfig.get(SysConfig.per_page['key'],
                          SysConfig.per_page['default']))
        )
        page = paginator.page(page_num)
        if to_json:
            object_list = [obj.to_list_json() for obj in page.object_list]
        else:
            object_list = page.object_list
        return {
            "object_list": object_list,
            "count": page.paginator.count,
            "total_pages": page.paginator.total_pages,
            "has_prev": page.has_previous(),
            "has_next": page.has_next(),
            "current_page": page_num
        }


class ListAPIMixin(object):
    """列表API接口的mixin"""
    model = None
    object_list = None
    post_form = None
    unique_field = None

    def prepare(self):
        """获取一些参数，进行一些准备工作"""
        if not self.current_user:
            return self.write_error(401)
        super().prepare()
        self._page = int(self.get_query_argument('page', 1))

    def get(self, *args, **kwargs):
        """获取对象列表"""
        if not self.object_list:
            self.object_list = self.model.get_object_list(self.db)
        data = self.handle_object_list(self.object_list, self._page,
                                       to_json=True)
        self.write(data)

    def post(self, *args, **kwargs):
        """新增对象"""
        # 解析json数据
        try:
            json_data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return self.write_error(400)

        # 表单验证
        form = self.post_form(data=json_data)
        if not form.validate():
            error_msg = {'error': 1}
            error_msg.update(form.errors)
            return self.write(error_msg)

        # 唯一性验证
        if self.unique_field:
            if self.model.exists(
                form.data[self.unique_field],
                self.db
            )is True:
                error_msg = {
                    'error': 2,
                    'msg': '{field}:{value} exists'.format(
                        field=self.unique_field,
                        value=form.data[self.unique_field]
                    )
                }
                return self.write(error_msg)

        # 创建对象
        self.model.create(self.db, **form.data)
        self.set_status(201)
        self.write({'error': 0})


class DetailAPIMixin(object):
    """详情API接口的mixin"""
    model = None
    put_form = None
    unique_field = None

    def prepare(self):
        if not self.current_user:
            return self.write_error(401)
        super().prepare()

    def get(self, *args, **kwargs):
        """获取对象详情"""
        id_ = kwargs['id']
        obj = self.model.get_object_by_id(self.db, id_)
        if not obj:
            return self.write_error(404, reason='Not Found')
        obj_data = obj.to_detail_json()
        self.write(obj_data)

    def put(self, *args, **kwargs):
        """更新该对象"""
        id_ = kwargs['id']
        obj = self.model.get_object_by_id(self.db, id_)
        if not obj:
            return self.write_error(404, reason='Not Found')

        # 解析JSON数据
        try:
            json_data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return self.write_error(400)
        # 处理表单验证
        form = self.put_form(data=json_data)
        if not form.validate():
            error_msg = {
                'error': 1,
            }
            error_msg.update(form.errors)
            return self.write(error_msg)
        # 唯一性验证
        if self.unique_field:
            if getattr(obj, self.unique_field) != \
                    form.data[self.unique_field]:
                if self.model.exists(
                    form.data[self.unique_field],
                    self.db
                ):
                    error_msg = {
                        'error': 2,
                        'msg': '{field}:{value} exists'.format(
                            field=self.unique_field,
                            value=form.data[self.unique_field]
                        )
                    }
                    return self.write(error_msg)

        # 更新操作
        self.model.update(self.db, obj, **form.data)
        self.set_status(201)
        return self.write({'error': 0})

    def delete(self, *args, **kwargs):
        """删除该对象"""
        id_ = kwargs['id']
        obj = self.model.get_object_by_id(self.db, id_)
        if not obj:
            return self.write_error(404, reason='Not Found')
        self.model.delete(self.db, obj)
        self.set_status(204)


class HomePageHandler(BaseHandler):
    """首页handler"""

    async def get(self, *args, **kwargs):
        # await gen.sleep(1)
        self.write("hello world")

    def post(self):
        pass