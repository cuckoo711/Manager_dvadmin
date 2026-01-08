"""
Creation Date: 2025/1/8
Creation Time: 下午9:35
Dir Path: backend/apps/gamebackend/xgbackend/utils
Project Name: Manager_dvadmin_my
File Name: util.py
Editor: cuckoo
"""
import functools
import time


def retry(max_retries=3, delay=1, exceptions=(Exception,)):
    """
    一个用于重试失败操作的装饰器。

    :param max_retries: 最大重试次数，默认为 3
    :param delay: 重试前的等待时间（秒），默认为 1 秒
    :param exceptions: 需要捕获进行重试的异常类型，默认为 Exception
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    print(f"尝试第 {attempts} 次调用 '{func.__name__}' 失败: {e}")
                    if attempts < max_retries:
                        time.sleep(delay)
                    else:
                        print("已达到最大重试次数，操作失败。")
                        raise

        return wrapper

    return decorator


def retry_xg(token_id, callback=None, max_retries=3, delay=1, exceptions=(Exception,)):
    """
    一个用于重试失败操作的装饰器。

    :param token_id: token_id, 用于更新token
    :param callback: 回调函数
    :param max_retries: 最大重试次数，默认为 3
    :param delay: 重试前的等待时间（秒），默认为 1 秒
    :param exceptions: 需要捕获进行重试的异常类型，默认为 Exception
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    print(f"尝试第 {attempts} 次调用 '{func.__name__}' 失败: {e}, {e.__class__.__name__}")
                    if attempts < max_retries:
                        from apps.gamebackend.xgbackend.models import XGToken
                        token = XGToken.objects.get(id=token_id)
                        token.update_token()
                        time.sleep(delay)
                        if callback:
                            callback()
                    else:
                        print("已达到最大重试次数，操作失败。")
                        raise

        return wrapper

    return decorator
