"""
Creation date: 2024/12/13
Creation Time: 下午12:55
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: delActivity.py
Editor: 30386
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiDelActivity(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    def __del_activity(self, activityId: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 305,
            "type": 31,
            "activityid": activityId,
        }
        response_json = self.get_action_request(params)
        return response_json.get("msg", "未知错误") == "0"

    def __initialize_del_activity(self, **kwargs):
        if self.token.is_active:
            return self.__del_activity(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_del_activity(**kwargs)
