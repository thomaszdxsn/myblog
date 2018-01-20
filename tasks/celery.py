#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from celery import Celery

from config import CommonConfig

if CommonConfig.REDIS_PASSWORD:
    redis_uri = "redis://:{password}@{hostname}:{port}/{db_number}".format(
        password=CommonConfig.REDIS_PASSWORD,
        hostname=CommonConfig.REDIS_HOST,
        port=CommonConfig.REDIS_PORT,
        db_number=1
    )
else:
    redis_uri = "redis://{hostname}:{port}/{db_number}".format(
        hostname=CommonConfig.REDIS_HOST,
        port=CommonConfig.REDIS_PORT,
        db_number=1
    )


app = Celery(
    'tasks',
    broker=redis_uri,
    backend=redis_uri,
    include=['tasks.cron']
)

# 周期性任务的规划
app.conf.beat_schedule = {
    # 每10分钟同步一次post点击量(Redis -> MySQL)
    'every-10-minute-sync_post_view_data': {
        'task': 'tasks.cron.sync_post_view',
        'schedule': 600.0,
    }
}



if __name__ == '__main__':
    app.start()