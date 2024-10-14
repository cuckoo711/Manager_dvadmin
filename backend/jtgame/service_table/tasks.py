"""
Creation date: 2024/10/14
Creation Time: 下午2:49
DIR PATH: backend/jtgame/service_table
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
import re
from datetime import timedelta

import pandas as pd

from application.celery import app
from jtgame.service_table.models import ServiceTableNormal
from jtgame.service_table.utils import build_output_path


@app.task
def task__generate_service_table(normal_service_table_id: int):
    normal = ServiceTableNormal.objects.get(id=normal_service_table_id)

    output_path = build_output_path()
    first_service_path = f"{output_path}/{normal.game_name}_带首服.xlsx"
    no_first_service_path = f"{output_path}/{normal.game_name}.xlsx"
    start_datetime = normal.open_datetime
    frequency = normal.open_frequency
    count = normal.open_count
    normal.copy_content = ''
    data = []

    server_name_match = re.search(r"(\D+)(\d+)(\D*)", normal.open_name)
    if not server_name_match:
        return {"error": "开服名称格式错误"}
    server_name_prefix = server_name_match.group(1) + '{}' + server_name_match.group(3)
    server_name_suffix = int(server_name_match.group(2))

    for _ in range(count + 1):
        server_name = server_name_prefix.format(server_name_suffix)
        current_date = start_datetime.strftime("%Y/%m/%d")
        current_time = start_datetime.strftime("%H:%M:%S")
        current_datetime = start_datetime.strftime("%Y/%m/%d %H:%M")
        data.append([normal.game_name, current_date, current_time,
                     current_datetime, server_name, server_name_suffix])
        normal.copy_content += f"{server_name}\t{current_time}" + '\n'.join(
            '' for _ in range(frequency)) + '\n'
        start_datetime += timedelta(days=frequency)
        server_name_suffix += 1

    columns = ['游戏名', '日期', '时间', '开服时间', '区服名称', '区服序号']
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(first_service_path, index=False)
    df.iloc[1:].to_excel(no_first_service_path, index=False)

    normal.first_service_path = first_service_path
    normal.no_first_service_path = no_first_service_path

    normal.generate_status = '1'
    normal.save()

    return {"message": "生成成功"}
