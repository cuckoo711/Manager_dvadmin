"""
Creation Date: 2024/11/30
Creation Time: 10:10
Dir Path: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
File Name: getGiftslogs.py
Editor: buguniao
"""
import concurrent.futures
from datetime import datetime

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import custom_sort_dict
from dvadmin.utils.backends import logger


class ApiGetGiftsLogs(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = {}

    def __get_gifts_logs(self, topage: int):
        params = {"key": self.token.get_token(), "cmd": 307, "serverSid": '', "topage": topage, "type": 3,
                  "username": '', "startTime": '', "stopTime": '', "prop": ''}
        return self.get_action_request(params)

    @staticmethod
    def __log_matches_conditions(log, conditions):
        """
        检查日志是否满足所有过滤条件。
        :param log: 单个日志字典
        :param conditions: 包含过滤条件的字典
        :return: 是否满足过滤条件
        """
        log_time = datetime.strptime(log.get('time', ''), '%Y-%m-%d %H:%M:%S.0') if log.get('time') else None
        # 检查时间范围
        if conditions['start_time'] and log_time and log_time < conditions['start_time']:
            return False
        if conditions['stop_time'] and log_time and log_time > conditions['stop_time']:
            return False
        # 检查服务器名称
        if conditions['server_name'] and conditions['server_name'].split(')')[-1] not in log.get('serverId', ''):
            return False
        # 检查玩家名称
        if conditions['player_name'] and log.get('playerNames', '') not in conditions['player_name']:
            return False
        # 检查道具
        if conditions['prop'] and conditions['prop'] not in log.get('gift', ''):
            return False
        return True

    def __filter_logs(self, logs, start_time, stop_time, server_name, player_name, prop):
        """
        过滤日志，根据提供的条件筛选符合的日志。
        :param logs: 日志列表
        :param start_time: 开始时间 (datetime对象)
        :param stop_time: 结束时间 (datetime对象)
        :param server_name: 服务器名称 (字符串)
        :param player_name: 玩家名称 (字符串或列表)
        :param prop: 道具名称 (字符串)
        :return: 符合条件的日志列表
        """
        conditions = {
            'start_time': start_time,
            'stop_time': stop_time,
            'server_name': server_name,
            'player_name': player_name,
            'prop': prop
        }

        result = [log for log in logs if self.__log_matches_conditions(log, conditions)]
        result_washed = self.__wash_logs(result)
        return result_washed

    @staticmethod
    def __wash_logs(logs):
        for log in logs:
            if not log.get('playerNames'):
                log['playerNames'] = '**全服邮件**'
            log['serverId'] = log.get('serverId').strip(':')
        return logs

    @staticmethod
    def __sort_logs(logs):
        return list(sorted(logs, key=lambda x: custom_sort_dict(x, 'id'), reverse=True))

    def __get_all_gifts_logs(self, start_time=None, stop_time=None, server_name=None, player_name=None, prop=None):
        first_data = self.__get_gifts_logs(1)
        page_size = int(first_data.get('pageSize', 10))
        total_count = int(first_data.get('totalCount', 0))
        first_logs = self.__filter_logs(
            first_data.get('logs', []),
            start_time, stop_time, server_name, player_name, prop
        )
        total_page = total_count // page_size + 1 if total_count % page_size else total_count // page_size
        result = {
            'logs': first_logs,
            'totalCount': 0,
            'pageSize': page_size
        }
        if total_count <= page_size:
            result['totalCount'] = len(result['logs'])
            result['logs'] = list(sorted(result['logs'], key=lambda x: custom_sort_dict(x, 'id')))
            return result
        with (concurrent.futures.ThreadPoolExecutor() as executor):
            future_to_page = {executor.submit(self.__get_gifts_logs, i): i for i in
                              range(2, total_page + 1)}
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    data = future.result()
                    filtered_logs = self.__filter_logs(
                        data.get('logs', []),
                        start_time, stop_time, server_name, player_name, prop
                    )
                    result['logs'].extend(filtered_logs)
                except Exception as exc:
                    logger.error(f'页面 {future_to_page[future]} 生成时出现异常: {exc}')
        result['totalCount'] = len(result['logs'])
        result['logs'] = self.__sort_logs(result['logs'])
        return result

    def __initialize_gifts_logs(self, **kwargs):
        if self.token.is_active:
            return self.__get_all_gifts_logs(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_gifts_logs(**kwargs)
