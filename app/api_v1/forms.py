#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import datetime

from wtforms import (StringField, PasswordField, IntegerField, TextAreaField,
                     DateTimeField, FileField)
from wtforms.validators import DataRequired, Email, Regexp
from wtforms_tornado import Form


class UserCreateForm(Form):
    email = StringField(
        'email',
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        'password',
        validators=[DataRequired(), Regexp(r'^[a-zA-Z]\w{7,31}$')]
    )


class UserLoginForm(Form):
    email = StringField(
        'email',
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        'password',
        validators=[DataRequired(), Regexp(r'^[a-zA-Z]\w{7,31}$')]
    )



class UserUpdateForm(Form):
    email = StringField(
        'email',
        validators=[Email()],
    )


class CategoryForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    parent_id = IntegerField(
        'parent_id'
    )


class PostCreateForm(Form):
    category_id = IntegerField(
        'category_id',
        validators=[DataRequired()]
    )
    image_id = IntegerField(
        'image_id'
    )
    title = StringField(
        'title',
        validators=[DataRequired()]
    )
    slug = StringField(
        'slug',
        validators=[DataRequired()]
    )
    content = TextAreaField(
        'content'
    )
    tags = StringField(
        'tags'
    )
    publish_time = DateTimeField(
        'publish_time',
        validators=[DataRequired()],
        default=datetime.datetime.now()
    )


class PostUpdateForm(Form):
    category_id = IntegerField(
        'category_id',
    )
    image_id = IntegerField(
        'image_id'
    )
    title = StringField(
        'title',
    )
    content = TextAreaField(
        'content'
    )
    tags = StringField(
        'tags'
    )
    publish_time = DateTimeField(
        'publish_time',
        default=datetime.datetime.now()
    )


class CommentCreateForm(Form):
    post_id = IntegerField(
        'post_id',
        validators=[DataRequired()]
    )
    email = StringField(
        'email',
        validators=[DataRequired()]
    )
    title = StringField(
        'title',
        validators=[DataRequired()]
    )
    content = TextAreaField(
        'content',
        validators=[DataRequired()]
    )
    reply_id = IntegerField(
        'reply_id'
    )


class CommentUpdateForm(Form):
    post_id = IntegerField(
        'post_id',
    )
    email = StringField(
        'email',
    )
    title = StringField(
        'title',
    )
    content = TextAreaField(
        'content',
    )
    reply_id = IntegerField(
        'reply_id'
    )


class TagForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )


class ImageCreateForm(Form):
    file = FileField(
        'file',
        validators=[DataRequired()]
    )

