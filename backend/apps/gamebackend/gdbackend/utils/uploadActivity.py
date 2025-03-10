"""
Creation date: 2024/12/16
Creation Time: 上午10:52
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: uploadActivity.py
Editor: 30386
"""
from collections import defaultdict

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import change_json


class ApiUploadActivity(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = {
            "status": False,
            "log": ["上传失败"]
        }
        self.__servers_len = 0

    def __get_servers(self):
        params = {"key": self.token.get_token(), "cmd": 200, "type": 0}
        response_json = self.get_action_request(params)
        return_data = change_json(
            master=response_json,
            father="servers",
            key="id",
            value="name",
        )
        if return_data:
            return return_data
        else:
            raise Exception("获取servers失败")

    def __get_range_values(self, key, ranges) -> str:
        servers = self.__get_servers()
        self.__servers_len = len(servers)
        keys = list(servers.keys())
        index = keys.index(key)
        start = max(0, index - ranges + 1)
        return '' if len(keys[start:index + 1]) < ranges else ':'.join(keys[start:index + 1])

    def __normal_upload(self, server: str, data: list):
        updata = "/r/n".join("/t".join('%s' % value for value in list_temp) for list_temp in data)
        params = {
            "key": self.token.get_token(),
            "cmd": 305,
            "type": 7,
            "username": self.token.user.username,
            "data": updata,
            "server": server
        }
        response_json = self.get_action_request(params)
        return response_json.get("msg")

    def __special_upload(self, servers: str, datas: list, activity_type: int):
        params = {"key": self.token.get_token(), "username": self.token.user.username, "server": servers, "cmd": 305,
                  "type": 2, "actvitiytype": activity_type, "activityid": datas[0], "name": datas[1], "des": datas[2],
                  "startTime": datas[3], "endTime": datas[4], "disTime": datas[5], "param": datas[6]}
        response_json = self.get_action_request(params)
        return response_json.get("msg")

    def __upload_activity(self, servers: str | list, datas: dict, range_start: str, range_end: str):
        all_servers = [str(_) for _ in list(self.__get_servers().keys())]
        result = {
            "status": False,
            "log": defaultdict(list)
        }
        if isinstance(servers, str):
            server_list = servers.split(",")
        elif isinstance(servers, list):
            server_list = servers
        else:
            raise Exception("服务器列表格式错误")
        result['log']['base'] = [
            f"共有区服: {self.__servers_len}",
            f"小跨服区间: {range_start}",
            f"大跨服区间: {range_end}",
            f"上传区服: {','.join(server_list)}"
        ]
        try:
            for server in server_list:
                server = server.strip()
                normal_full = self.__normal_upload(server, datas.get('Alone'))
                if normal_full == "1":
                    normal_half = self.__normal_upload(server, datas.get('Normal'))
                    if normal_half and normal_half == "0":
                        result['log'][server].append("续开活动已导入")
                    else:
                        result['log'][server].append("日常活动已存在")
                elif normal_full == "0":
                    result['log'][server].append("首发活动已导入")
                else:
                    result['log'][server].append(f"日常活动返回错误: {normal_full}")

                index = all_servers.index(server) + 1
                result['log'][server].append(f"当前区服ID: {server}, 索引: {index}")
                if int(range_start) == 0 or int(range_end) == 0:
                    result['log'][server].append("跨服区间未设置, 跳过")
                    continue
                if index % int(range_start) == 0:
                    servers_value = self.__get_range_values(server, int(range_start))
                    districts = [
                        self.__special_upload(servers_value, data, 13) for data in datas.get('District')
                    ]
                    if districts.count("0") == len(districts):
                        result['log'][server].append("小跨服活动已导入")
                    elif districts.count("1") == len(districts):
                        result['log'][server].append("小跨服活动已存在")
                    else:
                        result['log'][server].append(f"小跨服活动返回错误: {';'.join(districts)}")
                else:
                    result['log'][server].append("非小跨服区间, 跳过")
                if index % int(range_end) == 0:
                    servers_value = self.__get_range_values(server, int(range_end))
                    cross = [
                        self.__special_upload(servers_value, data, 14) for data in datas.get('Cross')
                    ]
                    if cross.count("0") == len(cross):
                        result['log'][server].append("大跨服活动已导入")
                    elif cross.count("1") == len(cross):
                        result['log'][server].append("大跨服活动已存在")
                    else:
                        result['log'][server].append(f"大跨服活动返回错误: {';'.join(cross)}")
                else:
                    result['log'][server].append("非大跨服区间, 跳过")
            result['status'] = True
            result['message'] = "上传成功"
        except Exception as e:
            result['status'] = False
            result['message'] = f"上传失败: {e}"
        return result

    def __initialize_upload_activity(self, **kwargs):
        if self.token.is_active:
            return self.__upload_activity(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_upload_activity(**kwargs)
