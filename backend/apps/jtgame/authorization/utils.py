"""
Creation Date: 2025/3/2
Creation Time: 上午12:49
Dir Path: backend/apps/jtgame/authorization
Project Name: Manager_dvadmin_my
File Name: utils.py
Editor: cuckoo
"""
import os
import sqlite3
import time
from typing import Dict, Any

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
