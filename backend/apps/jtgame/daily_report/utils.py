"""
Creation date: 2024/7/10
Creation Time: 下午5:04
DIR PATH: backend/jtgame/daily_report
Project Name: Manager_dvadmin
FILE NAME: untils.py
Editor: 30386
"""
import datetime
import json
import re
import traceback
from collections import defaultdict
from copy import deepcopy
from time import sleep

import requests
from django.core.mail import send_mail
from django.db import connection
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.dnspod.v20210323 import dnspod_client, models
from volcenginesdkcore import Configuration
from volcenginesdkcore.rest import ApiException
from volcenginesdkecs import DescribeImagesRequest, DescribeInstancesRequest, ECSApi, EipAddressForRunInstancesInput, \
    ModifyInstanceSpecRequest, NetworkInterfaceForRunInstancesInput, RenewInstanceRequest, RunInstancesRequest, \
    StopInstanceRequest, VolumeForRunInstancesInput

from application import settings
from apps.jtgame.daily_report.models import ConsoleAccount, Consoles, QuickAccount
from apps.jtgame.game_manage.models import Games
from conf.env import SECRET_ID, SECRET_KEY
from dvadmin.utils.backends import logger


class WeChatBot:
    def __init__(self, webhook_key):
        self.webhook_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}'

    def send_text(self, content, mentioned_list=None, mentioned_mobile_list=None):
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
            }
        }
        if mentioned_list:
            data['text']['mentioned_list'] = mentioned_list
        if mentioned_mobile_list:
            data['text']['mentioned_mobile_list'] = mentioned_mobile_list
        return self._post_request(data)

    def _post_request(self, data):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.webhook_url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise ValueError(f'Failed to send message: {response.text}')
        return response.json()


class ConsoleData:
    instances = []

    def make_daily_report(self, update=False):
        self.instances = []
        logs = []
        console_list = self.get_console_accounts()
        for console in console_list:
            self.set_configuration(console)
            ecs = self.get_ecs(console.account)
            self.instances.extend(ecs)
        if update:
            logs = self.update_to_models()
        return {'instances': len(self.instances), 'update': update, 'logs': logs}

    def update_to_models(self):
        logs = []
        try:
            logs.append(f"获取实例信息: {len(self.instances)} 条")
            logs.append(f"原有实例信息: {Consoles.objects.count()} 条")
            Consoles.objects.all().delete()
            with connection.cursor() as cursor:
                cursor.execute('ALTER TABLE jtadmin_daily_report_consoles AUTO_INCREMENT = 1')
            for instance in self.instances:
                Consoles.objects.create(
                    account=instance['所属账号'],
                    instance_id=instance['实例ID'],
                    instance_name=instance['实例名称'],
                    status=instance['状态'],
                    instance_type_id=instance['规格'],
                    cpus=instance['CPU'],
                    memory_size=instance['内存'],
                    eip_address=instance['主IPv4地址'],
                    primary_ip_address=instance['次IPv4地址'],
                    instance_charge_type=instance['实例计费类型'],
                    expired_at=instance['到期时间'],
                    created_at=instance['创建时间'],
                    updated_at=instance['更新时间'],
                )
                # logs.append(f"创建实例: {instance['实例名称']}")
            logs.append(f"更新实例信息: {Consoles.objects.count()} 条")
        except Exception as e:
            logs.append(f"更新实例信息失败: {str(e)}")
            logger.error("Detailed traceback: %s", traceback.format_exc())
        return logs

    @staticmethod
    def get_console_accounts():
        return ConsoleAccount.objects.all()

    @staticmethod
    def set_configuration(console):
        configuration = Configuration()
        configuration.ak = console.access_key
        configuration.sk = console.secret_key
        configuration.region = "cn-shanghai"
        Configuration.set_default(configuration)

    def get_ecs(self, account, next_token=''):
        api_instance = ECSApi()
        describe_instances_request = DescribeInstancesRequest(max_results=100, next_token=next_token)
        try:
            api_result = api_instance.describe_instances(describe_instances_request)
            ecs_info = self.analysis_ecs(api_result.instances, account)
            next_token = api_result.next_token
            if next_token:
                ecs_info += self.get_ecs(account, next_token)
            return ecs_info
        except ApiException as e:
            logger.error(f"Exception when calling ECSApi: {e}")
            return []

    @staticmethod
    def analysis_ecs(instances, account):
        instance_infos = []
        for instance in instances:
            instance_dict = instance.to_dict()
            instance_infos.append({
                '实例ID': instance_dict['instance_id'],
                '实例名称': instance_dict['instance_name'],
                '状态': instance_dict['status'],
                '规格': instance_dict['instance_type_id'],
                'CPU': str(instance_dict['cpus']) + '核',
                '内存': str(int(instance_dict['memory_size']) / 1024) + 'GB',
                '主IPv4地址': instance_dict['eip_address']['ip_address'] if instance_dict.get('eip_address') else '/',
                '次IPv4地址': instance_dict['network_interfaces'][0]['primary_ip_address'] if instance_dict.get(
                    'network_interfaces') else '/',
                '实例计费类型': {'PostPaid': '按量计费', 'PrePaid': '包年包月'}.get(
                    instance_dict['instance_charge_type']
                ),
                '到期时间': datetime.datetime.strptime(
                    instance_dict['expired_at'], "%Y-%m-%dT%H:%M:%S+08:00"
                ).strftime("%Y-%m-%d %H:%M:%S") if instance_dict.get('expired_at') else '/',
                '创建时间': datetime.datetime.strptime(
                    instance_dict['created_at'], "%Y-%m-%dT%H:%M:%S+08:00"
                ).strftime("%Y-%m-%d %H:%M:%S") if instance_dict.get('created_at') else '/',
                '更新时间': datetime.datetime.strptime(
                    instance_dict['updated_at'], "%Y-%m-%dT%H:%M:%S+08:00"
                ).strftime("%Y-%m-%d %H:%M:%S") if instance_dict.get('updated_at') else '/',
                '所属账号': account
            })
        return instance_infos


