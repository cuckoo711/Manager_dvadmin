"""
Creation date: 2024/10/24
Creation Time: 下午3:39
DIR PATH: backend/apps/quickbackend/quickcommon/utils
Project Name: Manager_dvadmin
FILE NAME: quickapi.py
Editor: 30386
"""
import csv
import uuid
from datetime import datetime, timedelta
from io import BytesIO, TextIOWrapper
from typing import Dict, Tuple, List, Any
from urllib import parse
from urllib.parse import quote
from zipfile import ZipFile

import chardet
import pandas as pd
from PIL import Image
from bs4 import BeautifulSoup, Tag
from ddddocr import DdddOcr

from apps.quickbackend.quickcommon.utils.utils import initialize_session


class QuickLogin:
    def __init__(self):
        self.session = initialize_session()

    def load_cookie(self, cookie: str):
        self.session.cookies.clear()
        self.session.cookies.update({k: v for k, v in [cookie.split('=') for cookie in cookie.split('; ')]})

    def get_captcha_code(self):
        """
        获取验证码并进行识别，最多尝试 3 次。
        :return: 识别的验证码
        """
        for attempt in range(3):
            try:
                response = self.session.get(url="https://www.quicksdk.com/base/scode", timeout=10)
                response.raise_for_status()
                captcha_image = Image.open(BytesIO(response.content))
                ocr = DdddOcr(show_ad=False)
                captcha_code_raw = ocr.classification(captcha_image)
                captcha_code = captcha_code_raw.replace(' ', '').strip()
                if len(captcha_code) == 4:
                    return captcha_code
            except Exception as e:
                print(f"验证码识别失败: {e}")

        raise ValueError("验证码连续识别失败 3 次")

    def get_cookie(self, username, password) -> tuple[str, datetime] | tuple[None, None]:
        for attempt in range(5):
            self.session.cookies.clear()
            cookies, expires_datetime = self._login(username, password)
            if cookies and expires_datetime:
                return cookies, expires_datetime
        return None, None

    def _login(self, username, password) -> tuple[str, datetime] | tuple[None, None]:
        try:
            login_data = {
                "username": username,
                "password": password,
                "checkCode": self.get_captcha_code(),
                "referUrl": "https://www.quicksdk.com/index.html"
            }
            response = self.session.post(url="https://www.quicksdk.com/loginHandle.do", data=login_data, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()

            if response.json().get('status'):
                set_cookie_header = response.headers.get('Set-Cookie')
                cookies = {}
                [cookies.update({k: v}) for k, v in
                 [cookie.split('=') for cookie in set_cookie_header.split('; ')]
                 if k not in cookies]
                expires = cookies.get('expires')
                expires_datetime = None

                if expires:
                    expires_datetime = datetime.strptime(expires, "%a, %d-%b-%Y %H:%M:%S GMT") + timedelta(hours=8)

                return set_cookie_header, expires_datetime
            else:
                raise ValueError("登录失败")
        except ValueError as e:
            print(f"登录失败: {e}")
        return None, None

    def load_game_data(self) -> list[Dict[str, str]]:
        """
        获取游戏字典信息，存储在类的属性中。
        :return: None
        """
        games_by_id = []
        try:
            response = self.session.get(url="https://www.quicksdk.com/system/dashboard", timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            game_elements = soup.select('.gpad-btm a')
            # replacements = {"01": "0.1", "005": "0.05"}
            for game in game_elements:
                game_title = game.get('title')
                product_id = game.get('productid')
                if game_title is None or product_id is None:
                    continue
                game_title = game_title.strip()
                games_by_id.append({'gameName': game_title, 'productId': product_id})
                # for old, new in replacements.items():
                #     if old in game_title:
                #         games_by_id.append({'gameName': game_title.replace(old, new), 'productId': product_id})
            return games_by_id
        except Exception as e:
            print(f"获取游戏数据失败: {e}")
            return []

    def switch_game(self, game_id) -> bool:
        """
        切换当前游戏到指定的游戏。
        :param game_id: 要切换的游戏 ID
        :return: 是否切换成功
        """
        try:
            response = self.session.get(url=f"https://www.quicksdk.com/system/changeGame?productId={game_id}",
                                        timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
            if response.json().get('status'):
                return True
        except Exception as e:
            print(f"切换游戏失败: {e}")
        return False

    def get_channel_list(self, game_id, channel_suffixs: list = None) -> dict:
        """
        获取指定游戏的渠道列表。
        :param game_id: 游戏 ID
        :param channel_suffixs: 渠道列表的后缀
        :return: 渠道列表的字典
        """
        channel_dict = {}
        if not channel_suffixs:
            channel_suffixs = ['全部']

        try:
            response = self.session.get(url=f"https://www.quicksdk.com/gameSet/editStopUser/gid/{game_id}?isFrame=1",
                                        timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            channel_sections = soup.select('dd.mt10')
            if len(channel_sections) != 3:
                return channel_dict

            channel_data = [self.parse_channel_data(section) for section in channel_sections]
            if all(len(data) == len(channel_data[0]) for data in channel_data):
                for channel_id in channel_data[0]:
                    add = False
                    channel_name = channel_data[0][channel_id]['channel_name']
                    if '全部' not in channel_suffixs:
                        if '无后缀' in channel_suffixs:
                            if not any(suffix in channel_name for suffix in channel_suffixs if suffix != '无后缀'):
                                add = True
                        else:
                            if any(suffix in channel_name for suffix in channel_suffixs):
                                add = True
                    else:
                        add = True
                    if add:
                        channel_dict[channel_id] = {
                            'channel_name': channel_name,
                            'no_login': channel_data[0][channel_id]['channel_status'],
                            'no_pay': channel_data[1][channel_id]['channel_status'],
                            'no_register': channel_data[2][channel_id]['channel_status']
                        }
        except Exception as e:
            print(f"获取渠道列表失败: {e}")
        return channel_dict

    @staticmethod
    def parse_channel_data(channel_soup: Tag) -> dict:
        """
        从渠道的 HTML 标签中解析出渠道字典。
        :param channel_soup: 包含渠道信息的 HTML 标签
        :return: 渠道信息字典
        """
        channel_dict = {}
        for channel in channel_soup.select('div.channelList'):
            channel_input = channel.select_one('input.selectGameCheck.checkboxType')
            if channel_input:
                channel_dict[channel_input.get('value')] = {
                    'channel_name': channel.select_one('label.channelBtn').text.strip(),
                    'channel_status': channel_input.get('checked') is not None
                }
        return channel_dict

    def update_channel_status(self, game_id, channel_statuses: dict, status_texts=None) -> bool:
        """
        修改指定游戏的渠道状态。
        :param game_id: 游戏名称
        :param channel_statuses: 渠道状态字典，包含各渠道的状态信息
        :param status_texts: 可选的文本字典，包含各状态的描述文本
        :return: 是否修改成功
        """
        # 使用默认参数以减少不必要的重复
        status_texts = status_texts or {
            'no_login': '渠道禁止登录',
            'no_pay': '渠道禁止充值',
            'no_register': '渠道禁止注册'
        }
        encoded_texts = {key: quote(text, encoding='utf-8') for key, text in status_texts.items()}

        data_params = self._construct_data_params(
            channel_statuses,
            encoded_texts['no_login'],
            encoded_texts['no_pay'],
            encoded_texts['no_register'],
            game_id
        )
        encoded_data = '&'.join(filter(None, data_params))

        try:
            with self.session.post(
                    url="https://www.quicksdk.com/gameSet/editStopUserDo",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data=encoded_data,
                    timeout=10
            ) as response:
                response.encoding = 'utf-8'
                response.raise_for_status()
                if "成功" in response.text:
                    return True
        except Exception as e:
            print(f"修改渠道状态失败: {e}")
        return False

    @staticmethod
    def _construct_data_params(channel_statuses, no_login_text, no_pay_text, no_register_text, game_id):
        """
        构造渠道状态的数据参数列表，减少代码重复。
        :param channel_statuses: 渠道状态字典
        :param no_login_text: 禁止登录文本
        :param no_pay_text: 禁止充值文本
        :param no_register_text: 禁止注册文本
        :param game_id: 游戏ID
        :return: 数据参数列表
        """
        data_params = []

        extra_keys = ['noLoginExtra', 'noPayExtra', 'noNewUserExtra']
        status_keys = ['noLogin', 'noPay', 'noNewUser']
        texts = [no_login_text, no_pay_text, no_register_text]

        for channel_id, statuses in channel_statuses.items():
            for i, status in enumerate(statuses):
                data_params.append(f'{extra_keys[i]}[{channel_id}]='
                                   f'{" " if not status else texts[i]}')
                if status:
                    data_params.append(f'{status_keys[i]}[]='
                                       f'{channel_id}')

        data_params += [
            f'noLoginTxt={no_login_text}',
            f'noPayTxt={no_pay_text}',
            f'noNewUserTxt={no_register_text}',
            f'productId={game_id}'
        ]

        return data_params

    def get_player_data_by_any(self, view: str, txt: str) -> str | tuple[list[Any], list[Any]]:
        """
        获取指定玩家 ID 的玩家数据。
        :param view: 视图名称
        :param txt: 搜索文本
        :return: 玩家数据字典
        """
        try:
            base_url = ("https://www.quicksdk.com/baseData/importOrderList/channelId/0/"
                        "btime/2020-01-01%2000:00:00/etime/2030-12-31%2023:59:59/"
                        f"payStatus/4/checkView/{view}/" +
                        (f"viewtxt/{parse.quote(txt)}/" if txt else '') +
                        f"platform/0/isAjax/1")
            data_params = {
                'fileName': uuid.uuid4().hex,
                'itemList': '1,2,3,4,5,6,7,8,9,10,11,12,13,14',
                'pageRows': '1000',
                'format': 'csv'
            }
            data_str = parse.urlencode(data_params)
            response = self.session.get(url=f"{base_url}?{data_str}", timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()

            response_json = response.json()
            if response_json.get('status'):
                data_url = response_json.get('url')
                load_data_url = f"https://www.quicksdk.com{data_url}"
                player_data_full, player_data_mix = [], []
                for io in self._load_data_url(load_data_url):
                    _player_data_full, _player_data_mix = self._parse_player_data(io)
                    player_data_full.extend(_player_data_full)
                    player_data_mix.extend(_player_data_mix)
                player_data = player_data_full, player_data_mix
            else:
                return f"获取玩家数据失败: {response_json.get('error')}"

        except Exception as e:
            return f"获取玩家数据失败: {e}"

        return player_data

    def _load_data_url(self, url: str) -> list[BytesIO]:
        """
        从指定的 URL 下载数据并返回 BytesIO 对象列表。
        :param url: 数据的 URL
        :return: 包含数据的 BytesIO 对象列表
        """
        if not url:
            return []

        response = self.session.get(url=url, timeout=60)
        response.raise_for_status()

        if url.endswith('csv'):
            return [BytesIO(response.content)]
        elif url.endswith('zip'):
            bytes_io_list = []
            with ZipFile(BytesIO(response.content)) as zip_file:
                for file_name in zip_file.namelist():
                    with zip_file.open(file_name) as file:
                        bytes_io_list.append(BytesIO(file.read()))

            return bytes_io_list
        else:
            return []

    @staticmethod
    def _parse_player_data(io: BytesIO) -> tuple[list, list]:
        """
        从玩家数据的 HTML 标签中解析出玩家数据字典。
        :param io: 包含玩家数据的 csv 文件
        :return: 玩家数据字典
        """
        io.seek(0)  # 确保 BytesIO 的指针在开头
        raw_data = io.read()  # 读取所有字节
        result = chardet.detect(raw_data)
        encoding = result['encoding']

        player_data = []
        with TextIOWrapper(BytesIO(raw_data), encoding=encoding) as text_io:
            csv_reader = csv.reader(text_io)
            for row in csv_reader:
                player_data.append([_.strip() for _ in row])

        header = player_data.pop(0)
        player_data = [dict(zip(header, row)) for row in player_data]

        df = pd.DataFrame(player_data)
        df['创建'] = pd.to_datetime(df['创建'])
        df['创建日期'] = df['创建'].dt.date
        df['金额'] = df['金额'].str.replace(',', '')
        df['金额'] = df['金额'].str.extract(r'(\d+\.\d+|\d+)')
        df['金额'] = df['金额'].astype(float)

        result = df.groupby(['渠道', '区服', '用户 UID', '角色', '创建日期'])['金额'].sum().reset_index()
        result['金额'] = result['金额'].astype(float)

        return player_data, result.to_dict(orient='records')


if __name__ == '__main__':
    test = QuickLogin()
    print(test.get_cookie("jtgameMXY", "jtgame123"))
    # test.load_cookie(
    #     'SESSIONID=ouu99tq4o0j70r2j3evs8a0k62; '
    #     'expires=Fri, 25-Oct-2024 09:52:46 GMT; path=/; HttpOnly, '
    #     'loginUsername=k0%2BSwPeMVjKb7G%2Feo7B4nA%3D%3D; '
    #     'expires=Thu, 31-Oct-2024 09:52:46 GMT; path=/; httponly, '
    #     'authToken=Yl1u%2B37QS7t%2BcVUzUxPNMOVaxDfdToit%2F3jnZx%2FiY7e7AHJCx6K4R8BGLrMtetOlXyA2w3QNcreBZ%2FJMF6w9NnM9W8lRtu50WP0KE9oayZnZIscx8ki3jwp1bbVlCmmFcmNaf2cH6B1Ld9Q%2FJR0O7aVy%2F7R3xIa2zKNTNBtvEIh72s1ZoEkETaXqTH0VJk3g; '
    #     'expires=Fri, 24-Oct-2025 09:52:46 GMT; path=/; domain=.quicksdk.com')
    print(test.load_game_data())
    print(test.switch_game("70099"))
    print(test.get_player_data_by_any("roleName", ""))
