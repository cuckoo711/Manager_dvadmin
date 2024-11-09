"""
Creation date: 2024/7/18
Creation Time: 上午11:01
DIR PATH: backend/jtgame/authorization
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
import json
import os
from datetime import timedelta

import requests

from application.celery import app
from apps.jtgame.authorization.models import AuthorizationConfig, AuthorizationInfo, AuthorizationLetter, Notice
from dvadmin.system.views.message_center import MessageCenterCreateSerializer
from dvadmin.utils.backends import logger


@app.task
def generate_authorization_letter(obj_id):
    obj = AuthorizationLetter.objects.get(pk=obj_id)
    obj: AuthorizationLetter

    try:
        bh_name = obj.name
        su_name = ''
        if '（' in bh_name:
            bh_name = obj.name.split('（')[0]
            su_name = obj.name.split('（')[1].split('）')[0]

        authorization_obj = AuthorizationInfo.objects.filter(name=bh_name).first()
        if not authorization_obj:
            raise Exception('未找到对应的版号信息')
        authorization_obj: AuthorizationInfo

        config_objs = AuthorizationConfig.objects.all()
        if not config_objs:
            raise Exception('未找到配置信息')

        dir_path = config_objs.filter(key='authorization_dir_path').first()
        if not dir_path:
            raise Exception('未找到授权书模板的路径配置')
        dir_path = json.loads(dir_path.value).get(authorization_obj.entity, None)
        if not dir_path:
            raise Exception('未找到对应主体的模板的存放路径')

        webhook_key = config_objs.filter(key='authorization_webhook_key').first()
        if not webhook_key:
            raise Exception('未找到发送通知的webhook_key配置')
        webhook_key = webhook_key.value
        authorization_end_date = authorization_obj.authorization_end_date
        if authorization_end_date < obj.release_date + timedelta(days=90):
            msg = f'授权书有效期不足90天, 请及时更新授权书, 授权书有效期至{authorization_end_date}'
            message_data = {
                'title': f'{authorization_obj.name}授权书有效期不足90天',
                'content': msg,
                'target_type': 1,
                'target_role': [8],
            }
            serializer = MessageCenterCreateSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()
        elif authorization_end_date > obj.release_date + timedelta(days=365):
            authorization_end_date = obj.release_date + timedelta(days=365)

        data = {
            'webhook_key': str(webhook_key),
            'file_name': str(obj.name),
            'dir_path': str(dir_path),
            'replacement_dict': {
                '彡': str(obj.name),
                '亇': str(bh_name),
                '⺧': str(authorization_obj.publisher),
                '丷': str(authorization_obj.software_registration_number),
                '⺌': str(authorization_obj.isbn),
                '艹': str(authorization_obj.publication_approval_number),
                '冖': str(obj.release_date.strftime('%Y年%m月%d日')),
                '宀': str(authorization_end_date.strftime('%Y年%m月%d日')),
                '亠': str(obj.release_date.strftime('%Y年%m月%d日')),
                '⻗': str(obj.release_date.strftime('%Y年%m月%d日')),
                '⺋': str(bh_name),
                '彐': str(su_name),
                '⺈': str(authorization_obj.icp_license)
            }
        }
        message_data = {
            'title': f'{obj.name}授权书生成',
            'content': f'授权书正在生成中, 请稍后查看',
            'target_type': 0,
            'target_user': [obj.creator.id],
        }
        serializer = MessageCenterCreateSerializer(data=message_data)
        if serializer.is_valid():
            serializer.save()

        result = requests.post('http://localhost:5020/build', json=data).json()
        if result.get('error'):
            obj.tips = result.get('error')
            if result.get('zip_file'):
                obj.status = 4
                obj.authorization_filepath = result.get('zip_file')
                obj.tips = '生成成功, 但发送失败'
            else:
                obj.status = 3
        else:
            obj.authorization_filepath = result.get('zip_file')
            obj.tips = '生成成功'
            obj.status = 1
        obj.save()
    except Exception as e:
        obj.tips = str(e)
        obj.status = 3
        obj.save()
        raise e


@app.task
def generate_notice(obj_id):
    obj = Notice.objects.get(pk=obj_id)
    obj: Notice

    try:
        config_objs = AuthorizationConfig.objects.all()
        if not config_objs:
            raise Exception('未找到配置信息')

        dir_path = config_objs.filter(key='notice_dir_path').first()
        if not dir_path:
            raise Exception('未找到通知模板的路径配置')
        webhook_key = config_objs.filter(key='notice_webhook_key').first()
        if not webhook_key:
            raise Exception('未找到发送通知的webhook_key配置')
        at_users = config_objs.filter(key='notice_at_users').first()
        if not at_users:
            raise Exception('未找到通知@的用户配置')

        games = obj.games.all()
        game_names = [game.name for game in games]
        data = {
            'game_names': game_names,
            'base_date': obj.build_date.strftime('%Y-%m-%d'),
            'template_path': dir_path.value,
            'build_type': obj.build_type,
            'webhook_key': webhook_key.value,
            'at_users': json.loads(at_users.value)
        }
        logger.info(f'data: {data}')
        result = requests.post('http://localhost:5021/build', json=data).json()
        logger.info(f'result: {result}')
        if result.get('error'):
            obj.tips = result.get('error')
            obj.status = 3
        else:
            obj.tips = '生成成功'
            obj.status = 1
            obj.notice_filepath = result.get('zip_file')
        obj.save()
        return result
    except Exception as e:
        obj.tips = str(e)
        obj.status = 3
        obj.save()
        raise e


def safe_remove(_file_path):
    try:
        if os.path.exists(_file_path):
            os.remove(_file_path)
            return True
        return False
    except Exception as _:
        logger.error(f'删除文件 {_file_path} 时发生错误: {str(_)}')
        return False


def safe_rmdir(_dir_path):
    try:
        if os.path.exists(_dir_path):
            os.rmdir(_dir_path)
            return True
        return False
    except Exception as _:
        logger.error(f'删除目录 {_dir_path} 时发生错误: {str(_)}')
        return False


@app.task
def task__auto_clear_authorization_letter():
    objs = AuthorizationLetter.objects.filter(authorization_filepath__isnull=False).values_list(
        'authorization_filepath', flat=True)
    save_path = set(objs)

    output_dir_config = AuthorizationConfig.objects.filter(key='authorization_output_dir').first()
    if not output_dir_config:
        message = '未找到授权书输出路径配置'
        logger.error(message)
        return {'error': message}
    output_dir = output_dir_config.value

    file_count = 0
    file_clear_count = 0

    # 清理多余文件
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))
            if file_path not in save_path:
                if safe_remove(file_path):
                    file_clear_count += 1
            file_count += 1

    dir_count = 0
    dir_clear_count = 0
    # 清理空目录
    for root, dirs, files in os.walk(output_dir, topdown=False):
        for _dir in dirs:
            dir_path = os.path.abspath(os.path.join(root, _dir))
            if not os.path.exists(dir_path):
                continue
            if not os.listdir(dir_path):
                if safe_rmdir(dir_path):
                    dir_clear_count += 1
            dir_count += 1
        if not os.path.exists(root):
            continue
        if not os.listdir(root):
            if safe_rmdir(root):
                dir_clear_count += 1

    message = (f'清理了{file_clear_count}个文件，共{file_count}个文件, '
               f'清理了{dir_clear_count}个目录，共{dir_count}个目录')
    logger.info(message)
    return {'message': message}
