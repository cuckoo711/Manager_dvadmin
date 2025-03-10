"""
Creation Date: 2024/12/19
Creation Time: 下午5:30
Dir Path: linker
Project Name: DSLH_Merge
File Name: filelinker.py
Editor: cuckoo
"""
import os
import shutil
import stat

import paramiko
from tqdm import tqdm


class RemoteFileManager:
    def __init__(self, ip, password, username="root"):
        self.ip = ip
        self.password = password
        self.username = username
        self.ssh_client = None
        self.sftp_client = None
        self._connect()

    def _connect(self):
        """建立 SSH 和 SFTP 连接"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.ip, username=self.username, password=self.password)
            self.sftp_client = self.ssh_client.open_sftp()
        except Exception as e:
            raise Exception(f"连接远程服务器失败: {e}")

    def check_file_exists(self, remote_path, file_name):
        try:
            full_path = f"{remote_path}/{file_name}"
            self.sftp_client.stat(full_path)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking existence: {e}")
            return False

    def execute_command(self, path, command):
        """
        在指定路径下执行传入的命令。
        :param path: 指定的路径
        :param command: 要执行的命令
        :return: 命令输出
        """
        if self.ssh_client:
            try:
                full_command = f"cd {path} && {command}"
                print(f"Executing command: {full_command}")
                stdin, stdout, stderr = self.ssh_client.exec_command(full_command)
                output = stdout.read().decode()
                error = stderr.read().decode()
                print(output.strip())
                if error:
                    print(f"命令执行警告&错误: \n{error}")
                else:
                    print(f"命令执行成功, 暂无警告&错误")
                return {"output": output.strip(), "error": error}
            except Exception as e:
                print(f"执行命令时发生错误: {e}")
        else:
            print("SSH连接未建立，无法执行命令")

    def _remote_path_exists(self, path):
        """检查远程路径是否存在"""
        try:
            self.sftp_client.stat(path)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def _local_path_exists(path):
        """检查本地路径是否存在"""
        return os.path.exists(path)

    def download(self, remote_path, local_path):
        """将远程文件/文件夹下载到本地"""
        if not self._remote_path_exists(remote_path):
            raise FileNotFoundError(f"远程路径不存在: {remote_path}")

        # 如果本地路径存在，删除并重新创建
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        os.makedirs(local_path, exist_ok=True)

        def _download_dir(remote_dir, local_dir):
            items = self.sftp_client.listdir_attr(remote_dir)
            with tqdm(total=len(items), desc=f"Downloading {remote_dir}") as pbar:
                for item in items:
                    remote_item = f"{remote_dir}/{item.filename}"
                    local_item = os.path.join(local_dir, item.filename)
                    if stat.S_ISDIR(item.st_mode):
                        os.makedirs(local_item, exist_ok=True)
                        _download_dir(remote_item, local_item)  # 递归下载
                    else:
                        self.sftp_client.get(remote_item, local_item)
                    pbar.update(1)

        if self._is_remote_directory(remote_path):
            _download_dir(remote_path, local_path)
        else:
            self.sftp_client.get(remote_path, os.path.join(local_path, os.path.basename(remote_path)))

    def mkdir(self, remote_path):
        if not self._remote_path_exists(remote_path):
            try:
                self.sftp_client.mkdir(remote_path)
            except FileNotFoundError:
                parent_path = os.path.dirname(remote_path)
                self.mkdir(parent_path)
                self.sftp_client.mkdir(remote_path)

    def upload(self, local_path, remote_path):
        """将本地文件/文件夹上传到远程"""
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"本地路径不存在: {local_path}")

        # 确保远程路径存在
        if not self._remote_path_exists(remote_path):
            self.mkdir(remote_path)

        def _upload_dir(local_dir, remote_dir):
            items = os.listdir(local_dir)
            with tqdm(total=len(items), desc=f"Uploading {local_dir}") as pbar:
                for item in items:
                    local_item = os.path.join(local_dir, item)
                    remote_item = f"{remote_dir}/{item}".replace("\\", "/")  # 修复路径拼接
                    if os.path.isdir(local_item):
                        if not self._remote_path_exists(remote_item):
                            self.sftp_client.mkdir(remote_item)
                        _upload_dir(local_item, remote_item)
                    else:
                        self.sftp_client.put(local_item, remote_item)
                    pbar.update(1)

        if os.path.isdir(local_path):
            _upload_dir(local_path, remote_path)
        else:
            # 如果是文件，直接上传到目标路径内
            file_name = os.path.basename(local_path)
            remote_file_path = f"{remote_path}/{file_name}".replace("\\", "/")
            self.sftp_client.put(local_path, remote_file_path)

    def _remove_remote_path(self, path):
        """递归删除远程文件夹或文件"""
        try:
            if self._is_remote_directory(path):
                for item in self.sftp_client.listdir_attr(path):
                    remote_item = f"{path}/{item.filename}"
                    if stat.S_ISDIR(item.st_mode):
                        self._remove_remote_path(remote_item)
                    else:
                        self.sftp_client.remove(remote_item)
                self.sftp_client.rmdir(path)
            else:
                self.sftp_client.remove(path)
        except Exception as e:
            print(f"Failed to remove remote path {path}: {e}")

    def _is_remote_directory(self, path):
        """检查远程路径是否为目录"""
        try:
            mode = self.sftp_client.stat(path).st_mode
            return stat.S_ISDIR(mode)
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking if remote path is directory: {e}")
            return False

    def close(self):
        """关闭连接"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
        except Exception:
            pass
        try:
            if self.ssh_client:
                self.ssh_client.close()
        except Exception:
            pass

    def __del__(self):
        self.close()