class ModifyInstanceSpec:
    def __init__(self, account: str):
        self.account = account
        self.console = ConsoleAccount.objects.get(account=account)

    def set_configuration(self):
        configuration = Configuration()
        configuration.ak = self.console.access_key
        configuration.sk = self.console.secret_key
        configuration.region = "cn-shanghai"
        Configuration.set_default(configuration)

    def check_instance_status(self, instance_id: str):
        self.set_configuration()
        api_instance = ECSApi()
        describe_instances_request = DescribeInstancesRequest(
            instance_ids=[instance_id],
        )
        try:
            result = api_instance.describe_instances(describe_instances_request)
            instanceids = result.instances
            if not instanceids:
                logger.error(f"获取实例信息失败: {result}")
                return {'status': None, 'result': result}
            instance = instanceids[0].to_dict()
            if instance.get('status', '').lower() != 'running':
                logger.error(f"实例未运行: {instance}")
                return {'status': False, 'result': '实例未运行'}
            return {'status': True, 'result': instance}
        except ApiException as e:
            logger.error(f"Exception when calling ECSApi: {e}")
            return {'status': None, 'result': e}

    def modify_instance_spec(self, instance_id: str, server_spec: str):
        self.set_configuration()
        api_instance = ECSApi()

        check_result = self.check_instance_status(instance_id)
        if check_result['status'] is None:
            return {'status': False, 'result': check_result['result']}
        elif not check_result['status']:
            logger.info(f"实例未运行: {check_result['result']}, 无需关机")
        else:
            logger.info(f"实例运行中: {check_result['result']}")
            stop_instance_request = StopInstanceRequest(
                force_stop=True,
                instance_id=instance_id,
            )
            try:
                api_instance.stop_instance(stop_instance_request)
            except ApiException as e:
                logger.error(f"Exception when calling ECSApi: {e}")
                return {'status': False, 'result': e}

            for i in range(10):
                describe_instances_request = DescribeInstancesRequest(
                    instance_ids=[instance_id],
                )
                try:
                    result = api_instance.describe_instances(describe_instances_request)
                    instanceids = result.instances
                    if not instanceids:
                        logger.error(f"获取实例信息失败: {result}")
                        sleep(1)
                        continue
                    instance = instanceids[0].to_dict()
                    if instance.get('status', '').lower() != 'stopped':
                        logger.error(f"实例未停止: {instance}")
                        sleep(1)
                    break
                except ApiException as e:
                    logger.error(f"Exception when calling ECSApi: {e}")
                    return {'status': False, 'result': e}
            else:
                logger.error(f"实例未停止: {instance_id}")
                return {'status': False, 'result': '实例未停止'}

        modify_instance_spec_request = ModifyInstanceSpecRequest(
            instance_id=instance_id,
            instance_type_id=server_spec,
        )
        try:
            result = api_instance.modify_instance_spec(modify_instance_spec_request)
            return {'status': True, 'result': result}
        except ApiException as e:
            logger.error(f"Exception when calling ECSApi: {e}")
            return {'status': False, 'result': e}


