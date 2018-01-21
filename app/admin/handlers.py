#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import uuid
from urllib.parse import urljoin
from io import BytesIO

from tornado import web, gen

from .forms import LoginForm, CategoryForm, PostForm, SysConfigForm
from .forms import ImageForm
from ..base.handlers import BaseHandler
from ..libs.utils import aggregate_errors
from ..libs.cloud import QiniuClient
from ..models.auth import User
from ..models.post import Category, Post, Image, Tag, PostCollection
from ..models.sys_config import SysConfig


class AdminLoginHandler(BaseHandler):
    """后台登入"""

    def get(self, *args, **kwargs):
        self.render("admin/login.html", errors=None)

    def post(self, *args, **kwargs):
        form = LoginForm(self.request.arguments)
        if not form.validate():
            error_string = aggregate_errors(form.errors)
            return self.render('admin/login.html', errors=error_string)
        obj = User.get_object_by_email(self.db, form.email.data)
        if obj is None:
            error_string = '用户名或密码错误'
            return self.render('admin/login.html', errors=error_string)
        if obj.verify_password(form.password.data) is False:
            error_string = '用户名或密码错误'
            return self.render('admin/login.html', errors=error_string)
        # 登录成功，记录session_id
        self.session.user_id = obj.id
        self.redirect(self.reverse_url("admin:post:list"), permanent=True)


class AdminLogoutHandler(BaseHandler):
    """后台登出"""

    def get(self, *args, **kwargs):
        self.clear_header('Session-ID')
        self.clear_cookie('session_id')
        self.session.logout()
        self.redirect(self.reverse_url('admin:login'))


class CategoryListHandler(BaseHandler):
    """分类列表"""
    _section = 'category'

    def prepare(self):
        super(CategoryListHandler, self).prepare()
        self._page = self.get_query_argument('page', 1)

    @web.authenticated
    def get(self, *args, **kwargs):
        object_list = Category.get_object_list(self.db)
        data = self.handle_object_list(
            object_list,
            self._page,
            SysConfig.get(**SysConfig.per_page)
        )
        self.render(
            "admin/category/list.html",
            section=self._section,
            data=data
        )


class CategoryCreateHandler(BaseHandler):
    """创建分类"""
    _section = "category"

    @web.authenticated
    def get(self, *args, **kwargs):
        category_list = Category.get_object_list(self.db)
        form = CategoryForm()
        parent_id_choices = form.parent_id.choices[:]
        parent_id_choices += [(obj.id, obj.name) for obj in category_list]
        form.parent_id.choices = parent_id_choices
        self.render(
            "admin/category/create.html",
            section=self._section,
            form=form,
            errors=None
        )

    @web.authenticated
    def post(self, *args, **kwargs):
        form = CategoryForm(self.request.arguments)
        category_list = Category.get_object_list(self.db)
        parent_id_choices = form.parent_id.choices[:]
        parent_id_choices += [(obj.id, obj.name) for obj in category_list]
        form.parent_id.choices = parent_id_choices
        if not form.validate():
            return self.render(
                "admin/category/create.html",
                section=self._section,
                form=form,
                errors=None
            )
        # 查询名称是否存在
        if Category.exists(form.name.data, self.db):
            return self.render(
                "admin/category/create.html",
                section=self._section,
                form=form,
                errors=u"分类名称:{} 已经存在".format(form.name.data)
            )
        Category.create(
            self.db,
            parent_id=None if form.parent_id.data == 0 else form.parent_id.data,
            name=form.name.data
        )
        self.redirect(
            self.reverse_url("admin:category:list"),
            permanent=True
        )


