"""
Creation date: 2024/7/18
Creation Time: 上午11:09
DIR PATH: backend/jtgame/daily_report
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
import datetime
import json

from celery import chain

from application.celery import app
from apps.jtgame.daily_report.models import ReportData, ConsoleAccount, Consoles
from apps.jtgame.daily_report.utils import ConsoleData, QuickTotal, RenewConsole


@app.task
def task__make_daily_report(shifting_days=0):
    console_data = ConsoleData()
    console_data.make_daily_report()
    instances = console_data.instances
    income = QuickTotal(shifting_days).make_daily_report()

    data = {
        "instance": instances,
        "income": income[0],
        "banhao": income[1]
    }
    data = json.loads(json.dumps(data, ensure_ascii=False))
    today = datetime.date.today() - datetime.timedelta(days=shifting_days)
    today_str = today.strftime('%Y-%m-%d')
    try:
        report = ReportData.objects.filter(date=today).first()
        if report:
            report.data = data
            report.save()
            result = {"success": True, "status": "update", "error": "", "date": today_str}
        else:
            ReportData.objects.create(date=today, data=data)
            result = {"success": True, "status": "create", "error": "", "date": today_str}
    except Exception as e:
        result = {"success": False, "status": "error", "error": str(e), "date": today_str}

    return json.dumps(result, ensure_ascii=False)


@app.task
def task__renew(instance_id, account):
    instance = Consoles.objects.filter(instance_id=instance_id).first()
    if not instance:
        raise Exception('未找到对应的服务器')
    console_account = ConsoleAccount.objects.filter(account=account).first()
    if not console_account:
        raise Exception('未找到对应的服务器账号')
    instance.renewal_status = True
    instance.save()
    response = RenewConsole(console_account, instance_id)
    instance.renewal_status = False
    instance.save()
    return response


@app.task
def task__update_consoles():
    try:
        result = ConsoleData().make_daily_report(update=True)
        return {"success": True, "status": "update", "error": "", "data": json.dumps(result, ensure_ascii=False)}
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e)}


@app.task
def task__auto_renew():
    instances = Consoles.objects.filter(renewal_status=False).all()
    result = []

    for instance in instances:
        expired_at_naive: datetime.datetime = instance.expired_at.replace(tzinfo=None) + datetime.timedelta(hours=8)
        today = datetime.date.today()
        now = datetime.datetime.combine(today, datetime.time.min)

        if instance.renewal_status or (expired_at_naive - now).days >= 1 or instance.status.lower() != "running":
            continue

        try:
            chain(task__renew.s(instance.instance_id, instance.account)).apply_async()
            result.append({"status": True, "instance_id": instance.instance_id})
        except Exception as e:
            result.append({"status": False, "message": '续费失败', "data": str(e), "instance_id": instance.instance_id})

    chain(task__update_consoles.s()).apply_async()
    return {"status": True, "message": "续费操作已提交", "data": result}
