"""
Creation Date: 2025/1/9
Creation Time: 下午10:09
Dir Path: backend/apps/gamebackend/xgbackend/utils
Project Name: Manager_dvadmin_my
File Name: getInfos.py
Editor: cuckoo
"""
from apps.gamebackend.xgbackend.utils.default import XGDefault


class ApiXGInfos(XGDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = {
            "GameName": self.token.game_server.gamename,
            "Servers": [],
        }
