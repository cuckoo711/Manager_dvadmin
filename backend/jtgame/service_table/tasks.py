"""
Creation date: 2024/10/14
Creation Time: 下午2:49
DIR PATH: backend/jtgame/service_table
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
import os
import re
import zipfile
from datetime import timedelta, datetime

import pandas as pd
import xlrd
import xlwt

from application.celery import app
from jtgame.service_table.models import ServiceTableNormal, ServiceTableSplit, ServiceTableTemplate, ServiceTableMap
from jtgame.service_table.utils.buildpath import build_server_table_output_path
from jtgame.service_table.utils.changer import Changer


@app.task
def task__generate_service_table(normal_service_table_ids: list):
    for normal_service_table_id in normal_service_table_ids:
        normal = ServiceTableNormal.objects.get(id=normal_service_table_id)

        output_path = build_server_table_output_path()
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

        start_datetime = start_datetime.replace(tzinfo=None) + timedelta(hours=8)
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

    return {"message": f"生成成功, 共计{len(normal_service_table_ids)}条"}


@app.task
def task__generate_service_split_table(split_service_table_id: int):
    split: ServiceTableSplit = ServiceTableSplit.objects.get(id=split_service_table_id)
    output_path = split.output_dir
    service_table_normals = split.service_table_normals.all()
    service_table_dict = {}
    service_table_list = []
    logs = []
    split.generate_status = '3'
    split.save()
    logs.append(f"开始生成{split.id}的开服表")
    stime = datetime.now()

    headers = ['gamename', 'open_date_only', 'open_time_only', 'open_datetime', 'open_name', 'open_id',
               'open_timestamp']
    for normal in service_table_normals:
        normal: ServiceTableNormal
        no_first_service_path = normal.no_first_service_path
        if not no_first_service_path:
            return {"error": f"{normal.game_name}未生成开服表"}
        datas = Changer.init_df(pd.read_excel(no_first_service_path, dtype=str))
        datas.columns = headers
        datas_dicts = datas.to_dict(orient='records')
        service_table_dict[normal.game_name] = datas_dicts
        service_table_list.extend(datas_dicts)

    templates = ServiceTableTemplate.objects.filter(is_enable='1')
    templates_splits = templates.filter(is_split='1')
    templates_no_splits = templates.filter(is_split='2')

    output_format_map = {
        '0': 'xls',
        '1': 'xlsx',
        '2': 'csv'
    }
    for template in templates_splits:
        template: ServiceTableTemplate
        template_dir_name = template.template_name
        channel = template.channel
        channel_output_path = f"{output_path}/{template_dir_name}/{channel.name}"
        os.makedirs(channel_output_path, exist_ok=True)

        for gamename, datas in service_table_dict.items():
            do_all = False if channel.column.strip() else True
            if not do_all:
                game_name_map: ServiceTableMap | None = ServiceTableMap.objects.filter(
                    game_name=gamename, channel=channel).first()
                if not game_name_map:
                    # logs.append(f"{gamename}未配置{channel.name}的映射")
                    continue
            else:
                game_name_map = None

            for data in datas:
                if not do_all:
                    data.update({'game_id': game_name_map.game_map_name})
            output_file = f"{channel_output_path}/{gamename}.{output_format_map[template.output_format]}"
            if template.output_engine == '0':
                field, headers = str(template.template_fields).split('||')
                fields = field.replace('&&', ' ').split(',')
                headers = headers.split(',')

                with pd.ExcelWriter(output_file) as writer:
                    work_sheet = writer.book.add_worksheet('Sheet1')
                    work_sheet.write_row(0, 0, headers)
                    for index, data in enumerate(datas):
                        for col, field in enumerate(fields):
                            for key, value in data.items():
                                if field.startswith(key):
                                    if 'open_datetime' in field:
                                        datetime_type = field.split('open_datetime_')[-1]
                                        if datetime_type.startswith('strftime_'):
                                            datetime_format = datetime_type.split('strftime_')[-1]
                                            work_sheet.write(index + 1, col, data[key].strftime(datetime_format))
                                        elif datetime_type == 'numformat':
                                            work_sheet.write_datetime(index + 1, col, data[key], writer.book.add_format(
                                                {'num_format': datetime_type.split('numformat_')[-1]}))
                                        else:
                                            work_sheet.write_datetime(index + 1, col, data[key])
                                    else:
                                        work_sheet.write(index + 1, col, data[key])
                                    break
                            else:
                                work_sheet.write(index + 1, col, field)
            elif template.output_engine == '1':
                res_data = pd.DataFrame(eval(template.template_fields))
                if template.output_format == '2':
                    res_data.to_csv(output_file, index=False, encoding='gbk')
                elif template.output_format == '1':
                    res_data.to_excel(output_file, index=False)
                else:
                    res_data.to_excel(output_file, index=False, engine='openpyxl')
            elif template.output_engine == '2':
                field, headers = str(template.template_fields).split('||')
                fields = field.replace('&&', ' ').split(',')
                headers = headers.split(',')

                workbook = xlwt.Workbook()
                worksheet = workbook.add_sheet('Sheet1', cell_overwrite_ok=True)
                for index, header in enumerate(headers):
                    worksheet.write(0, index, header)
                datastyle = xlwt.XFStyle()
                for index, data in enumerate(datas):
                    for col, field in enumerate(fields):
                        for key, value in data.items():
                            if field.startswith(key):
                                if 'open_timestamp' in field:
                                    timestamp_type = field.split('open_timestamp_')[-1]
                                    if timestamp_type.startswith('xlrd_'):
                                        timestamp_format = timestamp_type.split('xlrd_')[-1]
                                        worksheet.write(index + 1, col,
                                                        str(xlrd.xldate_as_datetime(data[key], int(timestamp_format))))
                                    else:
                                        datastyle.num_format_str = timestamp_type
                                        worksheet.write(index + 1, col, data[key], datastyle)
                                else:
                                    worksheet.write(index + 1, col, data[key])
                                break
                        else:
                            worksheet.write(index + 1, col, field)
                workbook.save(output_file)
            else:
                logs.append(f"{template.template_name}未配置输出引擎")

    for template in templates_no_splits:
        template: ServiceTableTemplate
        template_name = template.template_name
        channel = template.channel
        channel_output_path = f"{output_path}/{channel.name}"
        os.makedirs(channel_output_path, exist_ok=True)
        no_split_output_path = f"{channel_output_path}/{template_name}.{output_format_map[template.output_format]}"
        do_all = False if channel.column.strip() else True

        datas = []
        for data in service_table_list:
            gamename = data['gamename']
            if not do_all:
                game_name_map: ServiceTableMap = ServiceTableMap.objects.filter(
                    game_name=gamename, channel=channel).first()
                if not game_name_map:
                    # logs.append(f"{gamename}未配置{channel.name}的映射")
                    continue
                data.update({'game_id': game_name_map.game_map_name})
            else:
                data.update({'game_id': gamename})
            datas.append(data)

        if template.output_engine == '0':
            field, headers = str(template.template_fields).split('||')
            fields = field.replace('&&', ' ').split(',')
            headers = headers.split(',')

            with pd.ExcelWriter(no_split_output_path) as writer:
                work_sheet = writer.book.add_worksheet('Sheet1')
                work_sheet.write_row(0, 0, headers)
                for index, data in enumerate(datas):
                    for col, field in enumerate(fields):
                        for key, value in data.items():
                            if field.startswith(key):
                                if 'open_datetime' in field:
                                    datetime_type = field.split('open_datetime_')[-1]
                                    if datetime_type.startswith('strftime_'):
                                        datetime_format = datetime_type.split('strftime_')[-1]
                                        work_sheet.write(index + 1, col, data[key].strftime(datetime_format))
                                    elif datetime_type == 'numformat':
                                        work_sheet.write_datetime(index + 1, col, data[key], writer.book.add_format(
                                            {'num_format': datetime_type.split('numformat_')[-1]}))
                                    else:
                                        work_sheet.write_datetime(index + 1, col, data[key])
                                else:
                                    work_sheet.write(index + 1, col, data[key])
                                break
                        else:
                            work_sheet.write(index + 1, col, field)
        elif template.output_engine == '1':
            res_data = pd.DataFrame(eval(template.template_fields))
            if template.output_format == '2':
                res_data.to_csv(no_split_output_path, index=False, encoding='gbk')
            elif template.output_format == '1':
                res_data.to_excel(no_split_output_path, index=False)
            else:
                res_data.to_excel(no_split_output_path, index=False, engine='openpyxl')
        elif template.output_engine == '2':
            field, headers = str(template.template_fields).split('||')
            fields = field.replace('&&', ' ').split(',')
            headers = headers.split(',')

            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet1', cell_overwrite_ok=True)
            for index, header in enumerate(headers):
                worksheet.write(0, index, header)
            datastyle = xlwt.XFStyle()
            for index, data in enumerate(datas):
                for col, field in enumerate(fields):
                    for key, value in data.items():
                        if field.startswith(key):
                            if 'open_timestamp' in field:
                                timestamp_type = field.split('open_timestamp_')[-1]
                                if timestamp_type.startswith('xlrd_'):
                                    timestamp_format = timestamp_type.split('xlrd_')[-1]
                                    worksheet.write(index + 1, col,
                                                    str(xlrd.xldate_as_datetime(data[key], int(timestamp_format))))
                                else:
                                    datastyle.num_format_str = timestamp_type
                                    worksheet.write(index + 1, col, data[key], datastyle)
                            else:
                                worksheet.write(index + 1, col, data[key])
                            break
                    else:
                        worksheet.write(index + 1, col, field)
            workbook.save(no_split_output_path)

    logs.append(f"生成成功, 耗时: {datetime.now() - stime}")
    logs.append(f"开始压缩文件")
    # linux下压缩文件
    output_zip = f"{output_path}_{split.id}.zip"
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_path)
                zipf.write(file_path, arcname)
    logs.append(f"压缩成功 {split.id}.zip")
    split.generate_status = '1'
    split.generate_logs = '\n'.join(logs)
    split.service_table_split_zip = output_zip
    split.save()
    return {"message": "生成成功", "logs": logs}
