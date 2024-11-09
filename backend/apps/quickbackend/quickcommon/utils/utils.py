"""
Creation date: 2024/10/24
Creation Time: 下午4:09
DIR PATH: backend/apps/quickbackend/quickcommon/utils
Project Name: Manager_dvadmin
FILE NAME: utils.py
Editor: 30386
"""
from copy import deepcopy

import requests
from fake_useragent import UserAgent


def initialize_session():
    """
    初始化请求会话，并设置随机的 User-Agent。
    :return: requests.Session 对象
    """
    user_agent = UserAgent()
    session = requests.Session()
    try:
        session.headers.update({
            "User-Agent": user_agent.random
        })
    except Exception:
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })
    return session


def mix_channel_status(full_data: dict, channel_data: dict, batch_switch_type: str):
    """
    将渠道数据合并到完整数据中。
    :param full_data: 完整数据
    :param channel_data: 渠道数据
    :param batch_switch_type: 批量开关类型
    :return: 合并后的数据
    """
    batch_switch_type_mapping = {
        '0': ('no_register', True),
        '1': ('no_pay', True),
        '2': ('no_login', True),
        '3': ('no_register', False),
        '4': ('no_pay', False),
        '5': ('no_login', False),
    }
    for key, value in channel_data.items():
        value[batch_switch_type_mapping[batch_switch_type][0]] = batch_switch_type_mapping[batch_switch_type][1]
        full_data[key] = value

    mixed_data = {}
    for key, value in full_data.items():
        mixed_data[key] = [value['no_login'], value['no_pay'], value['no_register']]
    return mixed_data


def replace_game_data(game_data: list):
    """
    替换游戏
    :param game_data: 游戏数据
    :return: 替换后的数据
    """
    from apps.jtgame.game_manage.models import Games
    replace_data = []
    games = Games.objects.all()
    for data in game_data:
        game_quickname = data['gameName']
        for game in games:
            if game_quickname == game.quick_name:
                replace_data.append({"gameName": game.name, "productId": data['productId']})
                break
        else:
            # replace_data.append(data)
            if '01' in game_quickname:
                replace_data.append(deepcopy({
                    "gameName": game_quickname.replace('01', '0.1'),
                    "productId": data['productId']
                }))
            elif '005' in game_quickname:
                replace_data.append({
                    "gameName": game_quickname.replace('005', '0.05'),
                    "productId": data['productId']
                })
            else:
                replace_data.append(data)
    return replace_data
