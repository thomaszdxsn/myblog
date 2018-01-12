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
                "hash": result['hash'],
                "key": result['key']
            }

    def list_file(self, prefix=None, delimiter=None, marker=None, limit=None):
        """获取文件列表，提供了若干选项供筛选文件

        :param prefix: 前缀
        :param delimiter: 分隔符
        :param marker: 标记
        :param limit: 条目数量
        :return:
            - error: 是否有错误
            - exception: 错误的原因
        """
        try:
            result = self.bucket.list(
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
        return result

    def stat_info(self, filename):
        """获取文件信息"""
        result = self.bucket.stat(self.bucket_name, filename)
        return result

    def batch_stat(self, filenames):
        """批量获取文件信息"""
        ops = build_batch_stat(self.bucket_name, filenames)
        result = self.bucket.batch(ops)
        return result

    def batch_delete(self, filenames):
        ops = build_batch_delete(self.bucket_name, filenames)
        result = self.bucket.batch(ops)
        return result

    def fetch(self, url, filename):
        """抓去网络资源到空间"""
        result = self.bucket.fetch(url, self.bucket_name, filename)
        return result

client = QiniuClient("YGJZitPcvDcFywBpdd822E-Piw5ZGHHmj_SfI3PE",
                     "fK7u4oXhG-YLRBjkhxgTAclL2V9E3omt50unJmCu",
                     'myblog')

result = client.list_file()


