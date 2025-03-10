"""
Creation date: 2024/12/3
Creation Time: 下午3:44
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: EditServerName.py
Editor: 30386
"""

from apps.gamebackend.gdbackend.utils.default import GDDefault


class ApiEditServerName(GDDefault):
    def __init__(self, token_id):
        super().__init__(token_id)
        self.default_return = False

    @staticmethod
    def _change_name(oldinfo: dict, newname: str, combinedServices: str) -> dict:
        updated_info = {
            'id': oldinfo['id'],
            'name': newname,
            'areaID': oldinfo['areaID'],
            'address': oldinfo['address'],
            'httpPort': oldinfo['serverHttpPort'],
            'dbname': oldinfo['dbName'],
            'dbuser': oldinfo['dbuser'],
            'dbpwd': oldinfo['dbpwd'],
            'dbip': oldinfo['dbip'],
            'max': oldinfo['max'],
            'dbECD': oldinfo['dbECD'],
            'logAddress': oldinfo['logAddress'],
            'logHttpAddress': oldinfo['logHttpAddress'],
            'allowPackageVersion': oldinfo['allowPackageVersion'],
            'allowLookIP': oldinfo['allowLookIP'],
            'combinedServices': combinedServices,
        }
        return updated_info

    def __get_server_info(self, serverid: str):
        params = {
            "key": self.token.get_token(),
            "cmd": 203,
            "id": serverid
        }
        response_json = self.get_action_request(params)
        if response_json.get("msg") == "0" and "servers" in response_json:
            return response_json["servers"][0]
        raise Exception("获取服务器信息失败")

    def __edit_server_name(self, serverid: str, newname: str, combinedServices: str) -> bool:
        info = self.__get_server_info(serverid)
        new_info = self._change_name(info, newname, combinedServices)
        params = {
            "key": self.token.get_token(),
            "cmd": 204,
            **new_info
        }
        response_json = self.get_action_request(params)
        return response_json.get("msg") == "0"

    def __initialize_edit_server_name(self, serverid: str, newname: str, combinedServices: str):
        if self.token.is_active:
            return self.__edit_server_name(serverid, newname, combinedServices)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_edit_server_name(**kwargs)
