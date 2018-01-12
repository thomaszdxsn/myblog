#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from io import BytesIO

from qiniu import Auth, put_data, BucketManager
from qiniu import build_batch_stat, build_batch_delete


class QiniuClient(object):

    def __init__(self, access_key, secret_key, bucket_name):
        self.client = Auth(access_key, secret_key)
        self.bucket_name = bucket_name
        self.bucket = BucketManager(self.client)

    def set_bucket_name(self, bucket_name):
        """重设bucketname"""
        self.bucket_name = bucket_name

    def upload_file(self, filename, file_io=None):
        """上传文件
        接受文件名或者IO形式的数据

        :filename:
            可以是文件系统中的文件路径，也可以直接使用文件名称，
            最后会根据是否带`file_io`参数来决定是否需要读取文件。
        :file_io:
            文件IO对象，如果带有这个参数则直接将其上传。
        :return:
            - error: 是否有错误
            - exception: 错误原因
            - hash: 上传文件的hash
            - key: 上传文件的key
        """
        if file_io is None:
            file_io = BytesIO()
            with open(filename, 'rb') as f:
                file_io.write(f.read())
        filename = filename.rsplit("/")[-1]

        try:
            token = self.client.upload_token(self.bucket_name, filename)
            result, info = put_data(token, filename, file_io.getvalue())
        except Exception as exc:
            return {
                'error': True,
                'exception': str(exc)
            }
        else:
            return {
                "error": info.status_code != 200,
                "exception": info.exception,
                "hash": result.get('hash', None),
                "key": result.get('key', None)
            }

    def file_delete(self, filename):
        """删除指定的文件"""
        try:
            result, info = self.bucket.delete(self.bucket_name, filename)
        except Exception as exc:
            return {
                'error': True,
                'exception': str(exc)
            }
        else:
            return {
                'error': info.status_code != 200,
                'exception': info.exception
            }

    def file_list(self, prefix=None, delimiter=None, marker=None, limit=None):
        """获取文件列表，提供了若干选项供筛选文件

        :param prefix: 前缀
        :param delimiter: 分隔符
        :param marker: 标记
        :param limit: 条目数量
        :return:
            - error: 是否有错误
            - exception: 错误的原因
            - items: 文件数据列表
                - key
                - hash
                - fsize
                - mimeType
                - putTime
                - type
                - status
        """
        try:
            result, info = self.bucket.list(
                                self.bucket_name,
                                prefix,
                                marker,
                                limit,
                                delimiter
                            )
        except Exception as exc:
            return {
                'error': True,
                'exception': str(exc)
            }
        else:
            return {
                'error': info.status_code != 200,
                'exception': info.exception,
                'items': result.get('items', None)
            }

    def stat_info(self, filename):
        """获取文件信息

        :return: 同上
        """
        try:
            result, info = self.bucket.stat(self.bucket_name, filename)
        except Exception as exc:
            return {
                'error': True,
                'exception': str(exc)
            }
        return {
            'error': info.status_code != 200,
            'exception': info.exception,
            'fsize': result.get('fsize', None),
            'hash': result.get('hash', None),
            'mimeType': result.get("mimeType", None),
            'putTime': result.get("putTime", None),
            'type': result.get('type', None)
        }

    def batch_stat(self, filenames):
        """批量获取文件信息

        :return: 同上
        """
        try:
            ops = build_batch_stat(self.bucket_name, filenames)
            result, info = self.bucket.batch(ops)
        except Exception as exc:
            return {
                'error': True,
                'exception': str(exc)
            }
        else:
            return {
                'error': info.status_code != 200,
                'exception': info.exception,
                'items': result.get('items', None)
            }

    def batch_delete(self, filenames):
        """批量删除文件
        """
        try:
            ops = build_batch_delete(self.bucket_name, filenames)
            result, info = self.bucket.batch(ops)
        except Exception as exc:
            return {
                'error': True,
                'exception': str(exc)
            }
        else:
            return {
                'error': info.status_code != 200,
                'exception': info.exception
            }

    def fetch(self, url, filename):
        """抓去网络资源到空间"""
        try:
            result, info = self.bucket.fetch(url, self.bucket_name, filename)
        except Exception as exc:
            return {
                'error': True,
                'exception': str(exc)
            }
        return {
            'error': info.status_code != 200,
            'exception': info.exception
        }


