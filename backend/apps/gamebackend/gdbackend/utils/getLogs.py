"""
Creation date: 2024/12/6
Creation Time: 下午5:36
DIR PATH: backend/apps/gamebackend/gdbackend/utils
Project Name: Manager_dvadmin
FILE NAME: getLogs.py
Editor: 30386
"""
import re

from apps.gamebackend.gdbackend.utils.default import GDDefault

TRANSLATIONS = {
    "actid:": "活动编号:",
    "awardid:": "奖励编号:",
    "AwardInfo:": "奖励信息:",
    "buyInfo str:": "购买信息:",
    "count=": "数量=",
    "currtype:": "货币类型:",
    "damage:": "损耗:",
    "daycount:": "日计数:",
    "decrScore:": "扣除积分:",
    "defPlayerId:": "def玩家编号:",
    "exp:": "政绩:",
    "exp=": "政绩=",
    "false": "否:",
    "fame:": "声望:",
    "food:": "粮草:",
    "food=": "粮草=",
    "gold:": "充值货币:",
    "gold=": "充值货币=",
    "guestid:": "门客编号:",
    "guestName:": "门客名字:",
    "iswin:": "赢否:",
    "itemcount:": "项目计数:",
    "itemCount=": "使用数量=",
    "itemid:": "项目编号:",
    "itemNowCount=": "剩余数量=",
    "items:": "项目:",
    "itemSid:": "物品编号:",
    "itemSid=": "物品编号=",
    "mailid:": "邮件编号:",
    "mailinfo:": "邮件信息:",
    "money:": "货币:",
    "money=": "货币=",
    "monthSignCount:": "月卡计数:",
    "monthSignExtraCount:": "月卡额外计数:",
    "nowBossHp:": "当前Boss血量:",
    "nowCount=": "当前剩余=",
    "nowExp:": "当前经验:",
    "nowGuanQiaSid:": "当前关卡编号:",
    "nowlevel:": "新等级:",
    "nowScore:": "当前积分:",
    "oldlevel:": "旧等级:",
    "one_key_buy": "一键购买",
    "oneKeyFight": "一键攻打",
    "playerid:": "玩家编号:",
    "playername:": "玩家名称:",
    "prisonerid:": "囚犯编号:",
    "rankType:": "等级类型:",
    "scroe:": "积分:",
    "sid=": "物品编号=",
    "soldier:": "士兵:",
    "soldier=": "士兵=",
    "state:": "状态:",
    "taskid:": "任务编号:",
    "true": "是:",
    "use itemSid:": "使用物品编号:",
    "vipExp:": "VIP经验:",
    "vipExp=": "VIP经验="
}


class ApiGetLogs(GDDefault):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_return = []

    @staticmethod
    def __washdata(logs: list[dict]):
        translation_pattern = re.compile('|'.join(re.escape(key) for key in TRANSLATIONS.keys()))

        for log in logs:
            tempstr = log.get('des')
            if not tempstr:
                continue
            log['des'] = translation_pattern.sub(
                lambda match: TRANSLATIONS[match.group(0)], tempstr
            ).strip()
        return logs

    def __get_logs(self, log_action: str, log_reason: str, log_server: str,
                   log_pname: str, log_pid: str):
        params = {"key": self.token.get_token(),
                  "cmd": log_action, "type": 1,
                  "serverId": log_server, "page": 0,
                  "puid": log_pid, "logtype": log_reason, "name": log_pname}
        response_json = self.get_action_request(params)
        if "logs" in response_json:
            logs_list = self.__washdata(response_json["logs"])
            return logs_list
        else:
            raise Exception("获取日志失败")

    def __initialize_logs(self, **kwargs):
        if self.token.is_active:
            return self.__get_logs(**kwargs)
        else:
            raise Exception("Token无效")

    def func(self, **kwargs):
        return self.__initialize_logs(**kwargs)
