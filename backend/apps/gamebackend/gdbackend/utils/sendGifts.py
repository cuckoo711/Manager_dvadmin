"""
Creation Date: 2024/11/29
Creation Time: 下午5:54
Dir Path: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin_my
File Name: sendGifts.py
Editor: cuckoo
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiSendGifts(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    def __send_gift(self, server: str, gifts_name: str, pname: str, gifts_id: str, des: str):
        params = {"key": self.token.get_token(), "cmd": 307, "username": self.token.user.username, "servers": server,
                  "type": 1, "giftsName": gifts_name, "pname": pname, "giftsID": gifts_id, "des": des}
        response_json = self.get_action_request(params)
        return "succ" in response_json

    def __initialize_send_gifts(self, **kwargs):
        if self.token.is_active:
            return self.__send_gift(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_send_gifts(**kwargs)
