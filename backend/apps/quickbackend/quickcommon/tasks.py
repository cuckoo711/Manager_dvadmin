"""
Creation date: 2024/10/25
Creation Time: 下午3:16
DIR PATH: backend/apps/quickbackend/quickcommon
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
from application.celery import app
from apps.quickbackend.quickcommon.models import QuickUser


@app.task
def task__auto_update_quick_cookies():
    for account in QuickUser.objects.all():
        account: QuickUser
        if account.password:
            account.update_cookie()
