"""
Creation date: 2024/12/20
Creation Time: 下午2:31
DIR PATH: builder
Project Name: 大圣轮回合服
FILE NAME: import_sql.py
Editor: 30386
"""

import os

from jinja2 import Environment, FileSystemLoader


def generate_import_sql_script(output_dir, database, password, sql_path):
    # 创建目标文件夹
    os.makedirs(output_dir, exist_ok=True)

    # 定义模板文件路径
    template_folder = os.path.join(os.path.dirname(__file__), 'tempj2')
    template_name = 'import_sql.j2'

    # 加载 Jinja2 环境
    env = Environment(loader=FileSystemLoader(template_folder))
    template = env.get_template(template_name)

    # 渲染模板
    rendered_content = template.render({
        'mysql_database': database,
        'mysql_password': password,
        'sql_path': sql_path,
    })

    # 将渲染后的内容写入目标文件
    with open(os.path.join(output_dir, 'import_sql.sh'), 'w', encoding="utf-8", newline='\n') as output_file:
        output_file.write(rendered_content)
    print(f"Script generated at {os.path.join(output_dir, 'import_sql.sh')}")
