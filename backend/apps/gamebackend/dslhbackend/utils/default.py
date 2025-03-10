"""
Creation date: 2024/12/26
Creation Time: 下午2:51
DIR PATH: backend/apps/gamebackend/dslhbackend/utils
Project Name: Manager_dvadmin
FILE NAME: default.py
Editor: 30386
"""
import requests
from bs4 import BeautifulSoup

from dvadmin.utils.backends import logger


class DSLHDefault:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.strip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()

        self.servers = []
        self.has_recharges = []
        self.no_recharges = []
        self.server_config = {}

        self.login()
        self.get_servers()
        self.get_all_recharge()
        self.get_servers_config()

    def login(self):
        login_url = f"{self.base_url}/login.php"
        payload = {
            "gmname": self.username,
            "gmpswd": self.password
        }
        response = self.session.post(login_url, data=payload)
        if response.history and response.history[0].status_code == 302:
            logger.info("登录成功")
        else:
            raise ValueError("登录失败")

    def get_servers(self):
        self.servers = []
        server_url = f"{self.base_url}/main.php"
        response = self.session.get(server_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            servers = soup.find_all("option")
            for server in servers:
                self.servers.append(server.text)
            logger.info(f"获取服务器列表成功, 共{len(self.servers)}个")
        else:
            raise ValueError("获取服务器列表失败")

    def switch_server(self, server_index: int = None, server_name: str = None):
        if server_index is None and not server_name:
            raise ValueError("服务器名称或索引必须指定一个")
        if server_name and server_name not in self.servers:
            raise ValueError("服务器名称错误")
        if server_index and server_index >= len(self.servers):
            raise ValueError("服务器索引错误")

        switch_server_name = (
            server_name if server_name else (
                self.servers[server_index] if server_index < len(self.servers) else
                self.servers[0])
        )
        switch_url = f"{self.base_url}/main.php?svr={switch_server_name}"
        response = self.session.post(switch_url)
        if response.status_code == 200:
            logger.info(f"切换服务器到 {switch_server_name}")
        else:
            raise ValueError("切换服务器失败")

    def get_recharge(self):
        recharge_url = f"{self.base_url}/manager/page_list.php?temp=recharge.xml&title=充值账单&dbr=game"
        response = self.session.get(recharge_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find(name="table", attrs={"class": "common"})
            trs = table.find_all("tr", class_=lambda x: x != "header")
            rows = []
            for tr in trs:
                tds = tr.find_all("td", class_=lambda x: x != "page")
                rows.append([td.text.strip() for td in tds])
            rows = [_ for _ in rows if _]
            return rows
        else:
            raise ValueError("获取充值信息失败")

    def get_all_recharge(self):
        self.has_recharges = []
        self.no_recharges = []
        for index, server in enumerate(self.servers):
            self.switch_server(index)
            try:
                recharge = self.get_recharge()
                if recharge:
                    self.has_recharges.append(server)
                else:
                    self.no_recharges.append(server)
            except Exception as e:
                logger.info(f"获取服务器{server}充值信息失败: {e}")

    def get_servers_config(self):
        server_config_url = f"{self.base_url}/manager/page_list.php?temp=game_config.xml&title=游戏配置&dbr=game_op"
        response = self.session.get(server_config_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find(name="table", attrs={"class": "common"})
            trs = table.find_all("tr", class_=lambda x: x != "header")
            rows = []
            for tr in trs:
                tds = tr.find_all("td", class_=lambda x: x != "page")
                rows.append([td.text.strip() for td in tds])
            self.server_config = {
                _[1]: {
                    "server_name": _[1],
                    "server_id": _[2],
                    "server_ip": _[3],
                    "open_time": _[4],
                    "database_user": _[5],
                    "database_name": _[6],
                    "database_port": _[7],
                    "server_is_open": _[8],
                    "server_url": _[9],
                    "server_port": _[10],
                    "is_merged": _[11],
                    "server_type": _[12],
                }
                for _ in rows if _
            }
            logger.info(f"获取服务器配置信息成功, 共{len(self.server_config)}个")
        else:
            raise ValueError("获取服务器配置信息失败")

    def megeropt(self, startserverid, endserverid, sqlip, isshow, gameip, gameport, ismerge, state):
        megeropt_url = f"{self.base_url}/manager/megeropt.php"
        payload = {
            "startserverid": startserverid,
            "endserverid": endserverid,
            "sqlip": sqlip,
            "isshow": isshow,
            "gameip": gameip,
            "gameport": gameport,
            "ismerge": ismerge,
            "state": state,
            "submit": "更新"
        }
        response = self.session.post(megeropt_url, data=payload)
        if response.status_code == 200:
            logger.info("合服操作成功")
        else:
            raise ValueError("合服操作失败")


if __name__ == '__main__':
    dslh = DSLHDefault("https://ycnrg05sjby.jingtanggame.com/gmop/", "crcadmin", "cCxy*jw1{sPsscaonima")
    dslh.megeropt(
        "101",
        "101",
        "180.184.161.140",
        "1",
        "ycnrg05sjby.jingtanggame.com",
        "20001",
        "1",
        "2"
    )
