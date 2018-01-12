#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""这个模块用来定义命令行接口.包括服务器的启动，部署，数据库的操作等等"""

import argparse
import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line

from app import create_app
from config import config_dict


parser = argparse.ArgumentParser()
sub_parser = parser.add_subparsers(help='subcommands')

# 服务器启动的子命令
server_parser = sub_parser.add_parser(
    'start',
    help='about server start, include "dev|test|prod" start mode, '
         'default is dev mode'
)
server_parser.add_argument(
    '-m', '--start-mode',
    dest='start_mode',
    choices=['dev', 'test', 'prod'],
    default='dev',
    help='mode for server start'
)
server_parser.add_argument(
    '--host',
    dest='server_host',
    default='127.0.0.1',
    help='host for server start'
)
server_parser.add_argument(
    '--port',
    dest='server_port',
    default=8000,
    help='port for server start'

)

# 数据库操作的子命令
db_parser = sub_parser.add_parser(
    'db',
    help='about db operation'
)
db_parser.add_argument(
    'db_command',
    choices=['makemigrations', 'migrate'],
    help='make database migrations file'
)
db_parser.add_argument(
    '-m', '--comment',
    dest='comment',
    help='alembic migrations comment text'
)
db_parser.add_argument(
    '--db_mode',
    choices=['dev', 'test', 'prod'],
    default='dev',
    help='database configure mode, default is dev(development mode)'
)


def db_operation(args):
    """数据库操作命令

    首先根据模式来决定使用的数据库
    """
    # 根据模式设置环境变量
    config_cls = config_dict[args.db_mode]
    os.environ['SA_ENGINE_STRING'] = config_cls.SQLALCHEMY_URI

    if args.db_command == 'makemigrations':
        alembic_command = 'alembic revision --autogenerate'
        if args.comment:
            alembic_command += (' -m' + '"' + args.comment + '"')
        os.system(alembic_command)
    elif args.db_command == 'migrate':
        alembic_command = 'alembic upgrade head'
        os.system(alembic_command)


def start_server(args):
    """启动服务器

    :param args.start_mode:

        指定服务器开始的模式，包括dev, test, prod.
        分别对应"开发","测试"和“产品”配置环境.

    :param args.server_host: 服务器启动所使用的host
    :param args.server_port: 服务器启动所使用的port
    """
    start_mode = args.start_mode
    app = create_app(start_mode)
    http_server = HTTPServer(app, xheaders=True)
    http_server.bind(args.server_port, args.server_host)
    http_server.start()
    # 打印启动提示日志
    parse_command_line()
    app.logger.info('server start at {0}:{1}'.format(
        args.server_host, args.server_port
    ))
    IOLoop.current().start()


def main(args):
    if getattr(args, 'start_mode', None):
        # 触发服务器启动的函数
        start_server(args)
    if getattr(args, 'db_command', None):
        db_operation(args)
    if getattr(args, 'start_mode'):
        # 触发服务器启动的函数
        start_server(args)



if __name__ == '__main__':
    args = parser.parse_args()
    main(args)