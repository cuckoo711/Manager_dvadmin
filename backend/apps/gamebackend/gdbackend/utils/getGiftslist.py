"""
Creation date: 2024/12/2
Creation Time: 下午2:54
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: getGiftslist.py
Editor: 30386
"""
import concurrent.futures

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import custom_sort_dict
from dvadmin.utils.backends import logger


class ApiGetGiftsList(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = []

    @staticmethod
    def __log_matches_conditions(log, conditions):
        """
        检查日志是否满足所有过滤条件。
        :param log: 单个日志字典
        :param conditions: 包含过滤条件的字典
        :return: 是否满足过滤条件
        """
        # 检查礼包名称
        if conditions['name'] and conditions['name'] not in log.get('name', ''):
            return False
        # 检查礼包描述
        if conditions['giftDes'] and log.get('giftDes', '') not in conditions['giftDes']:
            return False
        # 检查礼包内容
        if conditions['gift'] and conditions['gift'] not in log.get('gift', ''):
            return False
        return True

    def __filter_logs(self, logs, name, giftDes, gift):
        """
        过滤日志，根据提供的条件筛选符合的日志。
        :param logs: 日志列表
        :param name: 礼包名称
        :param giftDes: 礼包描述
        :param gift: 礼包内容
        :return: 符合条件的日志列表
        """
        conditions = {
            'name': name,
            'giftDes': giftDes,
            'gift': gift
        }
        return [log for log in logs if self.__log_matches_conditions(log, conditions)]

    def __get_gifts(self, page: int):
        params = {"key": self.token.get_token(), "cmd": 303, "type": 2,
                  "username": self.token.user.username, "topage": page}

        return self.get_action_request(params)

    def __get_all_gifts(self, name=None, giftDes=None, gift=None):
        first_data = self.__get_gifts(1)
        page_size = len(first_data)
        total_count = int(first_data.get('totalCount', 0))
        first_logs = self.__filter_logs(
            first_data.get('logs', []), name, giftDes, gift
        )
        total_page = total_count // page_size + 1 if total_count % page_size else total_count // page_size
        result = {
            "logs": first_logs,
            "totalCount": 0,
            "pageSize": page_size
        }
        result['logs']: list
        if total_count <= page_size:
            result['totalCount'] = len(result['logs'])
            result['logs'] = list(sorted(result['logs'], key=lambda x: custom_sort_dict(x, 'name')))
            return result
        with (concurrent.futures.ThreadPoolExecutor() as executor):
            future_to_page = {executor.submit(self.__get_gifts, page): page for page in
                              range(2, total_page + 1)}
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    data = future.result()
                    filtered_logs = self.__filter_logs(
                        data.get('logs', []), name, giftDes, gift
                    )
                    result['logs'].extend(filtered_logs)
                except Exception as exc:
                    logger.error(f'页面 {future_to_page[future]} 生成时出现异常: {exc}')
        result['totalCount'] = len(result['logs'])
        result['logs'] = list(sorted(result['logs'], key=lambda x: custom_sort_dict(x, 'name')))
        return result

    def __initialize_gifts_logs(self, **kwargs):
        if self.token.is_active:
            return self.__get_all_gifts(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_gifts_logs(**kwargs)
