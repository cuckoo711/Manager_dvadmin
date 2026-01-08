"""
Creation date: 2024/12/4
Creation Time: 下午5:07
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: delWifes.py
Editor: 30386
"""
from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiDelWifes(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    def __del_wifes(self, server: str, pname: str, wifeid: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 11, "type": 147, "server": server,
            "pname": pname, "wifeid": wifeid
        }
        response_json = self.get_action_request(params)
        return "msg" in response_json

    def __initialize_del_wifes(self, **kwargs):
        if self.token.is_active:
            return self.__del_wifes(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_del_wifes(**kwargs)
