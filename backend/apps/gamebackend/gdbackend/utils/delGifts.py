"""
Creation date: 2024/11/28
Creation Time: 下午5:33
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: delGifts.py
Editor: 30386
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiDelGifts(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    def __del_gift(self, gift_id: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 303,
            "username": self.token.user.username,
            "GP_ID": gift_id, "type": 5
        }
        response_json = self.get_action_request(params)
        return "msg" in response_json

    def __del_gifts(self, gift_ids: list):
        result = []
        for gift_id in gift_ids:
            result.append(self.__del_gift(gift_id))
        return all(result)

    def __initialize_del_gifts(self, **kwargs):
        if self.token.is_active:
            return self.__del_gifts(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_del_gifts(**kwargs)
