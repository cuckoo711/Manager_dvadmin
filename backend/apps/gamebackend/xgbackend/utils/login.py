"""
Creation Date: 2025/1/8
Creation Time: 下午9:35
Dir Path: backend/apps/gamebackend/xgbackend/utils
Project Name: Manager_dvadmin_my
File Name: login.py
Editor: cuckoo
"""
import os
import time

from ddddocr import DdddOcr
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromiumOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

from application.settings import BASE_DIR
from apps.gamebackend.xgbackend.utils.util import retry
from dvadmin.utils.backends import logger


class UpdateCookie:
    def __init__(self, url: str, user: str, password: str):
        options = ChromiumOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-javascript')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-webgl')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--incognito')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        chrome_path = os.path.join(BASE_DIR, 'chrome', 'chrome-linux', 'chrome')
        chromedriver_path = os.path.join(BASE_DIR, 'chrome', 'chromedriver_linux64', 'chromedriver')

        os.environ["CHROME_BIN"] = chrome_path
        os.environ["webdriver.chrome.driver"] = chromedriver_path

        options.binary_location = chrome_path
        service = ChromeService(executable_path=chromedriver_path)

        self.url = url
        self.user = user
        self.password = password
        self.driver = Chrome(options=options, service=service)

    def input_text(self, element_id, text):
        """
        写入
        """
        element = self.driver.find_element(By.ID, element_id)
        element.clear()
        element.send_keys(text)

    def get_captcha(self):
        """
        获取图片验证码
        """
        image_element = self.driver.find_element(By.ID, "img")
        screenshot = image_element.screenshot_as_png
        image_code = (DdddOcr(show_ad=False).classification(img=screenshot)).replace(' ', '')
        if len(image_code) != 4:
            self.driver.find_element(By.ID, "img").click()
            return self.get_captcha()
        return image_code

    def captcha_login(self):
        """
        处理验证码登录
        """
        captcha_text = self.get_captcha()
        self.input_text("verifycode", captcha_text)
        self.driver.find_element(By.ID, "submit").click()

    def login(self):
        self.driver.get(url=self.url + 'master/login')
        self.input_text("loginName", self.user)
        self.input_text("password", self.password)

        max_attempts = 10
        for attempt in range(max_attempts):
            self.captcha_login()
            if self.driver.current_url != self.url:
                cookie = self.get_cookie()
                if cookie:
                    return cookie
            if attempt == max_attempts - 1:
                logger.error(f"登录失败, 重试次数超过{max_attempts}次, 请检查账号密码是否正确")
                return None

    def get_cookie(self):
        """
        获取cookie
        """
        try:
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            login_name = cookies.get('loginName')
            password = cookies.get('password')
            jsessionid = cookies.get('JSESSIONID')
            if not login_name or not password or not jsessionid:
                return None
            return f"loginName={cookies.get('loginName')}; password={cookies.get('password')}; JSESSIONID={cookies.get('JSESSIONID')}"
        except Exception:
            return None

    def wait_for_quit(self):
        while self.driver:
            try:
                if self.driver.current_url:
                    time.sleep(1)
            except Exception:
                self.driver.quit()
                logger.info("Driver quit")
                break


@retry()
def update_token(host: str, username: str, password: str) -> str:
    """
    获取token
    :return:
    """
    try:
        cookie_updater = UpdateCookie(host, username, password)
        return cookie_updater.login()
    except Exception as e:
        raise Exception(f"获取token失败: {e}")
