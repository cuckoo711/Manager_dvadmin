"""
Creation date: 2024/12/3
Creation Time: 下午5:13
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: getWifesList.py
Editor: 30386
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import change_json


class ApiGetWifesList(GDDefault):

    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = {
            "wifesall": [],
            "wifeshave": []
        }

    def __get_wifes_exist(self, server: str, pname: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 11,
            "type": 137,
            "server": server,
            "pname": pname
        }
        response_json = self.get_action_request(params)
        if response_json.get("msg") == "0" and "props" in response_json:
            return_list = [
                {
                    'label': wife['name'],
                    'value': wife['sid'],
                    'intimacy': wife['intimacy'],
                    'charm': wife['charm'],
                    'exp': wife['exp'],
                } for wife in response_json.get('props', [])
            ]
            return return_list
        else:
            raise Exception("获取已有红颜信息失败")

    def __get_all_wifes(self, server: str, pname: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 11,
            "type": 145,
            "server": server,
            "pname": pname
        }
        response_json = self.get_action_request(params)
        if response_json.get("msg") == "0" and "props" in response_json:
            return_list = change_json(
                master=response_json,
                father="props",
                key="name",
                value="sid",
                mode="list",
                sort=True
            )
            return return_list
        else:
            raise Exception("获取全部红颜信息失败")

    def __initialize_get_wifes_exist(self, server: str, pname: str):
        if self.token.is_active:
            return {
                "wifesall": self.__get_all_wifes(server, pname),
                "wifeshave": self.__get_wifes_exist(server, pname)
            }
        else:
            raise Exception("Token无效")

    def func(self, server: str, pname: str):
        return self.__initialize_get_wifes_exist(server, pname)
