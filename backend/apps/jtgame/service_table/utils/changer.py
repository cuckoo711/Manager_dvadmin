"""
Creation date: 2024/10/21
Creation Time: 上午9:52
DIR PATH: backend/jtgame/service_table/utils
Project Name: Manager_dvadmin
FILE NAME: changer.py
Editor: 30386
"""
import os
import subprocess
from datetime import datetime


class Changer:
    @staticmethod
    def change_xls_to_xlsx(file_name: str):
        if not os.path.exists(file_name):
            return
        if not file_name.endswith('.xls'):
            return

        file_name = os.path.abspath(file_name)
        new_name = os.path.splitext(file_name)[0] + '.xlsx'

        # 使用libreoffice命令行工具将xls转换为xlsx
        try:
            command = [
                'libreoffice', '--headless', '--convert-to', 'xlsx', file_name, '--outdir', os.path.dirname(file_name)
            ]
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.stderr.decode()}")
            return None

        return new_name

    @staticmethod
    def change_xlsx_to_xls(file_name: str):
        if not os.path.exists(file_name):
            return
        if not file_name.endswith('.xlsx'):
            return

        file_name = os.path.abspath(file_name)
        new_name = os.path.splitext(file_name)[0] + '.xls'

        try:
            command = [
                'libreoffice', '--headless', '--convert-to', 'xls', file_name, '--outdir', os.path.dirname(file_name)
            ]
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.stderr.decode()}")
            return None

        return new_name

    @staticmethod
    def str_to_datetime(date_str):
        # 实现日期字符串到datetime的转换
        formats = ['%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Date format for {date_str} not recognized.")

    @staticmethod
    def str_to_date(date_str):
        formats = ['%Y/%m/%d', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Date format for {date_str} not recognized.")

    @staticmethod
    def str_to_time(date_str):
        formats = ['%H:%M', '%H:%M:%S']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).time()
            except ValueError:
                continue
        raise ValueError(f"Time format for {date_str} not recognized.")

    @staticmethod
    def datetime_to_float(date_time: datetime):
        # 转成excel时间戳
        return (date_time - datetime(1899, 12, 30)).total_seconds() / 86400.0

    @staticmethod
    def init_df(df):
        df = df.dropna(how='all')
        df[df.columns[1]] = df.iloc[:, 1].apply(Changer.str_to_date)
        df[df.columns[2]] = df.iloc[:, 2].apply(Changer.str_to_time)
        df[df.columns[3]] = df.iloc[:, 3].apply(Changer.str_to_datetime)
        df['timestamp'] = df.iloc[:, 3].apply(Changer.datetime_to_float)
        return df