class ConsoleRun:
    def __init__(self):
        self.console = ConsoleAccount.objects.get(account="jtconsole")

    def set_configuration(self):
        configuration = Configuration()
        configuration.ak = self.console.access_key
        configuration.sk = self.console.secret_key
        configuration.region = "cn-shanghai"
        Configuration.set_default(configuration)

    def get_image_list(self):
        self.set_configuration()
        api_instance = ECSApi()
        describe_images_request = DescribeImagesRequest(
            max_results=20,
            visibility="private",
        )
        try:
            result = api_instance.describe_images(describe_images_request)
            return {'status': True, 'result': result}
        except ApiException as e:
            logger.error(f"Exception when calling ECSApi: {e}")
            return {'status': False, 'result': e}

    def run_instances(self, name: str, new_name: str, image_id: str, server_spec: str, dry_run: bool = True):
        self.set_configuration()
        api_instance = ECSApi()
        req_eip_address = EipAddressForRunInstancesInput(
            bandwidth_package_id="bwp-3qdfvmfgr914w7prml10y70k6",
            charge_type="PayByTraffic",
            release_with_instance=True,
        )
        req_network_interfaces = NetworkInterfaceForRunInstancesInput(
            security_group_ids=["sg-5ggjh8d729s073inql0d64yc"],
            subnet_id="subnet-5ggjhs3i6tj473inql4dnuw0",
        )
        req_volumes = VolumeForRunInstancesInput(
            delete_with_instance="true",
            size=300,
        )
        run_instances_request = RunInstancesRequest(
            description=name,
            dry_run=dry_run,
            eip_address=req_eip_address,
            hostname=new_name,
            image_id=image_id,
            instance_charge_type="PrePaid",
            instance_name=name,
            instance_type_id=server_spec,
            keep_image_credential=True,
            network_interfaces=[req_network_interfaces],
            period=1,
            period_unit="Month",
            volumes=[req_volumes],
            zone_id="cn-shanghai-a",
        )

        try:
            result = api_instance.run_instances(run_instances_request)
            return result
        except Exception as e:
            logger.error(f"Exception when calling ECSApi: {e}")
            return None

    def describe_instances(self, instance_id: str):
        self.set_configuration()
        api_instance = ECSApi()
        describe_instances_request = DescribeInstancesRequest(
            instance_ids=[instance_id],
        )
        try:
            result = api_instance.describe_instances(describe_instances_request)
            return result
        except ApiException as e:
            logger.error(f"Exception when calling ECSApi: {e}")
            return None

    def get_ipv4_from_instance(self, instance_id: str, retry: int = 60, stime: int = 1):
        for i in range(retry):
            instances = self.describe_instances(instance_id)
            if not instances:
                logger.error(f"获取实例信息失败: {instances}")
                sleep(stime)
                continue
            instanceids = instances.instances
            if not instanceids:
                logger.error(f"获取实例信息失败: {instances}")
                sleep(stime)
                continue
            instance = instanceids[0].to_dict()
            if not instance.get('eip_address'):
                logger.error(f"获取实例信息失败: {instance}")
                sleep(stime)
                continue
            eip_address = instance.get('eip_address').get('ip_address')
            if not eip_address:
                logger.error(f"获取实例IP信息失败: {instance}")
                sleep(stime)
                continue
            return {'status': True, 'result': eip_address}
        return {'status': False, 'result': '获取实例信息失败'}


def create_record(value: str, sub_domain: str):
    try:
        cred = credential.Credential(
            secret_id=SECRET_ID,
            secret_key=SECRET_KEY
        )
        http_profile = HttpProfile()
        http_profile.endpoint = "dnspod.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = dnspod_client.DnspodClient(cred, "", client_profile)

        req = models.CreateRecordRequest()
        params = {
            "Domain": "jingtanggame.com",
            "RecordType": "A",
            "RecordLine": "默认",
            "Value": value,
            "SubDomain": sub_domain
        }
        req.from_json_string(json.dumps(params))

        resp = client.CreateRecord(req)
        return {"status": True, "result": resp.to_json_string()}
    except TencentCloudSDKException as err:
        return {"status": False, "result": err}


