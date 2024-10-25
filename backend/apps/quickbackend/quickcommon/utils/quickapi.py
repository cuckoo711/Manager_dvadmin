"""
Creation date: 2024/10/24
Creation Time: 下午3:39
DIR PATH: backend/apps/quickbackend/quickcommon/utils
Project Name: Manager_dvadmin
FILE NAME: quickapi.py
Editor: 30386
"""
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict
from urllib.parse import quote

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

    def get_channel_list(self, game_id) -> dict:
        """
        获取指定游戏的渠道列表。
        :param game_id: 游戏 ID
        :return: 渠道列表的字典
        """
        channel_dict = {}

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
                    channel_dict[channel_id] = {
                        'channel_name': channel_data[0][channel_id]['channel_name'],
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


if __name__ == '__main__':
    test = QuickLogin()
    print(test.load_game_data())
    print(test.get_cookie("jtgameMXY", "jtgame123"))
    # test.load_cookie(
    #     'SESSIONID=ouu99tq4o0j70r2j3evs8a0k62; '
    #     'expires=Fri, 25-Oct-2024 09:52:46 GMT; path=/; HttpOnly, '
    #     'loginUsername=k0%2BSwPeMVjKb7G%2Feo7B4nA%3D%3D; '
    #     'expires=Thu, 31-Oct-2024 09:52:46 GMT; path=/; httponly, '
    #     'authToken=Yl1u%2B37QS7t%2BcVUzUxPNMOVaxDfdToit%2F3jnZx%2FiY7e7AHJCx6K4R8BGLrMtetOlXyA2w3QNcreBZ%2FJMF6w9NnM9W8lRtu50WP0KE9oayZnZIscx8ki3jwp1bbVlCmmFcmNaf2cH6B1Ld9Q%2FJR0O7aVy%2F7R3xIa2zKNTNBtvEIh72s1ZoEkETaXqTH0VJk3g; '
    #     'expires=Fri, 24-Oct-2025 09:52:46 GMT; path=/; domain=.quicksdk.com')
    print(test.load_game_data())
    print(test.get_channel_list("65539"))
    print(test.switch_game("62033"))
    print(test.get_channel_list("65539"))
    print(test.get_channel_list("62033"))
