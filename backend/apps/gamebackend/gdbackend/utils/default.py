"""
Creation Date: 2024/11/26
Creation Time: 11:30
Dir Path: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
File Name: default.py
Editor: buguniao
"""
import json
from typing import Union
from urllib.parse import urlencode

import requests

from apps.gamebackend.gdbackend.utils.util import retry_gd
from dvadmin.utils.backends import logger


class GDDefault:
    def __init__(self, token_id):
        from apps.gamebackend.gdbackend.models import GDToken
        self.token_id = token_id
        self.token: GDToken | None = None
        self.url = ""
        self.default_return = {}

        self.reset_token()

    def get_action_request(self, params: dict, rep: Union[bool, callable] = False) -> dict:
        url_temp = urlencode(params)
        head_url = f'{self.url}action?{url_temp}'
        response = requests.get(url=head_url)
        response.encoding = "utf-8"
        try:
            if isinstance(rep, bool):
                if rep:
                    return json.loads(response.text.replace("'", '"'))
                else:
                    return response.json(strict=False)
            else:
                return rep(response.text)
        except Exception as e:
            logger.error(f"请求失败: {e}, response: {response.text}")
            raise e

    def get_login_request(self, params: dict, rep: Union[bool, callable] = False) -> dict:
        url_temp = urlencode(params)
        head_url = f'{self.url}login?{url_temp}'
        response = requests.get(url=head_url)
        response.encoding = "utf-8"
        try:
            if isinstance(rep, bool):
                if rep:
                    return json.loads(response.text.replace("'", '"'))
                else:
                    return response.json(strict=False)
            else:
                return rep(response.text)
        except Exception as e:
            logger.error(f"请求失败: {e}, response: {response.text}")
            raise e

    def func(self, **kwargs):
        ...

    def reset_token(self):
        from apps.gamebackend.gdbackend.models import GDToken
        self.token = GDToken.objects.get(id=self.token_id)
        self.url = f'http://{self.token.game_server.server_host}:8801/'

    def run(self, **kwargs):

        @retry_gd(self.token_id, callback=self.reset_token)
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
