#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime

from wtforms_tornado import Form
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     FileField, DateTimeField, BooleanField, IntegerField)
from wtforms.validators import Email, Regexp, DataRequired


class LoginForm(Form):
    email = StringField(
        'email',
        validators=[
            DataRequired(message='email:这个字段是必填项'),
            Email(message='email:请输入合法的邮箱地址')
        ],
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码:这个字段是必填项'),
            Regexp(r'^[a-zA-Z]\w{7,31}$',
                   message='合法的密码为:首字符为字母，长度为8-32位')
        ]
    )


class CategoryForm(Form):
    parent_id = SelectField(
        "父级分类",
        choices=[(0, '---')],
        coerce=int
    )
    name = StringField(
        '分类名称',
        validators=[
            DataRequired(message="分类名称：这个字段是必填项")
        ],
        render_kw={"required": True}
    )


class PostForm(Form):
    category_id = SelectField(
        "文章分类",
        validators=[
            DataRequired(message="文章分类：这个字段是必填项")
        ],
        render_kw={"required": True},
        coerce=int
    )
    type = SelectField(
        "文章类型",
        choices=[
            ("origin", "原创"),
            ("reproduce", "转载"),
            ("translation", "翻译")
        ]
    )
    title = StringField(
        "文章标题",
        validators=[
            DataRequired(message='文章标题: 这个字段是必填项')
        ],
        render_kw={"required": True}
    )
    slug = StringField(
        "slug",
        validators=[
            DataRequired(message='slug: 这个字段是必填项')
        ],
        render_kw={"required": True}
    )
    meta_description = StringField(
        'meta_description'
    )
    meta_keywords = StringField(
        'meta_keywords'
    )
    brief = TextAreaField(
        '简介',
    )
    collection = StringField(
        "文章集合"
    )
    tags = StringField(
        '标签'
    )
    status = BooleanField(
        '状态',
        default=True,
    )
    publish_time = DateTimeField(
        '发布时间',
        default=datetime.now()
    )
    image = FileField(
        '图片'
    )
    content = TextAreaField(
        "内容",
        render_kw={"rows": 30, "required": True}
    )


class ImageForm(Form):
    image = FileField(
        "图片"
    )


class SysConfigForm(Form):
    template_version = SelectField(
        "模版版本",
        choices=[
            ('blog_startbootstrap', 'startbootstrap'),
            ('blog_von', "von")
        ]
    )
    template_code_skin = SelectField(
        "代码块皮肤",
        choices=[
            ('sons-of-obsidian', 'sons-of-obsidian'),
            ('sunburst', 'sunburst'),
            ('doxy', 'doxy'),
            ('desert', 'desert')
        ]
    )
    per_page = IntegerField(
        "分页时每页的条目数量(后台和API)",
        validators=[DataRequired()]
    )
    blog_per_page = IntegerField(
        "博客中每页显示的条目数量",
        validators=[DataRequired()]
    )
    cache_enable = BooleanField(
        "是否开启缓存",
    )
    cache_expire = IntegerField(
        "缓存过期时间(单位:秒)",
        validators=[DataRequired()]
    )
    session_expire = IntegerField(
        "session过期时间(单位:秒)",
        validators=[DataRequired()]
    )
    comment_limit_enable = BooleanField(
        "是否开启评论限制",
    )
    comment_limit = IntegerField(
        "评论限制数量(条/每分钟)",
        validators=[DataRequired()]
    )




