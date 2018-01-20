#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import datetime

import arrow

from .base import redis_cli
from ..libs.utils import get_next_weekday


class SiteStats(object):
    """网站的数据统计/分析"""
    _prefix = '_stats'
    access_ip = "_stats:access:ip"
    access_ip_day = "_stats:access:ip:{day}"
    pv_amount = "_stats:pv:amount"
    pv_day = "_stats:pv:{day}"
    uv_amount = "_stats:uv:amount"
    uv_day = "_stats:uv:{day}"
    ua_day = "_stats:access:ua:{day}"

    @classmethod
    def generate_key(cls, key):
        """生成加入前缀的KEY"""
        return "{0}:{1}".format(cls._prefix, key)

    @classmethod
    def incr_post_view(cls, slug):
        """增加某post的点击量

        TODO: 在post更改slug以后也要修改这个REDIS键
        """
        redis_key = cls.generate_key(slug)
        redis_cli.incr(redis_key, 1)

    @classmethod
    def get_post_view(cls, slug):
        """获取某post的点击量"""
        redis_key = cls.generate_key(slug)
        value = redis_cli.get(redis_key)
        if value is None:
            return 0
        return int(value)

    @classmethod
    def save_access_ip(cls, ip):
        """建立一个集合类型来存储访问者的IP

        另外每天建立一个集合来存储当天访问的IP，但是只保存一周(下周一刷新)
        """
        redis_cli.sadd(cls.access_ip, ip)

        today = datetime.date.today()
        day_redis_key = cls.access_ip_day.format(day=str(today))
        redis_cli.sadd(day_redis_key, ip)

        # 过期时间(下周一)
        next_monday_timestamp = arrow.get(
            get_next_weekday(today, 1)
        ).timestamp
        redis_cli.expireat(day_redis_key, next_monday_timestamp)

    @classmethod
    def get_access_ip(cls):
        """获取访问者IP"""
        # TODO

    @classmethod
    def incr_pv(cls):
        """增加pv(page-view)数据，默认会增加pv总量和每日的pv"""
        # 总PV
        redis_cli.incr(cls.pv_amount, 1)

        # 日PV
        pv_day_key = cls.pv_day.format(day=str(datetime.date.today()))
        redis_cli.incr(pv_day_key)

    @classmethod
    def get_pv(cls, date=None):
        """获取pv数据

        :param date:

            date对象，或者"%Y-%m-%d"格式的字符串

            可选。如果提供了，则返回改天的pv数据

        :return:

            pv数据，或者None
        """
        if date is None:
            redis_key = cls.pv_amount
        else:
            redis_key = cls.pv_day.format(str(date))

        value = redis_cli.get(redis_key)
        return value

    @classmethod
    def incr_uv(cls, ip):
        """增量UV数据

        UV = 'unique visitor'，即独立访问者.

        我们会根据IP是否已经访问过本站来统计这个UV数据.
        """
        today = datetime.date.today()
        day_ip_key = cls.access_ip_day.format(day=str(today))
        if not redis_cli.sismember(day_ip_key, ip):
            day_uv_key = cls.uv_day.format(day=str(today))
            redis_cli.incr(day_uv_key, 1)
        if not redis_cli.sismember(cls.access_ip, ip):
            redis_cli.incr(cls.uv_amount, 1)

    @classmethod
    def save_access_ua(cls, ua, ip):
        """存储ua信息，默认保留一个星期(每周7更新)，同一个IP每天只保存一个UA"""
        today = datetime.date.today()
        day_ip_key = cls.access_ip_day.format(day=str(today))
        if not redis_cli.sismember(day_ip_key, ip):
            redis_key = cls.ua_day.format(day=str(today))
            redis_cli.lpush(redis_key, ua)

            # 设置在下周一过期
            next_monday_timestamp = arrow.get(
                get_next_weekday(datetime.date.today(), 1)
            ).timestamp
            redis_cli.expireat(redis_key, next_monday_timestamp)

    @classmethod
    def get_access_ua(cls, date):
        redis_key = cls.ua_day.format(str(date))
        # TODO

