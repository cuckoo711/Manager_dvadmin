"""
Creation date: 2024/11/28
Creation Time: 下午4:45
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: getPinfo.py
Editor: 30386
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import change_json


class ApiGDPInfos(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = ("无效", "无效")

    def __get_pinfo(self, server: str, pid: str):
        params = {"key": self.token.get_token(), "cmd": 208, "serverid": server, "page": 0, "id": pid, "username": "",
                  "name": "", "lv1": "", "lv2": "", "login1": "", "login2": "", "t1": "", "t2": ""}
        response_json = self.get_action_request(params)
        data_temp = change_json(
            master=response_json,
            father="players",
            key="pid",
            value="name"
        )
        if data_temp:
            params = {"key": self.url, "cmd": 11, "type": 1, "server": server, "pname": data_temp[pid]}
            response_json = self.get_action_request(params)
            try:
                return response_json["pname"], (int(response_json["vipExp"]) - 400000)
            except Exception:
                return response_json["pname"], "无效"
        else:
            return self.default_return

    def __initialize_info_dict(self, **kwargs):
        if self.token.is_active:
            return self.__get_pinfo(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_info_dict(**kwargs)