class CategoryDetailHandler(BaseHandler):
    """分类详情"""
    _section = 'category'

    @web.authenticated
    def get(self, *args, **kwargs):
        obj = Category.get_object_by_id(self.db, kwargs['id'])
        if not obj:
            return self.write_error(404)
        form = CategoryForm(
            data=obj.__dict__
        )
        category_list = Category.get_object_list(self.db)
        parent_id_choices = form.parent_id.choices[:]
        parent_id_choices += [(c_obj.id, c_obj.name) for c_obj in category_list
                              if c_obj is not obj]
        form.parent_id.choices = parent_id_choices
        self.render(
            "admin/category/edit.html",
            section=self._section,
            form=form,
            obj=obj,
            errors=None,
        )

    @web.authenticated
    def post(self, *args, **kwargs):
        obj = Category.get_object_by_id(self.db, kwargs['id'])
        if not obj:
            return self.write_error(404)
        form = CategoryForm(self.request.arguments)
        category_list = Category.get_object_list(self.db)
        parent_id_choices = form.parent_id.choices[:]
        parent_id_choices += [(obj.id, obj.name) for obj in category_list]
        form.parent_id.choices = parent_id_choices
        if not form.validate():
            return self.render(
                "admin/category/edit.html",
                section=self._section,
                form=form,
                errors=None,
                obj=obj
            )
        # 查询名称是否存在
        if form.name.data != obj.name:
            if Category.exists(form.name.data, self.db):
                return self.render(
                    "admin/category/edit.html",
                    section=self._section,
                    form=form,
                    errors=u"分类名称:{} 已经存在".format(form.name.data),
                    obj=obj
                )
        Category.update(
            self.db,
            obj,
            patch=False,
            parent_id=None if form.parent_id.data == 0 else form.parent_id.data,
            name=form.name.data
        )
        self.redirect(
            self.reverse_url("admin:category:list"),
            permanent=True
        )

    @web.authenticated
    def delete(self, *args,**kwargs):
        obj = Category.get_object_by_id(self.db, kwargs['id'])
        if not obj:
            return self.write_error(404)
        Category.delete(self.db, obj)
        self.set_status(204)


class PostListHandler(BaseHandler):
    """文章列表"""
    _section = 'post'

    def prepare(self):
        super(PostListHandler, self).prepare()
        self._page = self.get_query_argument('page', 1)

    @web.authenticated
    def get(self, *args, **kwargs):
        object_list = Post.get_object_list(self.db)
        data = self.handle_object_list(
            object_list,
            self._page,
            SysConfig.get(**SysConfig.per_page)
        )
        self.render(
            'admin/post/list.html',
            section=self._section,
            data=data
        )


class PostCreateHandler(BaseHandler):
    """创建新文章"""
    _section = 'post'

    @web.authenticated
    def get(self, *args, **kwargs):
        category_list = Category.get_object_list(self.db)
        form = PostForm()
        form.category_id.choices = [(obj.id, obj.name) for obj in category_list]
        self.render(
            "admin/post/create.html",
            section=self._section,
            errors=None,
            form=form
        )

    @gen.coroutine
    @web.authenticated
    def post(self, *args, **kwargs):
        category_list = Category.get_object_list(self.db)
        form = PostForm(self.request.arguments)
        form.category_id.choices = [(obj.id, obj.name) for obj in category_list]
        if not form.validate():
            return self.render(
                "admin/post/create.html",
                section=self._section,
                form=form,
                errors=None
            )
        # 判断标题是否已经使用
        if Post.exists(form.title.data, self.db):
            error_string = '文章标题: {} 已经被使用'.format(form.title.data)
            return self.render(
                "admin/post/create.html",
                section=self._section,
                form=form,
                errors=error_string
            )
        if self.request.files.get('image', None):
            # 判断文件类型是否为图片
            file_info = self.request.files['image'][0]
            if 'image' not in file_info['content_type']:
                error_string = '图片: 格式不正确，请传入正确的图片格式'.format(
                    form.title.data
                )
                return self.render(
                    "admin/post/create.html",
                    section=self._section,
                    form=form,
                    errors=error_string
                )

            # 上传图片
            image_key = str(uuid.uuid4())
            file_io = BytesIO(file_info['body'])
            qiniu_client = QiniuClient(
                self.config.QINIU_ACCESS_KEY,
                self.config.QINIU_SECRET_KEY,
                self.config.QINIU_BUCKET_NAME
            )
            # 使用线程池进行非堵塞上传
            upload_result = yield self.thread_pool.submit(
                qiniu_client.upload_file, image_key, file_io
            )
            if upload_result['error'] is True:
                error_string = '图片上传失败'
                self.application.logger.error(
                    "图片上传失败：{}".format(upload_result['exception'])
                )
                return self.render(
                    "admin/post/create.html",
                    section=self._section,
                    form=form,
                    errors=error_string
                )
            image_obj = Image.create(
                self.db,
                key=image_key,
                name=file_info['filename'],
                url=urljoin(self.config.QINIU_DOMAIN, image_key)
            )
            form.image.data = image_obj  # 共享一个变量，可以应对没有上传图片的情况

        # 处理文章集合
        if form.collection.data:
            collection = PostCollection.get_object_by_name(
                form.collection.data, self.db
            )
            if not collection:
                collection = PostCollection.create(
                    self.db,
                    name=form.collection.data
                )
            form.collection.data = collection
        post_obj = Post.create(
            self.db,
            category_id=form.category_id.data,
            title=form.title.data,
            slug=form.slug.data,
            brief=form.brief.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            status=form.status.data,
            publish_time=form.publish_time.data,
            content=form.content.data,
            type=form.type.data,
            collection=form.collection.data
        )
        # 处理标签
        tags = Tag.create_by_string(self.db, form.tags.data)
        if tags:
            post_obj.tags = tags
        if isinstance(form.image.data, Image):
            post_obj.image = form.image.data
        self.db.add(post_obj)
        self.redirect(self.reverse_url("admin:post:list"), permanent=True)


