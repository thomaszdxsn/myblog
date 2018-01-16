#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime

from wtforms_tornado import Form
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     FileField, DateTimeField, BooleanField)
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
        render_kw={"rows": 30}
    )
