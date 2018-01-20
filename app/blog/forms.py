#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime

from wtforms_tornado import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import Email, DataRequired, Regexp


class CommentForm(Form):
    email = StringField(
        "邮箱地址",
        validators=[DataRequired(), Email()],
        render_kw={"required": True}
    )
    title = StringField(
        "标题",
        validators=[DataRequired(), Regexp(r".{,128}")],
        render_kw={
            "required": True,
            "max-length": 128
        }
    )
    content = TextAreaField(
        "内容",
        validators=[DataRequired()],
        render_kw={
            'required': True,
            'rows': 3
        }
    )