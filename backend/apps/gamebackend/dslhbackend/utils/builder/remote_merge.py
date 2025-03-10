"""
Creation date: 2024/12/18
Creation Time: 下午4:03
DIR PATH: 
Project Name: 大圣轮回合服
FILE NAME: remote_merge.py
Editor: 30386
"""
import os

from jinja2 import Environment, FileSystemLoader


def generate_backup_script(output_dir, remote_path, prefix, password, start_id, end_id):
    # 创建目标文件夹
    os.makedirs(output_dir, exist_ok=True)

    # 定义模板文件路径
    template_folder = os.path.join(os.path.dirname(__file__), 'tempj2')
    template_name = 'remote_merge.j2'

    # 加载 Jinja2 环境
    env = Environment(loader=FileSystemLoader(template_folder))
    template = env.get_template(template_name)

    # 渲染模板
    rendered_content = template.render({
        'mysql_database_prefix': prefix,
        'mysql_root_password': password,
        'start_id': start_id,
        'end_id': end_id,
        'remote_path': remote_path
    })

    # 将渲染后的内容写入目标文件
    with open(os.path.join(output_dir, 'remote_merge.sh'), 'w', encoding="utf-8", newline='\n') as output_file:
        output_file.write(rendered_content)
    print(f"Script generated at {os.path.join(output_dir, 'remote_merge.sh')}")