def get_record_list():
    try:
        cred = credential.Credential(
            secret_id=SECRET_ID,
            secret_key=SECRET_KEY
        )
        http_profile = HttpProfile()
        http_profile.endpoint = "dnspod.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = dnspod_client.DnspodClient(cred, "", client_profile)

        req = models.DescribeRecordListRequest()
        params = {
            "Domain": "jingtanggame.com",
            "Limit": 3000
        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeRecordList(req)
        return {"status": True, "result": resp.to_json_string()}
    except TencentCloudSDKException as err:
        return {"status": False, "result": err}


class QuickData:
    def __init__(self, shifting_days=0):
        self.host_url = 'http://127.0.0.1:5010'
        self.shifting_days = shifting_days

        self.game_name_temp = {}

    def make_daily_data(self):
        # 使用字典进行中间聚合，结构为 { type_id: { game_name: data_dict } }
        aggregated_result = {
            0: {},
            1: {},
            2: {},
            3: {},
            4: []  # 修正：初始化时不应该直接定义为列表，这里应该是字典，后面统一转
        }
        # 重新初始化为字典
        aggregated_result = {k: {} for k in range(5)}

        type_dict = {
            'yesterday_income': 0,
            'last_week_income': 1,
            'last_month_income': 2,
            'current_month_income': 3,
            'this_month_income': 4
        }
        quick_accounts = QuickAccount.objects.all()
        for account in quick_accounts:
            try:
                quick_datas_temp = self.get_income_details(account)
                for key in ['yesterday_income', 'last_week_income', 'last_month_income', 'current_month_income',
                            'this_month_income']:
                    type_id = type_dict[key]
                    cleaned_datas = self.wash_data(quick_datas_temp.get(key, []))
                    
                    for data in cleaned_datas:
                        game_name = data['game_name']
                        if game_name in aggregated_result[type_id]:
                            # 如果游戏已存在，进行数据累加
                            existing_data = aggregated_result[type_id][game_name]
                            existing_data['recharge'] = round(existing_data['recharge'] + data['recharge'], 2)
                            existing_data['yesterday_actives'] += data['yesterday_actives']
                            existing_data['channels'] += data['channels']
                            existing_data['subscribers'] += data['subscribers']
                            existing_data['devices'] += data['devices']
                            existing_data['payments'] += data['payments']
                        else:
                            # 如果游戏不存在，直接赋值
                            aggregated_result[type_id][game_name] = data

            except Exception as e:
                logger.error(f"Error processing account {account}: {e}")
                logger.error("Detailed traceback: %s", traceback.format_exc())
        
        # 将聚合后的字典转换为列表返回
        result = {k: list(v.values()) for k, v in aggregated_result.items()}
        return result

    def get_income_details(self, account) -> dict:
        try:
            result = requests.post(
                f'{self.host_url}/total',
                json={'account': account.account, 'password': account.password, 'shifting_days': self.shifting_days},
                timeout=6000
            )
            if result.status_code == 200:
                return result.json()
            else:
                logger.error(f"Error getting income details: {result.text}")
                return {}
        except Exception as e:
            logger.error(f"Error getting income details: {e}")
            logger.error("Detailed traceback: %s", traceback.format_exc())
            return {}

    def wash_data(self, quick_datas_temp):
        result = []
        for data in quick_datas_temp:
            data_temp = {}
            game_name = data.get('游戏名称', '')
            if not game_name:
                continue

            if game_name in self.game_name_temp:
                data_temp['game_name'] = self.game_name_temp[game_name]['game_name']
                data_temp['online_days'] = self.game_name_temp[game_name]['online_days']
                data_temp['banhao'] = self.game_name_temp[game_name]['banhao']
                reconciliation_ratio = self.game_name_temp[game_name]['reconciliation_ratio']
            else:
                game: Games = Games.objects.filter(quick_name=game_name).first()
                if game:
                    data_temp['game_name'] = game.name
                    data_temp['online_days'] = str((datetime.date.today() - game.release_date).days)
                    reconciliation_ratio = float(game.reconciliation_ratio)
                else:
                    data_temp['game_name'] = re.sub(r'0(?=\d)', '0.', game_name, count=1)
                    data_temp['online_days'] = '0'
                    reconciliation_ratio = 1

                data_temp['banhao'] = data_temp['game_name'].split('（')[0]
                self.game_name_temp[game_name] = {
                    'game_name': data_temp['game_name'],
                    'online_days': data_temp['online_days'],
                    'banhao': data_temp['banhao'],
                    'reconciliation_ratio': reconciliation_ratio
                }

            def safe_float(val):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0.0

            def safe_int(val):
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return 0

            data_temp['recharge'] = round(safe_float(data.get('累计充值（元）')) * reconciliation_ratio, 2)
            data_temp['yesterday_actives'] = safe_int(data.get('昨日活跃用户（人）'))
            data_temp['channels'] = safe_int(data.get('渠道数量'))
            data_temp['subscribers'] = safe_int(data.get('累计用户（人）'))
            data_temp['devices'] = safe_int(data.get('累计设备（台）'))
            data_temp['payments'] = safe_int(data.get('付费用户（人）'))

            result.append(data_temp)
        return result


class QuickTotal:
    def __init__(self, shifting_days=0):
        self.host_url = 'http://127.0.0.1:5010'
        self.shifting_days = shifting_days

    def make_daily_report(self):
        quick_datas = []
        total_datas = {}
        bh_datas = self._initialize_bh_datas()
        quick_accounts = self.get_quick_accounts()

        for account in quick_accounts:
            try:
                quick_datas_temp = self.get_daily_reporter(account)
                quick_datas.extend(quick_datas_temp[0])
                total_datas = quick_datas_temp[1]
            except Exception as e:
                logger.error(f"Error processing account {account}: {e}")
                logger.error("Detailed traceback: %s", traceback.format_exc())

        bh_datas = self._aggregate_data(quick_datas, bh_datas)
        banhao_datas = self._format_banhao_data(bh_datas)
        return quick_datas, banhao_datas, total_datas

    @staticmethod
    def get_quick_accounts():
        return QuickAccount.objects.all()

    def get_daily_reporter(self, account):
        try:
            today = datetime.date.today()

            datas = self.get_income_details(account)
            yesterday_income = datas.get('yesterday_income', [])
            last_week_income = datas.get('last_week_income', [])
            last_month_income = datas.get('last_month_income', [])
            current_month_income = datas.get('current_month_income', [])
            this_month_income = datas.get('this_month_income', [])

            merged_data = self._merge_game_data(yesterday_income, last_week_income, last_month_income,
                                                current_month_income, this_month_income)
            self._add_game_info(merged_data, today)
            logger.info(f'日报获取成功, 共 {len(merged_data)} 条')
            return merged_data, self.get_total(merged_data)
        except Exception as e:
            logger.error(f"Error getting daily report: {e}")
            logger.error("Detailed traceback: %s", traceback.format_exc())
            return [], {}

    @staticmethod
    def get_total(datas):
        total = {
            'last1day_recharge': 0.0,
            'last7days_recharge': 0.0,
            'last30days_recharge': 0.0,
            'lastmonth_recharge': 0.0,
            'thismonth_recharge': 0.0,
            'yesterday_actives': 0,
            'last1day': {
                'channels_number': 0,
                'subscriber_number': 0,
                'devices_number': 0,
                'payment_number': 0,
            },
            'last7days': {
                'channels_number': 0,
                'subscriber_number': 0,
                'devices_number': 0,
                'payment_number': 0,
            },
            'last30days': {
                'channels_number': 0,
                'subscriber_number': 0,
                'devices_number': 0,
                'payment_number': 0,
            },
            'lastmonth': {
                'channels_number': 0,
                'subscriber_number': 0,
                'devices_number': 0,
                'payment_number': 0,
            },
            'thismonth': {
                'channels_number': 0,
                'subscriber_number': 0,
                'devices_number': 0,
                'payment_number': 0,
            },
        }
        for data in datas:
            total['last1day_recharge'] += data['last1day_recharge']
            total['last7days_recharge'] += data['last7days_recharge']
            total['last30days_recharge'] += data['last30days_recharge']
            total['lastmonth_recharge'] += data['lastmonth_recharge']
            total['thismonth_recharge'] += data['thismonth_recharge']
            total['yesterday_actives'] += data['yesterday_actives']
            total['last1day']['channels_number'] += data['last1day']['channels_number']
            total['last1day']['subscriber_number'] += data['last1day']['subscriber_number']
            total['last1day']['devices_number'] += data['last1day']['devices_number']
            total['last1day']['payment_number'] += data['last1day']['payment_number']
            total['last7days']['channels_number'] += data['last7days']['channels_number']
            total['last7days']['subscriber_number'] += data['last7days']['subscriber_number']
            total['last7days']['devices_number'] += data['last7days']['devices_number']
            total['last7days']['payment_number'] += data['last7days']['payment_number']
            total['last30days']['channels_number'] += data['last30days']['channels_number']
            total['last30days']['subscriber_number'] += data['last30days']['subscriber_number']
            total['last30days']['devices_number'] += data['last30days']['devices_number']
            total['last30days']['payment_number'] += data['last30days']['payment_number']
            total['lastmonth']['channels_number'] += data['lastmonth']['channels_number']
            total['lastmonth']['subscriber_number'] += data['lastmonth']['subscriber_number']
            total['lastmonth']['devices_number'] += data['lastmonth']['devices_number']
            total['lastmonth']['payment_number'] += data['lastmonth']['payment_number']
            total['thismonth']['channels_number'] += data['thismonth']['channels_number']
            total['thismonth']['subscriber_number'] += data['thismonth']['subscriber_number']
            total['thismonth']['devices_number'] += data['thismonth']['devices_number']
            total['thismonth']['payment_number'] += data['thismonth']['payment_number']

        for key in ['last1day_recharge', 'last7days_recharge', 'last30days_recharge', 'lastmonth_recharge',
                    'thismonth_recharge']:
            total[key] = round(total[key], 2)
        for key in ['last1day', 'last7days', 'last30days', 'lastmonth', 'thismonth']:
            total[key]['channels_number'] = int(total[key]['channels_number'])
            total[key]['subscriber_number'] = int(total[key]['subscriber_number'])
            total[key]['devices_number'] = int(total[key]['devices_number'])
            total[key]['payment_number'] = int(total[key]['payment_number'])
        return total

    def get_income_details(self, account) -> dict:
        try:
            result = requests.post(
                f'{self.host_url}/total',
                json={'account': account.account, 'password': account.password, 'shifting_days': self.shifting_days},
                timeout=300
            )
            if result.status_code == 200:
                return result.json()
            else:
                logger.error(f"Error getting income details: {result.text}")
                return {}
        except Exception as e:
            logger.error(f"Error getting income details: {e}")
            logger.error("Detailed traceback: %s", traceback.format_exc())
            return {}

    @staticmethod
    def _initialize_bh_datas():
        return defaultdict(lambda: {
            'last1day_recharge': 0.0,
            'last7days_recharge': 0.0,
            'last30days_recharge': 0.0,
            'lastmonth_recharge': 0.0,
            'thismonth_recharge': 0.0,
            'yesterday_actives': 0
        })

    @staticmethod
    def _aggregate_data(quick_datas, bh_datas):
        try:
            for quick_data in quick_datas:
                game_name = quick_data['game_name'].split('（')[0]
                for key in [
                    'last1day_recharge',
                    'last7days_recharge',
                    'last30days_recharge',
                    'lastmonth_recharge',
                    'thismonth_recharge'
                ]:
                    quick_data[key] = float(quick_data[key])
                    bh_datas[game_name][key] += quick_data[key]
                bh_datas[game_name]['yesterday_actives'] += int(quick_data['yesterday_actives'])
            return {k: {sub_k: round(sub_v, 2) for sub_k, sub_v in v.items()} for k, v in bh_datas.items()}
        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            logger.error("Detailed traceback: %s", traceback.format_exc())
            return bh_datas

    @staticmethod
    def _format_banhao_data(bh_datas):
        try:
            return [{
                '版号': k,
                'last1day_recharge': v['last1day_recharge'],
                'last7days_recharge': v['last7days_recharge'],
                'last30days_recharge': v['last30days_recharge'],
                'lastmonth_recharge': v['lastmonth_recharge'],
                'thismonth_recharge': v['thismonth_recharge'],
                'yesterday_actives': v['yesterday_actives']}
                for k, v in bh_datas.items()]
        except Exception as e:
            logger.error(f"Error formatting banhao data: {e}")
            logger.error("Detailed traceback: %s", traceback.format_exc())
            return []

    @staticmethod
    def search_game_by_quick_gamename(quick_gamename) -> Games:
        game = Games.objects.filter(quick_name=quick_gamename).first()
        return game if game else None

    @staticmethod
    def _merge_game_data(daily_data, weekly_data, monthly_data, current_month_data, this_month_income):
        try:
            merged_data = {}

            for data in daily_data:
                game_name = data["游戏名称"]
                merged_data[game_name] = {
                    "game_name": game_name,
                    "last1day_recharge": data.get("累计充值（元）", 0),
                    "last7days_recharge": 0,
                    "last30days_recharge": 0,
                    "lastmonth_recharge": 0,
                    "thismonth_recharge": 0,
                    'yesterday_actives': data.get('昨日活跃用户（人）', 0),
                    "last1day": {
                        "channels_number": data.get("渠道数量", 0),
                        "subscriber_number": data.get("累计用户（人）", 0),
                        "devices_number": data.get("累计设备（台）", 0),
                        "payment_number": data.get("付费用户（人）", 0),
                    },
                    'last7days': {
                        "channels_number": 0,
                        "subscriber_number": 0,
                        "devices_number": 0,
                        "payment_number": 0,
                    },
                    'last30days': {
                        "channels_number": 0,
                        "subscriber_number": 0,
                        "devices_number": 0,
                        "payment_number": 0,
                    },
                    'lastmonth': {
                        "channels_number": 0,
                        "subscriber_number": 0,
                        "devices_number": 0,
                        "payment_number": 0,
                    },
                    'thismonth': {
                        "channels_number": 0,
                        "subscriber_number": 0,
                        "devices_number": 0,
                        "payment_number": 0,
                    },
                }

            for data in weekly_data:
                game_name = data["游戏名称"]
                if game_name in merged_data:
                    merged_data[game_name]["last7days_recharge"] = data.get("累计充值（元）", 0)
                    merged_data[game_name]["last7days"] = {
                        "channels_number": data.get("渠道数量", 0),
                        "subscriber_number": data.get("累计用户（人）", 0),
                        "devices_number": data.get("累计设备（台）", 0),
                        "payment_number": data.get("付费用户（人）", 0),
                    }
                else:
                    merged_data[game_name] = {
                        "game_name": game_name,
                        "last1day_recharge": 0,
                        "last7days_recharge": data.get("累计充值（元）", 0),
                        "last30days_recharge": 0,
                        "lastmonth_recharge": 0,
                        "thismonth_recharge": 0,
                        'yesterday_actives': data.get('昨日活跃用户（人）', 0),
                        'last1day': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        "last7days": {
                            "channels_number": data.get("渠道数量", 0),
                            "subscriber_number": data.get("累计用户（人）", 0),
                            "devices_number": data.get("累计设备（台）", 0),
                            "payment_number": data.get("付费用户（人）", 0),
                        },
                        'last30days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'lastmonth': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'thismonth': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                    }

            for data in monthly_data:
                game_name = data["游戏名称"]
                if game_name in merged_data:
                    merged_data[game_name]["last30days_recharge"] = data.get("累计充值（元）", 0)
                    merged_data[game_name]["last30days"] = {
                        "channels_number": data.get("渠道数量", 0),
                        "subscriber_number": data.get("累计用户（人）", 0),
                        "devices_number": data.get("累计设备（台）", 0),
                        "payment_number": data.get("付费用户（人）", 0),
                    }
                else:
                    merged_data[game_name] = {
                        "game_name": game_name,
                        "last1day_recharge": 0,
                        "last7days_recharge": 0,
                        "last30days_recharge": data.get("累计充值（元）", 0),
                        "lastmonth_recharge": 0,
                        "thismonth_recharge": 0,
                        'yesterday_actives': data.get('昨日活跃用户（人）', 0),
                        'last1days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'last7days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        "last30days": {
                            "channels_number": data.get("渠道数量", 0),
                            "subscriber_number": data.get("累计用户（人）", 0),
                            "devices_number": data.get("累计设备（台）", 0),
                            "payment_number": data.get("付费用户（人）", 0),
                        },

                        'lastmonth': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'thismonth': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                    }

            for data in current_month_data:
                game_name = data["游戏名称"]
                if game_name in merged_data:
                    merged_data[game_name]["lastmonth_recharge"] = data.get("累计充值（元）", 0)
                    merged_data[game_name]["lastmonth"] = {
                        "channels_number": data.get("渠道数量", 0),
                        "subscriber_number": data.get("累计用户（人）", 0),
                        "devices_number": data.get("累计设备（台）", 0),
                        "payment_number": data.get("付费用户（人）", 0),
                    }
                else:
                    merged_data[game_name] = {
                        "game_name": game_name,
                        "last1day_recharge": 0,
                        "last7days_recharge": 0,
                        "last30days_recharge": 0,
                        "lastmonth_recharge": data.get("累计充值（元）", 0),
                        "thismonth_recharge": 0,
                        'yesterday_actives': data.get('昨日活跃用户（人）', 0),
                        'last1days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'last7days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'last30days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        "lastmonth": {
                            "channels_number": data.get("渠道数量", 0),
                            "subscriber_number": data.get("累计用户（人）", 0),
                            "devices_number": data.get("累计设备（台）", 0),
                            "payment_number": data.get("付费用户（人）", 0),
                        },
                        'thismonth': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                    }
            for data in this_month_income:
                game_name = data["游戏名称"]
                if game_name in merged_data:
                    merged_data[game_name]["thismonth_recharge"] = data.get("累计充值（元）", 0)
                    merged_data[game_name]["thismonth"] = {
                        "channels_number": data.get("渠道数量", 0),
                        "subscriber_number": data.get("累计用户（人）", 0),
                        "devices_number": data.get("累计设备（台）", 0),
                        "payment_number": data.get("付费用户（人）", 0),
                    }
                else:
                    merged_data[game_name] = {
                        "game_name": game_name,
                        "last1day_recharge": 0,
                        "last7days_recharge": 0,
                        "last30days_recharge": 0,
                        "lastmonth_recharge": 0,
                        "thismonth_recharge": data.get("累计充值（元）", 0),
                        'yesterday_actives': data.get('昨日活跃用户（人）', 0),
                        'last1days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'last7days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        'last30days': {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        "lastmonth": {
                            "channels_number": 0,
                            "subscriber_number": 0,
                            "devices_number": 0,
                            "payment_number": 0,
                        },
                        "thismonth": {
                            "channels_number": data.get("渠道数量", 0),
                            "subscriber_number": data.get("累计用户（人）", 0),
                            "devices_number": data.get("累计设备（台）", 0),
                            "payment_number": data.get("付费用户（人）", 0),
                        },
                    }
            return list(merged_data.values())
        except Exception as e:
            logger.error(f"Error merging game data: {e}")
            logger.error("Detailed traceback: %s", traceback.format_exc())
            return []

    def _add_game_info(self, merged_data, today):
        try:
            for data in merged_data:
                game_info: Games = self.search_game_by_quick_gamename(data['game_name'])
                if game_info:
                    launch_days = (today - game_info.release_date).days
                    data['online_days'] = launch_days
                    data['game_name'] = game_info.name
                    reconciliation_ratio = float(game_info.reconciliation_ratio)
                else:
                    data['online_days'] = '未知'
                    data['game_name'] = re.sub(r'0(?=\d)', '0.', data['game_name'], count=1)
                    reconciliation_ratio = 1
                data['last1day_recharge'] = round(data['last1day_recharge'] * reconciliation_ratio, 2)
                data['last7days_recharge'] = round(data['last7days_recharge'] * reconciliation_ratio, 2)
                data['last30days_recharge'] = round(data['last30days_recharge'] * reconciliation_ratio, 2)
                data['lastmonth_recharge'] = round(data['lastmonth_recharge'] * reconciliation_ratio, 2)
                data['thismonth_recharge'] = round(data['thismonth_recharge'] * reconciliation_ratio, 2)
                for key in ['last1day', 'last7days', 'last30days', 'lastmonth', 'thismonth']:
                    if data.get(key):
                        data[key]['channels_number'] = int(data[key].get('channels_number', 0))
                        data[key]['subscriber_number'] = int(data[key].get('subscriber_number', 0))
                        data[key]['devices_number'] = int(data[key].get('devices_number', 0))
                        data[key]['payment_number'] = int(data[key].get('payment_number', 0))
                    else:
                        data[key] = {
                            'channels_number': 0,
                            'subscriber_number': 0,
                            'devices_number': 0,
                            'payment_number': 0
                        }

        except Exception as e:
            logger.error(f"Error adding game info: {e}")
            logger.error("Detailed traceback: %s", traceback.format_exc())


def renew_console(account: ConsoleAccount, instance_id: str):
    configuration = Configuration()
    configuration.ak = account.access_key
    configuration.sk = account.secret_key
    configuration.region = "cn-shanghai"
    # set default configuration
    Configuration.set_default(configuration)

    # use global default configuration
    api_instance = ECSApi()
    renew_instance_request = RenewInstanceRequest(
        instance_id=instance_id,
        period=1,
        period_unit="Month",
    )

    try:
        result = api_instance.renew_instance(renew_instance_request).to_dict()
        del configuration, api_instance, renew_instance_request
        return {'status': True, 'message': '续费成功', 'data': result}
    except ApiException as e:
        return {'status': False, 'message': '续费失败', 'data': str(e)}


def send_email(subject, message, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,

        )
        return True
    except Exception as e:
        logger.error(f"Send email error: {e}")
        logger.error("Detailed traceback: %s", traceback.format_exc())
        return False


def rebuide_datas_report(in_datas: dict):
    datas = deepcopy(in_datas)
    income_datas = []
    data_id = 0
    data_index = 1
    for data in datas['income']:
        income_data = {
            'id': data_id,
            'index': f'{data_index}',
            'include': '昨日',
            'game_name': data['game_name'],
            'recharge': data['last1day_recharge'],
            'online_days': data['online_days'],
            'yesterday_actives': data['yesterday_actives'],
            'channels_number': data['last1day']['channels_number'],
            'subscribers': data['last1day']['subscriber_number'],
            'payments': data['last1day']['payment_number'],
            'children': [
                {
                    'id': data_id + 1,
                    'index': f'{data_index} - 1',
                    'include': '前七日',
                    'game_name': '',
                    'recharge': data['last7days_recharge'],
                    'online_days': '',
                    'yesterday_actives': '',
                    'channels_number': data['last7days']['channels_number'],
                    'subscribers': data['last7days']['subscriber_number'],
                    'payments': data['last7days']['payment_number'],
                },
                {
                    'id': data_id + 2,
                    'index': f'{data_index} - 2',
                    'include': '前三十日',
                    'game_name': '',
                    'recharge': data['last30days_recharge'],
                    'online_days': '',
                    'yesterday_actives': '',
                    'channels_number': data['last30days']['channels_number'],
                    'subscribers': data['last30days']['subscriber_number'],
                    'payments': data['last30days']['payment_number'],
                },
                {
                    'id': data_id + 3,
                    'index': f'{data_index} - 3',
                    'include': '上个月',
                    'game_name': '',
                    'recharge': data['lastmonth_recharge'],
                    'online_days': '',
                    'yesterday_actives': '',
                    'channels_number': data['lastmonth']['channels_number'],
                    'subscribers': data['lastmonth']['subscriber_number'],
                    'payments': data['lastmonth']['payment_number'],
                },
                {
                    'id': data_id + 4,
                    'index': f'{data_index} - 4',
                    'include': '当前月',
                    'game_name': '',
                    'recharge': data['thismonth_recharge'],
                    'online_days': '',
                    'yesterday_actives': '',
                    'channels_number': data['thismonth']['channels_number'],
                    'subscribers': data['thismonth']['subscriber_number'],
                    'payments': data['thismonth']['payment_number'],
                }
            ]
        }
        income_datas.append(income_data)
        data_id += 5
        data_index += 1
    datas['income'] = income_datas
    return datas