class PostDetailHandler(BaseHandler):
    """文章详情"""
    _section = 'post'

    @web.authenticated
    def get(self, *args, **kwargs):
        obj = Post.get_object_by_id(self.db, kwargs['id'])
        if not obj:
            return self.write_error(404)

        # 表单的自动填充
        category_list = Category.get_object_list(self.db)
        form_data = obj.__dict__
        form_data['type'] = obj.type.code
        form = PostForm(data=form_data)
        form.category_id.choices = [(obj.id, obj.name)
                                    for obj in category_list]
        if obj.collection:
            form.collection.data = obj.collection.name
        if obj.tags:
            form.tags.data = ",".join(tag.name for tag in obj.tags)

        self.render(
            "admin/post/edit.html",
            section=self._section,
            form=form,
            errors=None,
            obj=obj
        )

    @gen.coroutine
    @web.authenticated
    def post(self, *args, **kwargs):
        # 判断对象是否存在
        obj = Post.get_object_by_id(self.db, kwargs['id'])
        if not obj:
            return self.write_error(404)

        # 验证表单
        category_list = Category.get_object_list(self.db)
        form = PostForm(self.request.arguments)
        form.category_id.choices = [(obj.id, obj.name) for obj in category_list]
        if not form.validate():
            return self.render(
                "admin/post/create.html",
                section=self._section,
                form=form,
                errors=None,
                obj=obj
            )
        # 判断标题是否已经使用
        if obj.title != form.title.data:
            if Post.exists(form.title.data, self.db):
                error_string = '文章标题: {} 已经被使用'.format(form.title.data)
                return self.render(
                    "admin/post/edit.html",
                    section=self._section,
                    form=form,
                    errors=error_string,
                    obj=obj
                )
        # 查询slug是否已经被使用
        # create()有自动处理，但是update()暂定需要修改，所以放在这里处理
        if obj.slug != form.slug.data:
            slug = form.slug.data
            slug_index = 1
            while True:
                if Post.slug_exists(slug, self.db):
                    slug = form.slug.data + "-" + str(slug_index)
                    slug_index += 1
                else:
                    form.slug.data = slug
                    break
        # 图片文件的处理
        if self.request.files.get('image', None):
            # 判断文件类型是否为图片
            file_info = self.request.files['image'][0]
            if 'image' not in file_info['content_type']:
                error_string = '图片: 格式不正确，请传入正确的图片格式'.format(
                    form.title.data
                )
                return self.render(
                    "admin/post/edit.html",
                    section=self._section,
                    form=form,
                    errors=error_string,
                    obj=obj
                )

            # 上传图片
            image_key = str(uuid.uuid4())
            file_io = BytesIO(file_info['body'])
            qiniu_client = QiniuClient(
                self.config.QINIU_ACCESS_KEY,
                self.config.QINIU_SECRET_KEY,
                self.config.QINIU_BUCKET_NAME
            )
            # 使用线程池进行非堵塞上传
            upload_result = yield self.thread_pool.submit(
                qiniu_client.upload_file, image_key, file_io
            )
            if upload_result['error'] is True:
                error_string = '图片上传失败'
                self.application.logger.error(
                    "图片上传失败：{}".format(upload_result['exception'])
                )
                return self.render(
                    "admin/post/edit.html",
                    section=self._section,
                    form=form,
                    errors=error_string,
                    obj=obj
                )
            image_obj = Image.create(
                self.db,
                key=image_key,
                name=file_info['filename'],
                url=urljoin(self.config.QINIU_DOMAIN, image_key)
            )
            form.image.data = image_obj  # 共享一个变量，可以应对没有上传图片的情况

        Post.update(
            self.db,
            obj,
            patch=False,
            category_id=form.category_id.data,
            title=form.title.data,
            slug=form.slug.data,
            brief=form.brief.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            status=form.status.data,
            publish_time=form.publish_time.data,
            content=form.content.data,
            type=form.type.data,
        )
        # collection的处理
        if not form.collection.data:
            obj.collection = None
        else:
            if ((not obj.collection) or
                 (obj.collection and
                          obj.collection.name != form.collection.data)):
                collection = PostCollection.get_object_by_name(
                    form.collection.data, self.db
                )
                if not collection:
                    collection = PostCollection.create(
                        self.db,
                        name=form.collection.data
                    )
                obj.collection = collection
        # 处理标签
        tags = Tag.create_by_string(self.db, form.tags.data)
        if tags:
            obj.tags = tags
        if isinstance(form.image.data, Image):     # 暂不能删除文章的图片
            obj.image = form.image.data
        self.db.add(obj)
        self.redirect(self.reverse_url("admin:post:list"), permanent=True)

    @web.authenticated
    def delete(self, *args, **kwargs):
        obj = Post.get_object_by_id(self.db, kwargs['id'])
        if not obj:
            return self.write_error(404)
        Post.delete(self.db, obj)
        self.set_status(204)


