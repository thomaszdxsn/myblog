#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""博客页面的handlers"""
from tornado import web

from sqlalchemy import func

from ..base.handlers import BaseHandler
from ..models.post import Post, Category, PostTag, Tag, Comment
from ..models.sys_config import SysConfig
from .forms import CommentForm


class HomepageHandler(BaseHandler):
    """首页"""

    def prepare(self):
        super(HomepageHandler, self).prepare()
        self._page_num = self.get_query_argument('page', 1)
        self._tag_id = self.get_query_argument('tag', None)
        self._category_id = self.get_query_argument('category', None)
        self._archive_month = self.get_query_argument('month', None)

    def handle_object_list(self, object_list, page_num,
                           per_page, to_json=False):
        """筛选文章列表"""
        if self._tag_id:
            object_list = object_list.join(PostTag).filter(
                PostTag.tag_id == self._tag_id
            )
        if self._category_id:
            object_list = object_list.filter_by(
                category_id=self._category_id
            )
        if self._archive_month:
            object_list = object_list.filter(
                func.DATE_FORMAT(Post.publish_time, "%Y%m") == self._archive_month
            )
        return super(HomepageHandler, self).handle_object_list(
            object_list, page_num, per_page, to_json
        )

    def get(self, *args, **kwargs):
        """

        context变量介绍:

        :param archive_info(list):

            归档信息: (月份，该月发布的文章数量)，倒序排列(最近的日期在前)

        :param tag_data(ResultList):

            标签数据：标签对象列表

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
        tag_data = Tag.get_object_list(self.db, have_post=True)
        category_data = Category.get_object_list(self.db)
        archive_info = Post.get_archive_month(self.db)
        self.render(
            "homepage.html",
            post_data=post_data,
            category_data=category_data,
            archive_info=archive_info,
            tag_data=tag_data,
            code_skin=SysConfig.get(**SysConfig.template_code_skin)
        )


class PostHandler(BaseHandler):
    """文章详情"""
    
    def prepare(self):
        # TODO: 统计文章的点击量
        print(self.path_kwargs)
        super(PostHandler, self).prepare()

    def get(self, *args, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            return self.write_error(404)
        post_obj = Post.get_object_by_slug(self.db, slug)
        if not post_obj:
            return self.write_error(404)

        tag_data = Tag.get_object_list(self.db, have_post=True)
        category_data = Category.get_object_list(self.db)
        archive_info = Post.get_archive_month(self.db)
        form = CommentForm()
        self.render(
            "post.html",
            post_obj=post_obj,
            tag_data=tag_data,
            category_data=category_data,
            archive_info=archive_info,
            form=form,
            errors=None,
            code_skin=SysConfig.get(**SysConfig.template_code_skin)
        )

    def post(self, *args, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            return self.write_error(404)
        post_obj = Post.get_object_by_slug(self.db, slug)
        if not post_obj:
            return self.write_error(404)

        # 验证表单
        form = CommentForm(self.request.arguments)
        if not form.validate():
            tag_data = Tag.get_object_list(self.db, have_post=True)
            category_data = Category.get_object_list(self.db)
            archive_info = Post.get_archive_month(self.db)
            return self.render(
                "post.html",
                post_obj=post_obj,
                tag_data=tag_data,
                category_data=category_data,
                archive_info=archive_info,
                form=form,
                errors=None,
                code_skin=SysConfig.get(**SysConfig.template_code_skin)
            )

        # 判断该IP是否收到评论限制
        if Comment.comment_restricted(self.request.remote_ip) is True:
            errors='您的IP受到评论限制，请联系管理员'
            tag_data = Tag.get_object_list(self.db, have_post=True)
            category_data = Category.get_object_list(self.db)
            archive_info = Post.get_archive_month(self.db)
            return self.render(
                "post.html",
                post_obj=post_obj,
                tag_data=tag_data,
                category_data=category_data,
                archive_info=archive_info,
                form=form,
                errors=errors,
                code_skin=SysConfig.get(**SysConfig.template_code_skin)
            )

        # 创建评论
        floor = len(post_obj.comment_set) + 1
        Comment.create(
            self.db,
            email=form.email.data,
            title=form.title.data,
            content=form.content.data,
            remote_ip=self.request.remote_ip,
            floor=floor,
            post_id=post_obj.id,
            code_skin=SysConfig.get(**SysConfig.template_code_skin)
        )

        self.redirect(self.reverse_url("post", slug))

    def put(self, *args, **kwargs):
        """将评论转为"开启"状态"""
        if not self.current_user:
            return self.write_error(401)
        if not self.current_user.is_superuser:
            return self.write_error(403)
        comment_obj = Comment.get_object_by_id(self.db,
                                               self.json_body['comment_id'])
        if not comment_obj:
            return self.write_error(404)
        Comment.update(
            self.db,
            comment_obj,
            status=True
        )
        self.set_status(201)

    def delete(self, *args, **kwargs):
        """将评论转为"关闭"状态"""
        if not self.current_user:
            return self.write_error(401)
        if not self.current_user.is_superuser:
            return self.write_error(403)
        comment_obj = Comment.get_object_by_id(self.db,
                                               self.json_body['comment_id'])
        if not comment_obj:
            return self.write_error(404)
        Comment.update(
            self.db,
            comment_obj,
            status=False
        )
        self.set_status(204)