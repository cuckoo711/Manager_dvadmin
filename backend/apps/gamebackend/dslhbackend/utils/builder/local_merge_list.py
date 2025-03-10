"""
Creation Date: 2024/12/19
Creation Time: 下午7:05
Dir Path: builder
Project Name: DSLH_Merge
File Name: local_merge_list.py
Editor: cuckoo
"""
import os

from jinja2 import Environment, FileSystemLoader


def generate_local_merge_script(output_path, variables, single=False, merged=False):
    # 创建目标文件夹
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 定义模板文件路径
    template_folder = os.path.join(os.path.dirname(__file__), 'tempj2')
    if single:
        if merged:
            template_name = 'cp_single.j2'
        else:
            template_name = 'local_merge_single.j2'
    else:
        if merged:
            template_name = 'local_merged.j2'
        else:
            template_name = 'local_merge.j2'

    # 加载 Jinja2 环境
    env = Environment(loader=FileSystemLoader(template_folder))
    template = env.get_template(template_name)

    # 渲染模板
    rendered_content = template.render(variables)

    # 将渲染后的内容写入目标文件
    with open(output_path, 'w', encoding="utf-8", newline='\n') as output_file:
        output_file.write(rendered_content)
    print(f"Script generated at {output_path}")


def generate_batch_execute_script(output_path, shs_path, script_count, merged_count):
    """
    生成批量执行脚本

    :param output_path: 批量执行脚本的输出路径
    :param shs_path: 脚本的路径
    :param script_count: 要执行的脚本总数
    :param merged_count: 要执行的合并脚本总数
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 脚本内容
    script_lines = ["#!/bin/bash", ""]

    if script_count != 0:
        for idx in range(1, script_count + 1):
            script_lines.append(f"echo \"Executing {shs_path}/local_merge_{idx}.sh...\"")
            script_lines.append(f"bash {shs_path}/local_merge_{idx}.sh")
            script_lines.append("if [ $? -ne 0 ]; then")
            script_lines.append(f"  echo \"Error occurred while executing {shs_path}/local_merge_{idx}.sh\"")
            script_lines.append("  exit 1")
            script_lines.append("fi")
            script_lines.append(f"echo \"{shs_path}/local_merge_{idx}.sh executed successfully!\"\n")
    if merged_count != 0:
        for idx in range(1, merged_count + 1):
            script_lines.append(f"echo \"Executing {shs_path}/local_merge_merged_{idx}.sh...\"")
            script_lines.append(f"bash {shs_path}/local_merge_merged_{idx}.sh")
            script_lines.append("if [ $? -ne 0 ]; then")
            script_lines.append(f"  echo \"Error occurred while executing {shs_path}/local_merge_merged_{idx}.sh\"")
            script_lines.append("  exit 1")
            script_lines.append("fi")
            script_lines.append(f"echo \"{shs_path}/local_merge_merged_{idx}.sh executed successfully!\"\n")

    # 如果有单独的脚本, 则执行单独的脚本, 否则跳过
    script_lines.append(f"if [ -f \"{shs_path}/local_merge_single_{script_count + 1}.sh\" ]; then")
    script_lines.append(f"  echo \"Executing {shs_path}/local_merge_single_{script_count + 1}.sh...\"")
    script_lines.append(f"  bash {shs_path}/local_merge_single_{script_count + 1}.sh")
    script_lines.append("  if [ $? -ne 0 ]; then")
    script_lines.append(
        f"    echo \"Error occurred while executing {shs_path}/local_merge_single_{script_count + 1}.sh\"")
    script_lines.append("    exit 1")
    script_lines.append("  fi")
    script_lines.append(f"  echo \"{shs_path}/local_merge_single_{script_count + 1}.sh executed successfully!\"")
    script_lines.append("else")
    script_lines.append(f"  echo \"{shs_path}/local_merge_single_{script_count + 1}.sh not found, skipping...\"")
    script_lines.append("fi\n")

    script_lines.append("echo \"All scripts executed successfully!\"")

    # 将内容写入脚本
    with open(output_path, 'w', encoding='utf-8', newline='\n') as batch_file:
        batch_file.write('\n'.join(script_lines))

    print(f"Batch execute script generated at {output_path}")


def generate_batch_all_execute_script(output_path, script_count):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 脚本内容
    script_lines = ["#!/bin/bash", ""]

    for idx in range(1, script_count + 1):
        script_lines.append(f"echo \"Executing ./batch_execute_{idx}.sh...\"")
        script_lines.append(f"bash ./batch_execute_{idx}.sh")
        script_lines.append("if [ $? -ne 0 ]; then")
        script_lines.append(f"  echo \"Error occurred while executing ./batch_execute_{idx}.sh\"")
        script_lines.append("  exit 1")
        script_lines.append("fi")
        script_lines.append(f"echo \"./batch_execute_{idx}.sh executed successfully!\"\n")

    # 将内容写入脚本
    with open(output_path, 'w', encoding='utf-8', newline='\n') as batch_file:
        batch_file.write('\n'.join(script_lines))

    print(f"Batch execute all script generated at {output_path}")


def generate_merge_scripts(output_path, remote_path, prefix, dest_id, merge_ids, merged_ids, password, step=1):
    merge_ids.sort(key=lambda x: int(x), reverse=True)
    os.makedirs(output_path, exist_ok=True)
    second_output = f'shs_{step}'
    os.makedirs(os.path.join(output_path, second_output), exist_ok=True)
    variables_list = []
    variables_merged_list = []
    next_ids = []
    variables_single = {}
    is_single = len(merge_ids) % 2
    for i in range(0, len(merge_ids) - is_single, 2):
        source_server_id = merge_ids[i]
        target_server_id = merge_ids[i + 1]
        print(f"source_server_id: {source_server_id}, target_server_id: {target_server_id}")
        variables = {
            'mysql_database_prefix': prefix,
            'source_server_id': source_server_id,
            'target_server_id': target_server_id,
            'dest_server_id': dest_id,
            'mysql_root_password': password,
            'backup_dir': f'{remote_path}/merge{step - 1 if step != 1 else ""}',
            'merge_dir': f'{remote_path}/merge{step}',
        }
        variables_list.append(variables)
        next_ids.append(target_server_id)
    for idx, merged_id in enumerate(merged_ids):
        variables = {
            'source_file_path': f'{remote_path}/merge/{prefix}{merged_id}.sql',
            'destination_directory': f'{remote_path}/merge{step}',
        }
        variables_merged_list.append(variables)
        next_ids.append(merged_id)
    if is_single:
        last_id = merge_ids[-1]
        if step == 1:
            variables_single = {
                'mysql_database_prefix': prefix,
                'source_server_id': last_id,
                'target_server_id': last_id,
                'dest_server_id': dest_id,
                'mysql_root_password': password,
                'backup_dir': f'{remote_path}/merge{step - 1 if step != 1 else ""}',
                'merge_dir': f'{remote_path}/merge{step}',
            }
        else:
            variables_single = {
                'source_file_path': f'{remote_path}/merge{step - 1 if step != 1 else ""}/{prefix}{last_id}.sql',
                'destination_directory': f'{remote_path}/merge{step}',
            }
        next_ids.append(last_id)

    for idx, variables in enumerate(variables_list):
        script_name = f'{output_path}/{second_output}/local_merge_{idx + 1}.sh'
        if step == 1:
            generate_local_merge_script(script_name, variables)
        else:
            generate_local_merge_script(script_name, variables, merged=True)
    for idx, variables in enumerate(variables_merged_list):
        script_name = f'{output_path}/{second_output}/local_merge_merged_{idx + 1}.sh'
        generate_local_merge_script(script_name, variables, single=True, merged=True)
    if variables_single:
        script_name = f'{output_path}/{second_output}/local_merge_single_{len(variables_list) + 1}.sh'
        if step == 1:
            generate_local_merge_script(script_name, variables_single, single=True)
        else:
            generate_local_merge_script(script_name, variables_single, single=True, merged=True)

    generate_batch_execute_script(f'{output_path}/batch_execute_{step}.sh', second_output, len(variables_list), len(variables_merged_list))
    if len(next_ids) > 1:
        return generate_merge_scripts(output_path, remote_path, prefix, dest_id, next_ids, [], password, step + 1)
    else:
        generate_batch_all_execute_script(f'{output_path}/batch_execute_all.sh', step)
        print("All scripts executed successfully!")
        return step
