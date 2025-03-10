"""
Creation date: 2024/12/20
Creation Time: 下午5:55
DIR PATH: 
Project Name: 大圣轮回合服
FILE NAME: Merger.py
Editor: 30386
"""
import os
import shutil
import time
from typing import List

from application.settings import BASE_DIR
from apps.gamebackend.dslhbackend.utils.builder.import_sql import generate_import_sql_script
from apps.gamebackend.dslhbackend.utils.builder.local_merge_list import generate_merge_scripts
from apps.gamebackend.dslhbackend.utils.builder.remote_merge import generate_backup_script
from apps.gamebackend.dslhbackend.utils.filelinker import RemoteFileManager


class ServerMerger:
    def __init__(
            self,
            remote_ip: str,
            mysql_password: str,
            prefix: str,
            start_id: int,
            end_id: int,
            dest_id: str,
            merge_ids: List[str],
            merged_ids: List[str],
            remote_password: str,
            remote_path: str = "/home/merge",
            output_dir: str = "merge_scripts"
    ):
        self.remote_ip = remote_ip
        self.remote_password = remote_password
        self.mysql_password = mysql_password
        self.prefix = prefix
        self.start_id = start_id
        self.end_id = end_id
        self.dest_id = dest_id
        self.merge_ids = merge_ids
        self.merged_ids = merged_ids
        self.remote_path = remote_path
        self.output_dir = os.path.join(BASE_DIR, 'temp', 'dslh_merge', output_dir)

        self._logs = []

    def clear_output_dir(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def generate_scripts(self):
        self.clear_output_dir()
        os.makedirs(self.output_dir, exist_ok=True)
        generate_backup_script(
            self.output_dir,
            self.remote_path,
            self.prefix,
            self.mysql_password,
            self.start_id,
            self.end_id
        )
        step = generate_merge_scripts(
            self.output_dir, self.remote_path,
            self.prefix,
            self.dest_id,
            self.merge_ids,
            self.merged_ids,
            self.mysql_password,
            1
        )
        last_database = f"{self.prefix}{self.start_id}"
        last_sql = f"{self.remote_path}/merge{step}/{last_database}.sql"
        generate_import_sql_script(self.output_dir, last_database, self.mysql_password, last_sql)

    def execute_command_log(self, source_manager: RemoteFileManager, path, command):
        logs = source_manager.execute_command(path, command)
        self._logs.append({
            "path": path,
            "command": command,
            "logs": logs
        })

    def merge(self):
        source_manager = RemoteFileManager(self.remote_ip, self.remote_password)
        try:
            # 检查合服状态
            if source_manager.check_file_exists("/home", "merging"):
                raise Exception("合服正在进行中，请稍后再试")

            self.execute_command_log(source_manager, "/home", "touch merging")
            if not source_manager.check_file_exists("/home", "merging"):
                raise Exception("标记文件创建失败")

            if source_manager.check_file_exists("/home", self.remote_path):
                # 备份旧合服脚本
                self.execute_command_log(source_manager, "/home", f"mv {self.remote_path} {self.remote_path}_{time.time()}")

            # 上传合服脚本
            source_manager.upload(self.output_dir, f"{self.remote_path}/merge_scripts")
            self.execute_command_log(source_manager, self.remote_path, f"chmod -R +x {self.remote_path}/merge_scripts")
            self.execute_command_log(source_manager, f"{self.remote_path}/merge_scripts", "sh remote_merge.sh")
            self.execute_command_log(source_manager, f"{self.remote_path}/merge_scripts", "sh batch_execute_all.sh")

            # 导入合服后的 SQL 文件
            self.execute_command_log(source_manager, f"{self.remote_path}/merge_scripts", "sh import_sql.sh")
        finally:
            # 清理标记文件
            self.execute_command_log(source_manager, "/home", "rm -rf merging")
            source_manager.close()

    @property
    def logs(self):
        return self._logs


if __name__ == '__main__':
    merger = ServerMerger(
        remote_ip="",  # 远程主机 IP
        mysql_password="",  # MySQL root 密码
        prefix="",  # 数据库前缀
        start_id=1,  # 备份起始 ID
        end_id=19,  # 备份结束 ID
        dest_id="101",  # 合并后的 ID
        merge_ids=[],  # 需要合并的 ID 列表
        merged_ids=[],
        remote_password="",  # 远程主机密码
        remote_path="/home/merge",
        output_dir="merge_scripts",
    )
    merger.generate_scripts()
