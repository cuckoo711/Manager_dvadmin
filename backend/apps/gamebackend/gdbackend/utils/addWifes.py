"""
Creation date: 2024/12/4
Creation Time: 下午5:06
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: addWifes.py
Editor: 30386
"""
import json
import re

from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiAddWifes(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    @staticmethod
    def __wash_response(response: str):
        match = re.search(r'\{.*}', response)
        if match:
            response_json = json.loads(match.group(), strict=False)
            return response_json
        else:
            return {}

    def __add_wifes(self, server: str, pname: str, wifeid: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 11, "type": 146, "server": server,
            "pname": pname, "wifeid": wifeid
        }
        response_json = self.get_action_request(params, rep=self.__wash_response)
        return "msg" in response_json

    def __initialize_add_wifes(self, **kwargs):
        if self.token.is_active:
            return self.__add_wifes(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_add_wifes(**kwargs)
