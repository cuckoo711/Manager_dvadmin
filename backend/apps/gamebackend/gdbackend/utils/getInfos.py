"""
Creation Date: 2024/11/26
Creation Time: 11:43
Dir Path: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
File Name: getInfos.py
Editor: buguniao
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault
from apps.gamebackend.gdbackend.utils.util import change_json, custom_sort_dict


class ApiGDInfos(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = {
            "GameName": self.token.game_server.gamename,
            "WebUrl": self.token.game_server.web_url,
            "Servers": [],
            "ServerTime": {},
            "Actions": [],
            "Reasons": [],
            "CombinedServices": [],
            "Gifts": [],
            "Sids": [],
            "Activetype": [],
            "SidsDict": {
                "menkes": [],
                "props": [],
                "wifes": []
            }
        }

    def __get_sids(self):
        params = {"key": self.token.get_token(), "cmd": 11, "type": 120}
        response_json = self.get_action_request(params)
        temp_dicts = {
            "menkes": change_json(master=response_json, father="menkes", key="name", value="sid", mode="list"),
            "props": change_json(master=response_json, father="props", key="name", value="sid", mode="list"),
            "wifes": change_json(master=response_json, father="wifes", key="name", value="sid", mode="list")
        }
        return_dict = [item for value in temp_dicts.values() for item in value]
        return_dict = list(sorted(return_dict, key=lambda x: custom_sort_dict(x, 'label')))

        if return_dict:
            return [return_dict, temp_dicts]
        else:
            raise Exception("获取sids失败")

    def __get_servers(self):
        params = {"key": self.token.get_token(), "cmd": 200, "type": 0}
        response_json = self.get_action_request(params)
        return_data = change_json(
            master=response_json,
            father="servers",
            key="name",
            value="id",
            mode="list"
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

    def __get_actions(self):
        params = {"key": self.token.get_token(), "action": 7}
        response_json = self.get_login_request(params, rep=True)
        return_data = change_json(
            master=response_json,
            father="funs",
            key="name",
            value="id",
            mode="list",
            sort=True
        )
        if return_data:
            return return_data
        else:
            raise Exception("获取actions失败")

    def __get_reasons(self):
        params = {"key": self.token.get_token(), "cmd": 11, "type": 119}
        response_json = self.get_action_request(params)
        return_data = [{"label": "All全选（所有事件）", "value": "-1"}]
        return_data.extend(change_json(
            master=response_json,
            father="reasontype",
            key="name",
            value="id",
            mode="list",
            sort=True
        ))
        if len(return_data) > 1:
            return return_data
        else:
            raise Exception("获取reasons失败")

    def __get_activetype(self):
        params = {"key": self.token.get_token(), "cmd": 305, "type": 6}
        response_json = self.get_action_request(params)
        return_data = change_json(
            master=response_json,
            father="acts",
            key="name",
            value="id",
            mode="list",
            sort=True
        )
        if len(return_data) > 1:
            return return_data
        else:
            raise Exception("获取activetype失败")

    def __get_combined_services(self):
        params = {"key": self.token.get_token(), "cmd": 200, "type": 1}
        response_json = self.get_action_request(params)
        return_data = change_json(
            master=response_json,
            father="servers",
            key="id",
            value="combinedServices",
            mode="list"
        )
        if return_data:
            return return_data
        else:
            raise Exception("获取combined_services失败")

    def __get_gifts(self):
        params = {"key": self.token.get_token(), "cmd": 307, "type": 2}
        response_json = self.get_action_request(params)
        return_data = change_json(
            master=response_json,
            father="gifts",
            key="giftName",
            value="giftId",
            mode="list",
            sort=True
        )
        if return_data:
            return return_data
        else:
            raise Exception("获取gifts失败")

    def __initialize_info_dict(self):
        if self.token.is_active:
            sids_temp = self.__get_sids()
            return {
                "GameName": self.token.game_server.gamename,
                "WebUrl": self.token.game_server.web_url,
                "Servers": self.__get_servers(),
                "ServerTime": self.__get_servers_open(),
                "Actions": self.__get_actions(),
                "Reasons": self.__get_reasons(),
                "Activetype": self.__get_activetype(),
                "CombinedServices": self.__get_combined_services(),
                "Gifts": self.__get_gifts(),
                "Sids": sids_temp[0],
                "SidsDict": sids_temp[1]
            }
        else:
            raise Exception("Token无效")

    def func(self):
        return self.__initialize_info_dict()
