"""
Creation date: 2024/10/24
Creation Time: 下午4:09
DIR PATH: backend/apps/quickbackend/quickcommon/utils
Project Name: Manager_dvadmin
FILE NAME: utils.py
Editor: 30386
"""
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
    except Exception as e:
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })
    return session
