#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
用户-角色-权限相关的表
"""
import string
import secrets
import hashlib
from datetime import datetime

from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        bindparam)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base, sql_bakery, ModelAPIMixin


__all__ = ['User', 'Role', 'Permission', 'UserRole', 'RolePermission']


class User(ModelAPIMixin, Base):
    """用户表"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(32), index=True, nullable=False, unique=True)
    encrypt_password = Column(String(64))
    salt = Column(String(8))
    created_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, onupdate=datetime.now)

    user_roles = relationship('UserRole',
                              cascade='all, delete-orphan',
                              backref='user')
    # 使用sqlalchemy的association_proxy技术
    roles = association_proxy('user_roles', 'role')

    def __init__(self, email, password, roles=None, user_roles=None):
        self.email = email
        self.password = str(password)
        if user_roles:
            self.user_roles = user_roles
        if roles:
            self.roles = roles

    # password相关方法, property
    @hybrid_property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, value):
        self.encrypt_password, self.salt = self.generate_password(value)

    @staticmethod
    def generate_password(value, salt=None):
        """使用盐值salt将密码加密(sha256)并存储"""
        if not salt:
            alphabet = string.ascii_letters + string.digits
            salt = "".join(secrets.choice(alphabet) for _ in range(8))
        password = (salt + value).encode()
        secret_password = hashlib.sha256(password).hexdigest()
        return secret_password, salt

    def verify_password(self, password):
        """检查密码是否一致"""
        encrypt_password = self.generate_password(password, self.salt)[0]
        return self.encrypt_password == encrypt_password

    @staticmethod
    def exists(email, session):
        """检查该用户邮箱是否已经存在.

        这里使用了sqlalchemy.ext.baked.bakery，
        这个特性可以缓存编译后的sql语句，然后再将变量值插入到缓存语句中。
        """
        exists_query = sql_bakery(
            lambda session: session.query(User.id)
        )
        exists_query += lambda q: q.filter(User.email == bindparam('email'))
        result = exists_query(session).params(email=email).scalar()
        return result is not None


class Role(Base):
    """角色表"""
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True, nullable=False)
    description = Column(String(512))
    created_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, onupdate=datetime.now)

    role_permissions = relationship('RolePermission',
                                    cascade='all,delete-orphan',
                                    backref='role')
    permissions = association_proxy('role_permissions', 'permission')


class UserRole(Base):
    __tablename__ = 'user_role'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    created_time = Column(DateTime, default=datetime.now)

    role = relationship(Role, lazy='joined')

    def __init__(self, role):
        self.role = role


class Permission(Base):
    """权限表"""
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True, nullable=False)
    operate = Column(String(16), index=True)
    description = Column(String(512))
    created_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, onupdate=datetime.now)


class RolePermission(Base):
    __tablename__ = 'role_permission'

    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permission.id'),
                           primary_key=True)
    created_time = Column(DateTime, default=datetime.now)

    permission = relationship(Permission, lazy='joined')

    def __init__(self, permission):
        self.permission = permission