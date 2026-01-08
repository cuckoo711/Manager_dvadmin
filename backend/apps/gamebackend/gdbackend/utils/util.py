"""
Creation Date: 2024/11/26
Creation Time: 10:36
Dir Path: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
File Name: util.py
Editor: buguniao
"""
import functools
import re
import time
from datetime import datetime, timedelta

import pypinyin


def extract_first_number(text):
    """ 提取字符串中的第一个数字组合，并转换成整数 """
    match = re.search(r'\d+', text)  # 使用 re.search 而不是 re.findall 以获取第一个匹配项
    return int(match.group()) if match else 0  # 如果找到匹配，则返回第一个数字部分，否则返回 0


def extract_first_segment(text):
    """ 提取字符串中第一次出现的由符号或数字隔开的文字组合 """
    match = re.split(r'[\d\W]+', text)  # 使用 re.split 按照符号或数字进行分割
    return match[0] if match else ''  # 如果找到匹配，则返回第一个文字部分


def custom_sort(text_tuple):
    """ 自定义排序函数，结合拼音和数字大小 """
    text = text_tuple[0]
    non_number_text = extract_first_segment(text)  # 只截取第一次匹配的文字部分
    letters = pypinyin.pinyin(non_number_text, style=pypinyin.Style.FIRST_LETTER)
    letters_str = ''.join(letter[0] for letter in letters if letter)
    first_number = extract_first_number(text)
    return letters_str, first_number


def custom_sort_dict(text_dict, sort_key):
    """ 自定义字典排序函数，结合拼音和数字大小 """
    text = text_dict[sort_key]
    non_number_text = extract_first_segment(text)  # 只截取第一次匹配的文字部分
    letters = pypinyin.pinyin(non_number_text, style=pypinyin.Style.FIRST_LETTER)
    letters_str = ''.join(letter[0] for letter in letters if letter)
    first_number = extract_first_number(text)
    return letters_str, first_number


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


def retry_gd(token_id, callback=None, max_retries=3, delay=1, exceptions=(Exception,)):
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
                        from apps.gamebackend.gdbackend.models import GDToken
                        token = GDToken.objects.get(id=token_id)
                        token.update_token()
                        time.sleep(delay)
                        if callback:
                            callback()
                    else:
                        print("已达到最大重试次数，操作失败。")
                        raise

        return wrapper

    return decorator


def change_json(master: dict, father: str, key: str, value: str, callback: callable = None,
                mode: str = "dict", sort: bool = False) -> dict | list:
    """
    转换返回的数据成想要的字典
    :param master: 总数据
    :param father: 数据标识
    :param key: 字典键
    :param value: 字典值
    :param callback: 回调函数
    :param mode: 返回模式
    :param sort: 排序
    :return: 字典 or 列表
    """
    output = {}
    output_list = []
    try:
        child_dicts = master.get(father, [])
        if not child_dicts:
            return {}

        for child_dict in child_dicts:
            if key in child_dict and value in child_dict:
                if callback:
                    output[child_dict[key]] = callback(child_dict[value])
                else:
                    output[child_dict[key]] = child_dict[value]

        if sort:
            output = dict(sorted(output.items(), key=custom_sort))

        for output_key, output_value in output.items():
            output_list.append({"label": output_key, "value": output_value})
        return output if mode == "dict" else output_list

    except KeyError:
        # 只捕获 KeyError 错误
        return {}


def add_seconds_to_date(base_date, seconds):
    """
    给定 datetime 对象和秒数，返回格式化后的日期字符串。
    """
    new_date = base_date + timedelta(seconds=seconds)
    return new_date.strftime('%Y-%m-%d %H:%M:%S')


def process_sublist(sublist, base_date):
    """
    处理子列表，生成所需结构化数据。
    """
    times = [
        add_seconds_to_date(base_date, int(sublist.get(key, 0)))
        for key in ['startTime', 'settleTime', 'endTime']
    ]
    return [
        sublist.get('activityId', ''),
        sublist.get('name', ''),
        sublist.get('description', ''),
        *times,
        sublist.get('params', '')
    ]


def process_lists(json_dict, date_str) -> dict:
    """
    处理嵌套字典，生成指定的结构化字典。
    """
    temp_dict = {key: [] for key in ['Normal', 'Alone', 'District', 'Cross']}

    if not json_dict:
        return temp_dict

    if isinstance(date_str, str):
        if '-' in date_str:
            base_date = datetime.strptime(date_str, '%Y-%m-%d')
        elif '/' in date_str:
            base_date = datetime.strptime(date_str, '%Y/%m/%d')
        else:
            raise ValueError(f"日期格式错误: {date_str}")
    elif isinstance(date_str, datetime):
        base_date = date_str
    else:
        raise ValueError(f"日期格式错误: {type(date_str)}")

    for key, sublists in json_dict.items():
        if key in temp_dict:
            temp_dict[key] = [process_sublist(sublist, base_date) for sublist in sublists]

    # 合并 Normal 和 Alone
    temp_dict['Alone'].extend(temp_dict['Normal'])

    return temp_dict
