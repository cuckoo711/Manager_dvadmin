"""
Creation Date: 2025/1/9
Creation Time: 下午10:10
Dir Path: backend/apps/gamebackend/xgbackend/utils
Project Name: Manager_dvadmin_my
File Name: default.py
Editor: cuckoo
"""
from apps.gamebackend.xgbackend.utils.util import retry_xg
from dvadmin.utils.backends import logger


class XGDefault:
    def __init__(self, token_id):
        from apps.gamebackend.xgbackend.models import XGToken
        self.token_id = token_id
        self.token: XGToken | None = None
        self.url = ""
        self.default_return = {}

        self.reset_token()

    def func(self, **kwargs):
        ...

    def reset_token(self):
        from apps.gamebackend.xgbackend.models import XGToken
        self.token: XGToken = XGToken.objects.get(id=self.token_id)
        self.url = f'{self.token.game_server.server_host}/master'

    def run(self, **kwargs):

        @retry_xg(self.token_id, callback=self.reset_token)
        def _run():
            return self.func(**kwargs)

        try:
            return _run()
        except Exception as e:
            logger.error(f"请求失败: {e}")
            return self.default_return

    def __call__(self, token_id):
        logger(f"Processing token_id: {token_id}")
        return self