class SysConfigHandler(BaseHandler):
    """系统配置"""
    _section = 'sys-config'

    @web.authenticated
    def get(self, *args, **kwargs):
        form = SysConfigForm(data={
            "session_expire": SysConfig.get(**SysConfig.session_expire),
            "per_page": SysConfig.get(**SysConfig.per_page),
            "blog_per_page": SysConfig.get(**SysConfig.blog_per_page),
            "cache_enable": SysConfig.get(**SysConfig.cache_enable),
            "cache_expire": SysConfig.get(**SysConfig.cache_expire),
            'template_version': SysConfig.get(**SysConfig.template_version),
            'comment_limit_enable': SysConfig.get(
                                        **SysConfig.comment_limit_enable),
            'comment_limit': SysConfig.get(**SysConfig.comment_limit),
            'template_code_skin': SysConfig.get(**SysConfig.template_code_skin)
        })
        self.render(
            "admin/sys_config/index.html",
            section=self._section,
            form=form,
            errors=None
        )

    @web.authenticated
    def post(self, *args, **kwargs):
        form = SysConfigForm(self.request.arguments)
        if not form.validate():
            return self.render(
                "admin/sys_config/index.html",
                section=self._section,
                form=form,
                errors=None
            )

        for key, value in form.data.items():
            SysConfig.set(key, value, type=type(value))
        # 清空缓存
        self.cache_client.flush_all()
        self.redirect("admin:sys-config")


class ImageListHandler(BaseHandler):
    """图片列表"""
    _section = 'image'

    def prepare(self):
        super(ImageListHandler, self).prepare()
        self._page = self.get_query_argument('page', 1)

    @web.authenticated
    def get(self, *args, **kwargs):
        object_list = Image.get_object_list(self.db)
        data = self.handle_object_list(
            object_list,
            self._page,
            SysConfig.get(**SysConfig.per_page)
        )
        self.render(
            'admin/image/list.html',
            section=self._section,
            data=data
        )


class ImageCreateHandler(BaseHandler):
    """图片创建"""
    _section = 'image'

    @web.authenticated
    def get(self, *args, **kwargs):
        form = ImageForm()
        self.render(
            "admin/image/create.html",
            section=self._section,
            form=form,
            errors=None
        )

    @gen.coroutine
    @web.authenticated
    def post(self, *args, **kwargs):
        form = ImageForm(self.request.arguments)
        file_info = self.request.files['image'][0]
        if 'image' not in file_info['content_type']:
            error_string = '图片: 格式不正确，请传入正确的图片格式'
            return self.render(
                "admin/image/create.html",
                section=self._section,
                form=form,
                errors=error_string,
            )

        # 上传图片
        image_key = str(uuid.uuid4())
        file_io = BytesIO(file_info['body'])
        qiniu_client = QiniuClient(
            self.config.QINIU_ACCESS_KEY,
            self.config.QINIU_SECRET_KEY,
            self.config.QINIU_BUCKET_NAME
        )
        # 使用线程池进行非堵塞上传
        upload_result = yield self.thread_pool.submit(
            qiniu_client.upload_file, image_key, file_io
        )
        if upload_result['error'] is True:
            error_string = '图片上传失败'
            self.application.logger.error(
                "图片上传失败：{}".format(upload_result['exception'])
            )
            return self.render(
                "admin/image/create.html",
                section=self._section,
                form=form,
                errors=error_string,
            )
        image_obj = Image.create(
            self.db,
            key=image_key,
            name=file_info['filename'],
            url=urljoin(self.config.QINIU_DOMAIN, image_key)
        )
        self.redirect(self.reverse_url("admin:image:list"))


class ImageDetailHandler(BaseHandler):
    """图片详情"""
    _section = 'image'

    @web.authenticated
    def get(self, *args, **kwargs):
        pass

    @gen.coroutine
    @web.authenticated
    def post(self, *args, **kwargs):
        pass

    @web.authenticated
    def delete(self, *args, **kwargs):
        pass