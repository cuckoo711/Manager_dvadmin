"""
Creation date: 2024/12/13
Creation Time: 上午10:16
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: getActivity.py
Editor: 30386
"""
import concurrent.futures

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import custom_sort_dict
from dvadmin.utils.backends import logger


class ApiGetActivity(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    def __get_actcheck(self, serverid: str, topage: int, actid: str, qstime: str, qetime: str):
        params = {"key": self.token.get_token(), "cmd": 305, "serverid": serverid, "topage": topage,
                  "type": 3, "actid": actid, "qstime": qstime,
                  "qetime": qetime}
        return self.get_action_request(params)

    @staticmethod
    def __sort_logs(logs):
        return list(sorted(logs, key=lambda x: custom_sort_dict(x, 'id'), reverse=True))

    def __get_all_gifts_logs(self, serverid: str, actid: str, qstime: str, qetime: str):
        first_data = self.__get_actcheck(serverid, 1, actid, qstime, qetime)
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
            result['logs'] = list(sorted(result['logs'], key=lambda x: custom_sort_dict(x, 'id')))
            return result
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_page = {executor.submit(self.__get_actcheck, serverid, i, actid, qstime, qetime): i for i in
                              range(2, total_page + 1)}
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    data = future.result()
                    result['logs'].extend(data.get('logs', []))
                except Exception as exc:
                    logger.error(f'页面 {future_to_page[future]} 生成时出现异常: {exc}')
        result['totalCount'] = len(result['logs'])
        result['logs'] = self.__sort_logs(result['logs'])
        return result

    def __initialize_activity_logs(self, **kwargs):
        if self.token.is_active:
            return self.__get_all_gifts_logs(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_activity_logs(**kwargs)
