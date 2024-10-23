"""
Creation date: 2024/10/17
Creation Time: 下午1:16
DIR PATH: backend/jtgame/service_table/utils
Project Name: Manager_dvadmin
FILE NAME: spliter.py
Editor: 30386
"""


def parse_template_fields(template_fields):
    fields = template_fields.split(',')
    field_mappings = []
    for field in fields:
        if '&&' in field:
            field = field.replace('&&', ' ')
        field_mappings.append(field)
    return field_mappings


def parse_strftime_format(format_str):
    format_str = format_str.replace('yyyy', '%Y').replace('MM', '%m').replace('dd', '%d').replace(
        'HH', '%H').replace('mm', '%M').replace('ss', '%S')
    return format_str
