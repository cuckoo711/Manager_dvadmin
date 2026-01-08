"""
Creation date: 2024/12/3
Creation Time: 上午11:03
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: addGifts.py
Editor: 30386
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiAddGifts(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    def __add_gift(self, gift_name: str, gift_des: str, gift_content: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 303,
            "GP_name": gift_name,
            "username": self.token.user.username,
            "GP_bookdes": gift_des,
            "type": 1,
            "GP_gift": gift_content
        }
        response_json = self.get_action_request(params)
        return "msg" in response_json

    def __initialize_add_gifts(self, **kwargs):
        if self.token.is_active:
            return self.__add_gift(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_add_gifts(**kwargs)
