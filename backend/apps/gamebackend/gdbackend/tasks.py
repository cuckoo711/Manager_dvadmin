"""
Creation date: 2024/12/9
Creation Time: 下午1:42
DIR PATH: backend/apps/gamebackend/gdbackend
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
from hashlib import md5
from io import BytesIO
from urllib.parse import urlparse

import pandas as pd
import requests
from _socket import gethostbyname
from django.core.files.base import ContentFile

from application.celery import app
from apps.gamebackend.gdbackend.models import GDServer, GDToken, GDActiveConfig, GDActiveLog
from apps.gamebackend.gdbackend.utils import get_class_by_name
from apps.gamebackend.gdbackend.utils.getLatestServers import ApiGetLatestServers
from apps.gamebackend.gdbackend.utils.uploadActivity import ApiUploadActivity
from apps.gamebackend.gdbackend.utils.util import process_lists
from apps.jtgame.daily_report.utils import send_email
from dvadmin.system.models import DownloadCenter, Users
from dvadmin.system.views.message_center import MessageCenterCreateSerializer
from dvadmin.utils.backends import logger


@app.task
def async_export_data(func_cls_name: str, token_id: int, run_kwargs: dict,
                      filename: str, dcid: int, export_field_label: dict, *args, **kwargs):
    instance = DownloadCenter.objects.get(pk=dcid)
    instance.task_status = 1
    instance.save()
    try:
        func_cls = get_class_by_name(func_cls_name)
        data = func_cls(token_id).run(**run_kwargs)
        df = pd.DataFrame(data)
        df.rename(columns=export_field_label, inplace=True)
        stream = BytesIO()
        # noinspection PyTypeChecker
        df.to_excel(stream, index=False, header=True, sheet_name='Sheet1')
        stream.seek(0)
        s = md5()
        while True:
            chunk = stream.read(1024)
            if not chunk:
                break
            s.update(chunk)
        stream.seek(0)
        instance.md5sum = s.hexdigest()
        instance.file_name = filename
        instance.url.save(filename, ContentFile(stream.read()))
        instance.task_status = 2
        message_data = {
            'title': f'数据导出成功',
            'content': f'您的{instance.file_name}已经成功导出，请到数据中心下载',
            'target_type': 0,
            'target_role': [instance.creator.id],
        }
        serializer = MessageCenterCreateSerializer(data=message_data)
        if serializer.is_valid():
            serializer.save()
    except Exception as e:
        instance.task_status = 3
        instance.description = str(e)[:250]
        message_data = {
            'title': f'数据导出失败',
            'content': f'导出任务失败，错误信息：{str(e)[:100]}',
            'target_type': 0,
            'target_role': [instance.creator.id],
        }
        serializer = MessageCenterCreateSerializer(data=message_data)
        if serializer.is_valid():
            serializer.save()
    finally:
        instance.save()


def generate_tree(data):
    tree = ""
    for game in data:
        for game_name, game_data in game.items():
            tree += f"{game_name}\n"
            for key, value in game_data.items():
                tree += f"\t├── {key}\n"
                for item in value:
                    tree += f"\t\t├── {item}\n"
    return tree


def check_server(game_server: GDServer):
    retries = 3
    check_message = ""

    host_check = False
    while retries > 0:
        try:
            parsed_url = urlparse(game_server.web_url)
            # 获取域名或从URL路径提取域名
            host_url = parsed_url.netloc or parsed_url.path.split("/")[0]
            # 获取服务器主机地址
            host = gethostbyname(host_url)

            # 比较域名解析结果
            if game_server.server_host != host:
                check_message = f"游戏{game_server.gamename}的域名解析不一致，服务器可能已经更换，请检查"
                logger.warning(check_message)  # 添加日志记录
            else:
                host_check = True
            break
        except Exception as e:
            check_message = f"游戏{game_server.gamename}的域名解析失败，服务器可能已经退订，请检查。错误详情：{str(e)}"

        retries -= 1
    if not host_check:
        logger.error(f"重试3次，{check_message}")
    if host_check:
        web_check = False
        retries = 3
        while retries > 0:
            try:
                response = requests.get(game_server.web_url, timeout=30)
                if response.status_code != 200:
                    check_message = f"游戏{game_server.gamename}的网站访问失败，服务器可能已经退订，请检查"
                    logger.warning(check_message)
                else:
                    web_check = True
                break
            except Exception as e:
                check_message = f"游戏{game_server.gamename}的网站访问失败，服务器可能已经退订，请检查。错误详情：{str(e)}"
            retries -= 1
        if not web_check:
            logger.error(f"重试3次，{check_message}")
        else:
            return True
    send_email("自动上传活动警告", check_message, ["cuckoo@halffive.fun"])

    # 使用字典直接传递数据，避免不必要的变量
    message_data = {
        'title': '自动上传活动警告',
        'content': check_message,
        'target_type': 1,
        'target_role': [21],
    }

    # 保存消息
    serializer = MessageCenterCreateSerializer(data=message_data)
    if serializer.is_valid():
        serializer.save()

    # 将游戏服务器状态设置为不活跃
    game_server.is_active = False
    game_server.save()

    return False


@app.task
def task__auto_upload_activity(*args, **kwargs):
    user: Users
    token: GDToken
    game_server: GDServer

    game_servers = GDServer.objects.filter(is_active=True).all()
    user = Users.objects.filter(is_staff=True).first()
    count = 0
    logs = []
    for game_server in game_servers:
        if not check_server(game_server):
            continue
        active_config = GDActiveConfig.objects.filter(game_server=game_server).first()
        if not active_config:
            continue
        token = GDToken.objects.filter(user=user, game_server=game_server).first()
        if not token:
            token = GDToken.objects.create(
                user=user,
                game_server=game_server,
                creator=user,
                dept_belong_id=user.dept.id if user.dept else None
            )
            token.update_token()
        start_date, upload_server, range_end = ApiGetLatestServers(token.id).run()
        if start_date and upload_server:
            upload_config = process_lists(active_config.configs, start_date)
            result = ApiUploadActivity(token.id).run(
                servers=upload_server,
                range_start=2,
                range_end=4,
                datas=upload_config
            )
            GDActiveLog.objects.create(
                log=result['log'],
                game_name=game_server.gamename,
                upload_type=1,
                status=1 if result['status'] else 0,
                creator=user,
                dept_belong_id=user.dept.id if user.dept else None,
                description="自动上传活动"
            )
            count += 1
            logs.append({f"{str(game_server.gamename)}_{start_date}": result['log']})
    if count:
        message = f"自动上传活动成功, 共{count}个游戏\n{generate_tree(logs)}"
    else:
        message = "没有需要上传的活动"
    email = send_email("自动上传活动结果", message, ["cuckoo@halffive.fun"])

    return {"status": True, "message": f"自动上传活动成功, 共{len(game_servers)}个游戏", "email": email}
