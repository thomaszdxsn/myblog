#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from wtforms import StringField, PasswordField
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