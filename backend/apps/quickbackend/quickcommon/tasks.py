"""
Creation date: 2024/10/25
Creation Time: 下午3:16
DIR PATH: backend/apps/quickbackend/quickcommon
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
from datetime import datetime

from application.celery import app
from apps.quickbackend.quickcommon.models import QuickUser, QuickRegularTask
from dvadmin.system.views.message_center import MessageCenterCreateSerializer
from dvadmin.utils.backends import logger


@app.task
def task__auto_update_quick_cookies():
    for account in QuickUser.objects.all():
        account: QuickUser
        if account.password:
            account.update_cookie()


@app.task
def task__auto_update_channel_status():
    today = datetime.now().date()
    quick_regular_tasks = QuickRegularTask.objects.filter(status='0', task_date=today)
    task_type_map = {
        '0': '批量关注册',
        '1': '批量关支付',
        '2': '批量关登录',
        '3': '批量开注册',
        '4': '批量开支付',
        '5': '批量开登录',
    }
    task_status_map = {
        '0': '未执行',
        '1': '已执行',
        '2': '执行失败',
    }
    msg = ''
    for task in quick_regular_tasks:
        task: QuickRegularTask
        task.execute_task()
        logger.info(f'执行任务{task.id} {task.game_name} {task.status}')

        msg += (f'[{task_status_map[task.status]}] 游戏 [{task.game_name}] - [{task_type_map[task.task_type]}] '
                f'创建人：[{task.creator.username}]\n')
    message_data = {
        'title': f'执行定时关服流程-{today}',
        'content': msg,
        'target_type': 1,
        'target_role': [17],
    }
    serializer = MessageCenterCreateSerializer(data=message_data)
    if serializer.is_valid():
        serializer.save()
