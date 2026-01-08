"""
Creation Date: 2024/11/26
Creation Time: 10:34
Dir Path: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
File Name: login.py
Editor: buguniao
"""

import json
from urllib.parse import urlencode

import requests

from apps.gamebackend.gdbackend.utils.util import retry
from dvadmin.utils.backends import logger


@retry()
def update_token(host: str, username: str, password: str) -> str:
    """
    获取token
    :return:
    """
    url_temp = urlencode(
        {
            "action": 1,
            "name": username,
            "passwd": password,
        }
    )
    # noinspection HttpUrlsUsage
    head_url = f'http://{host}:8801/login?{url_temp}'
    logger.debug(f"请求地址: {head_url}")
    login_response = requests.get(head_url)
    response_dict = json.loads(login_response.text.strip("()").replace("'", '"'))
    if "key" in response_dict:
        key_token = response_dict["key"]
        return key_token
    else:
        raise Exception("获取token失败")
