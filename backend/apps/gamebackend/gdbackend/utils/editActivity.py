"""
Creation date: 2024/12/13
Creation Time: 上午11:54
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: editActivity.py
Editor: 30386
"""
from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiEditActivity(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    def __edit_activity(self, activityId: str, name: str, des: str, startTime: str,
                        endTime: str, disTime: str, param: str):
        params = {
            "key": self.token.get_token(), "cmd": 305, "type": 5, "activityId": activityId,
            "name": name, "des": des, "startTime": startTime, "endTime": endTime,
            "disTime": disTime, "param": param
        }
        response_json = self.get_action_request(params)
        return response_json.get("msg", "未知错误") == "0"

    def __initialize_edit_activity(self, **kwargs):
        if self.token.is_active:
            return self.__edit_activity(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_edit_activity(**kwargs)
