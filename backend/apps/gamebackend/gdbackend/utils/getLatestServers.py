"""
Creation date: 2024/12/13
Creation Time: 下午3:32
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: getLatestServers.py
Editor: 30386
"""
from datetime import datetime, timedelta

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import change_json


class ApiGetLatestServers(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = ("", [], 0)
        self.__servers_len = 0

    def __get_contest(self, topage: int, serverid: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 305,
            "serverid": serverid,
            "topage": topage,
            "type": 3,
            "qstime": '1990-01-01 00:00:00',
            "qetime": '2030-12-31 23:59:59'
        }
        if self.__servers_len > 1:
            params['actid'] = '1301'
        else:
            params['actid'] = '-1'
        return self.get_action_request(params)

    def __get_all_contest(self, serverid: str):
        first_data = self.__get_contest(1, serverid)
        page_size = int(first_data.get('pageSize', 10))
        total_count = int(first_data.get('totalCount', 0))
        total_page = (total_count + page_size - 1) // page_size
        first_logs = first_data.get('logs', [])
        result = {
            "logs": first_logs,
            'totalCount': 0,
            'pageSize': page_size
        }
        if total_count <= page_size:
            result['totalCount'] = len(result['logs'])
            return result
        for i in range(2, total_page + 1):
            data = self.__get_contest(i, serverid)
            result['logs'].extend(data.get('logs', []))
        result['totalCount'] = len(result['logs'])
        return result

    def __get_servers(self):
        params = {"key": self.token.get_token(), "cmd": 200, "type": 0}
        response_json = self.get_action_request(params)
        return_data = change_json(
            master=response_json,
            father="servers",
            key="name",
            value="id",
        )
        if return_data:
            return return_data
        else:
            raise Exception("获取servers失败")

    def __get_servers_open(self):
        params = {"key": self.token.get_token(), "cmd": 211, "type": 1}
        response_json = self.get_action_request(params)
        return_data = change_json(
            master=response_json,
            father="servers",
            key="id",
            value="opentime"
        )
        if return_data:
            return return_data
        else:
            raise Exception("获取servers_open失败")

    def __find_latest_activity_time(self, serverid: str, server_time_dict: dict):
        logs = self.__get_all_contest(serverid).get('logs', [])
        server_time = server_time_dict.get(serverid, "2030-01-01 00:00:00")

        def find_latest(data_list):
            if not data_list:
                if server_time:
                    opentime = datetime.strptime(server_time, '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
                    return {'endTime': opentime.strftime('%Y-%m-%d 00:00:00'),
                            'serverid': '', 'len': 0}
                return {'endTime': datetime.now().strftime('%Y-%m-%d 00:00:00'),
                        'serverid': '', 'len': 0}

            latest_time = None
            _latest_item = None

            for item in data_list:
                current_time = datetime.strptime(item['endTime'], '%Y-%m-%d %H:%M:%S')
                if latest_time is None or current_time > latest_time:
                    latest_time = current_time
                    _latest_item = item

            return _latest_item

        latest_item = find_latest(logs)

        return {
            "endTime": latest_item['endTime'],
            "nextTime": (datetime.strptime(latest_item['endTime'], '%Y-%m-%d %H:%M:%S') +
                         timedelta(days=1)).strftime('%Y-%m-%d 00:00:00'),
            "serverid": latest_item['serverid'].split(':') if latest_item['serverid'] else [],
            "len": len(latest_item['serverid'].split(':')) if latest_item['serverid'] else 0,
            "is_valid": (datetime.strptime(latest_item['endTime'], '%Y-%m-%d %H:%M:%S')
                         < datetime.now() + timedelta(days=1))
        }

    def __find_all_latest(self):
        results = ["", [], 0]
        latest_time = None
        temp_len = 0
        server_time = self.__get_servers_open()
        servers = self.__get_servers()
        self.__servers_len = len(servers)
        for server, serverid in servers.items():
            item = self.__find_latest_activity_time(serverid, server_time)
            if item.get('is_valid'):
                current_time = datetime.strptime(item['nextTime'], '%Y-%m-%d %H:%M:%S')
                if latest_time is None or current_time > latest_time:
                    latest_time = current_time
                    results[0] = item['nextTime'][0:10]
                if temp_len < item['len']:
                    temp_len = item['len']
                    results[2] = temp_len
                results[1].append(serverid)

        return tuple(results)

    def __initialize_latest_activity(self):
        if self.token.is_active:
            return self.__find_all_latest()
        else:
            raise Exception("Token无效")

    def func(self):
        return self.__initialize_latest_activity()
