"""
Creation Date: 2025/3/2
Creation Time: 上午12:49
Dir Path: backend/apps/jtgame/authorization
Project Name: Manager_dvadmin_my
File Name: utils.py
Editor: cuckoo
"""
import base64
import hashlib
import json
import os
import shutil
import sqlite3
import time
from typing import Any, Dict

import requests

from apps.jtgame.authorization.models import AuthorizationConfig


class ZFileDB:
    def __init__(self, db_path: str):
        """
        初始化数据库连接
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        上下文管理器的进入方法，建立数据库连接
        """
        self.conn = sqlite3.connect(self.db_path)  # 连接到数据库
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        上下文管理器的退出方法，关闭数据库连接
        """
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def insert_data(self, table_name: str, data: Dict[str, Any]):
        """
        插入数据
        :param table_name: 表名
        :param data: 插入的数据，字典形式，键为列名
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_data(self, table_name: str, data: Dict[str, Any], condition: str):
        """
        更新数据
        :param table_name: 表名
        :param data: 更新的数据，字典形式，键为列名
        :param condition: 条件，用于指定更新哪些记录
        """
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_data(self, table_name: str, condition: str):
        """
        删除数据
        :param table_name: 表名
        :param condition: 条件，用于指定删除哪些记录
        """
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query)
        self.conn.commit()

    def query_data(self, table_name: str, columns=None, condition: str = None):
        """
        查询数据
        :param table_name: 表名
        :param columns: 查询的列，默认为所有列
        :param condition: 查询条件
        :return: 查询结果
        """
        if columns is None:
            columns = ['*']
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query)
        return self.cursor.fetchall()


class zfile_func:
    def __init__(self):
        db_path: AuthorizationConfig = AuthorizationConfig.objects.filter(key='zfile_db').first()
        if not db_path:
            raise Exception('未找到数据库路径配置')
        if not os.path.exists(db_path.value):
            raise Exception('数据库文件不存在')
        self.db_path: str = db_path.value

    def create_user(self, username: str):
        with ZFileDB(self.db_path) as db:
            # 先查询用户是否存在
            user = db.query_data('user', ['username'], f"username = '{username}'")
            if user:
                raise Exception('用户已存在')

            # 插入用户
            timestamp = int(time.time())
            db.insert_data('user', {
                'username': username,
                'nickname': username,
                'password': 'c5df76d5ab97aac51b3712c1408890b3',  # 默认密码为：admin123456
                'enabled': 1,
                'create_time': timestamp,
                'update_time': timestamp,
                'default_permissions': 'preview,download,upload,rename,ignoreHidden,newFolder,copy,ignorePassword,generateShortLink,delete',
                'salt': 'ad868c042affc1ba9971feaf4b81cfbc'
            })
            new_user = db.query_data('user', ['id'], f"username = '{username}'")

            # 添加用户权限
            db.insert_data('user_storage_source', {
                'user_id': new_user[0][0],
                'storage_source_id': 1,
                'root_path': '/',
                'enable': 1,
                'permissions': 'preview,download,upload,rename,ignoreHidden,newFolder,copy,ignorePassword,generateShortLink,delete',
            })

    def delete_user(self, username: str):
        with ZFileDB(self.db_path) as db:
            # 先查询用户是否存在
            user = db.query_data('user', ['id'], f"username = '{username}'")
            if not user:
                raise Exception('用户不存在')

            # 删除用户
            db.delete_data('user_storage_source', f"user_id = {user[0][0]}")
            db.delete_data('user', f"username = '{username}'")

    def change_username(self, old_username: str, new_username: str):
        with ZFileDB(self.db_path) as db:
            # 先查询用户是否存在
            user = db.query_data('user', ['id'], f"username = '{old_username}'")
            if not user:
                raise Exception('用户不存在')

            # 修改用户名
            db.update_data('user', {
                'username': new_username,
                'nickname': new_username,
            }, f"username = '{old_username}'")


class WeChatBot:
    def __init__(self, webhook_key):
        self.webhook_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}'
        self.upload_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={webhook_key}&type=file'
        self.max_file_size = 20 * 1024 * 1024  # 20 MB
        self.zip_file = None

    def send_text(self, content, mentioned_list=None, mentioned_mobile_list=None):
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
            }
        }
        if mentioned_list:
            data['text']['mentioned_list'] = mentioned_list
        if mentioned_mobile_list:
            data['text']['mentioned_mobile_list'] = mentioned_mobile_list
        self._post_request(data)

    def send_markdown(self, content):
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        self._post_request(data)

    def send_image(self, image_path):
        with open(image_path, 'rb') as f:
            image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        md5_hash = hashlib.md5(image_data).hexdigest()
        data = {
            "msgtype": "image",
            "image": {
                "base64": base64_data,
                "md5": md5_hash
            }
        }
        self._post_request(data)

    def send_file(self, file_path):
        if not os.path.isdir(file_path) and file_path.endswith('.zip'):
            self.zip_file = file_path
        else:
            self.zip_file = self._handle_directory(file_path)
        if os.path.isdir(file_path):
            if os.path.getsize(self.zip_file) > self.max_file_size:
                file_paths = self._split_and_zip(file_path)
                for file in file_paths:
                    self._upload_file(file)
            else:
                self._upload_file(self.zip_file)
        elif os.path.getsize(file_path) > self.max_file_size:
            raise ValueError(f'File size exceeds the limit of {self.max_file_size} bytes.')
        else:
            self._upload_file(file_path)

    @staticmethod
    def _handle_directory(dir_path):
        return shutil.make_archive(dir_path, 'zip', dir_path)

    @staticmethod
    def _split_and_zip(dir_path) -> list[str]:
        files = os.listdir(dir_path)
        dir_name = os.path.basename(dir_path)

        mid_point = len(files) // 2
        sub_dirs = [files[:mid_point], files[mid_point:]]
        zip_paths = []
        for idx, sub_files in enumerate(sub_dirs):
            sub_dir = os.path.join(dir_path, f'{dir_name}_{idx}')
            os.makedirs(sub_dir, exist_ok=True)
            for file in sub_files:
                shutil.move(os.path.join(dir_path, file), sub_dir)
            zip_path = shutil.make_archive(sub_dir, 'zip', sub_dir)
            zip_paths.append(zip_path)
            shutil.rmtree(sub_dir)
        return zip_paths

    def _upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(self.upload_url, files=files)
        if response.status_code == 200 and response.json().get('errcode') == 0:
            media_id = response.json().get('media_id')
            self._send_file_message(media_id)
        else:
            raise ValueError(f'File upload failed: {response.text}')

    def _send_file_message(self, media_id):
        data = {
            "msgtype": "file",
            "file": {
                "media_id": media_id
            }
        }
        self._post_request(data)

    def _post_request(self, data):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.webhook_url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise ValueError(f'Failed to send message: {response.text}')
