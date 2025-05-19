import json
from datetime import datetime, timedelta
from time import sleep

from django.db.models import Sum
from django.http import JsonResponse
from rest_framework.decorators import action

from apps.jtgame.daily_report.models import ConsoleAccount, QuickAccount, ReportData, Consoles, DayliData
from apps.jtgame.daily_report.tasks import task__update_consoles, task__renew
from apps.jtgame.daily_report.utils import ModifyInstanceSpec, rebuide_datas_report, ConsoleRun, create_record, \
    WeChatBot
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


# Create your views here.


class ConsoleAccountSerializer(CustomModelSerializer):
    class Meta:
        model = ConsoleAccount
        fields = '__all__'


class ConsoleAccountViewSet(CustomModelViewSet):
    queryset = ConsoleAccount.objects.all()
    serializer_class = ConsoleAccountSerializer


class QuickAccountSerializer(CustomModelSerializer):
    class Meta:
        model = QuickAccount
        fields = '__all__'


class QuickAccountViewSet(CustomModelViewSet):
    queryset = QuickAccount.objects.all()
    serializer_class = QuickAccountSerializer


class DailyReportSerializer(CustomModelSerializer):
    class Meta:
        model = ReportData
        fields = '__all__'


class DailyReportViewSet(CustomModelViewSet):
    queryset = ReportData.objects.all()
    serializer_class = DailyReportSerializer

    @action(detail=False, methods=['get', 'post'], url_path='get_report')
    def get_report(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                post_data = json.loads(request.body)
                if not post_data or 'date' not in post_data:
                    return JsonResponse({"error": "Invalid data"}, status=400)
                result = self.queryset.filter(date=post_data.get('date')).first()
                if not result or not result.data or not result.data.get('income'):
                    return JsonResponse({}, status=200)
                return JsonResponse(rebuide_datas_report(result.data), status=200)
            except Exception as e:
                return JsonResponse({"error": f"Server error: {e}"}, status=500)
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            result = self.queryset.filter(date=date).first()
            if not result or not result.data or not result.data.get('income'):
                return JsonResponse({}, status=200)
            return JsonResponse(rebuide_datas_report(result.data), status=200)


class DayliDataSerializer(CustomModelSerializer):
    class Meta:
        model = DayliData
        fields = '__all__'


class DayliDataViewSet(CustomModelViewSet):
    queryset = DayliData.objects.all()
    serializer_class = DailyReportSerializer

    @action(detail=False, methods=['get'], url_path='get_datas')
    def get_datas(self, request, *args, **kwargs):
        # 计算昨天和今天的日期
        today_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

        # 一次性查询今天和昨天的数据，减少数据库查询次数
        today_result = self.queryset.filter(date=today_date, data_type=0)
        yesterday_result = self.queryset.filter(date=yesterday_date, data_type=0)

        # 汇总今天和昨天的统计数据
        all_games_count = today_result.values('game_name').distinct().count()
        all_banhaos_count = today_result.values('banhao').distinct().count()
        all_recharge = today_result.aggregate(recharge=Sum('recharge'))['recharge'] or 0
        all_actives = today_result.aggregate(actives=Sum('actives'))['actives'] or 0

        all_games_count_yesterday = yesterday_result.values('game_name').distinct().count()
        all_banhaos_count_yesterday = yesterday_result.values('banhao').distinct().count()
        all_recharge_yesterday = yesterday_result.aggregate(recharge=Sum('recharge'))['recharge'] or 0
        all_actives_yesterday = yesterday_result.aggregate(actives=Sum('actives'))['actives'] or 0

        # 查询过去30天的数据，减少查询次数
        last_30_days_data = self.queryset.filter(
            date__gte=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            data_type=0
        ).values('date').annotate(
            daily_recharge=Sum('recharge'),
            daily_actives=Sum('actives'),
            daily_subscribers=Sum('subscribers'),
            daily_devices=Sum('devices'),
            daily_payments=Sum('payments'),
        )
        last_30_days_weekly_data = self.queryset.filter(
            date__gte=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            data_type=1
        ).values('date').annotate(
            weekly_recharge=Sum('recharge'),
        )
        last_30_days_monthly_data = self.queryset.filter(
            date__gte=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            data_type=2
        ).values('date').annotate(
            monthly_recharge=Sum('recharge'),
        )

        # 整理过去30天的数据
        last_30_days_datas = {
            "daily_recharge": [],
            "daily_actives": [],
            "daily_subscribers": [],
            "daily_devices": [],
            "daily_payments": [],
            "weekly_daily_recharge": [],
            "monthly_daily_recharge": [],
        }

        for data in last_30_days_data:
            last_30_days_datas['daily_recharge'].append(data['daily_recharge'] or 0)
            last_30_days_datas['daily_actives'].append(data['daily_actives'] or 0)
            last_30_days_datas['daily_subscribers'].append(data['daily_subscribers'] or 0)
            last_30_days_datas['daily_devices'].append(data['daily_devices'] or 0)
            last_30_days_datas['daily_payments'].append(data['daily_payments'] or 0)
        for data in last_30_days_weekly_data:
            last_30_days_datas['weekly_daily_recharge'].append(
                round(data['weekly_recharge'] / 7, 2) if data['weekly_recharge'] else 0)
        for data in last_30_days_monthly_data:
            last_30_days_datas['monthly_daily_recharge'].append(
                round(data['monthly_recharge'] / 30, 2) if data['monthly_recharge'] else 0)

        # 本月的所有版号的数据
        this_month_data = self.queryset.filter(date=today_date, data_type=4)
        banhaos = this_month_data.values_list('banhao', flat=True).distinct()

        banhaos_recharge_temp = {
            banhao: this_month_data.filter(banhao=banhao).aggregate(recharge=Sum('recharge'))['recharge'] or 0
            for banhao in banhaos
        }

        # 排序并取前10
        banhaos_recharge = sorted(banhaos_recharge_temp.items(), key=lambda x: x[1], reverse=True)
        banhaos_recharge = banhaos_recharge[:10] + [('其他', sum(x[1] for x in banhaos_recharge[10:]))]

        # 汇总最终数据
        datas = {
            "all_games_count": all_games_count,
            "all_games_ratio": str(
                round((all_games_count - all_games_count_yesterday), 2) if all_games_count_yesterday else 0),
            "all_banhaos_count": all_banhaos_count,
            "all_banhaos_ratio": str(
                round((all_banhaos_count - all_banhaos_count_yesterday), 2) if all_banhaos_count_yesterday else 0),
            "all_recharge": all_recharge,
            "all_recharge_ratio": str(
                round((all_recharge - all_recharge_yesterday), 2) if all_recharge_yesterday else 0),
            "all_actives": all_actives,
            "all_actives_ratio": str(round((all_actives - all_actives_yesterday), 2) if all_actives_yesterday else 0),
            **last_30_days_datas,
            "banhaos_recharge": dict(banhaos_recharge)
        }
        return JsonResponse(datas, status=200)


class ConsolesSerializer(CustomModelSerializer):
    class Meta:
        model = Consoles
        fields = '__all__'


class ConsolesExportSerializer(CustomModelSerializer):
    class Meta:
        model = Consoles
        fields = '__all__'


class ConsolesViewSet(CustomModelViewSet):
    queryset = Consoles.objects.all()
    serializer_class = ConsolesSerializer
    export_field_label = {
        "eip_address": "主IPv4地址",
        "account": "所属账号",
        "instance_id": "实例ID",
        "instance_name": "实例名称",
        "cpus": "CPU",
        "memory_size": "内存",
        "instance_charge_type": "实例计费类型",
        "expired_at": "到期时间",
        "created_at": "创建时间",
        "updated_at": "更新时间",
    }
    export_serializer_class = ConsolesExportSerializer

    def get_object(self) -> Consoles:
        filter_kwargs = {'id': self.kwargs['pk']}
        obj = self.queryset.filter(**filter_kwargs).first()
        return obj

    def get_queryset(self):
        if getattr(self, 'values_queryset', None):
            return self.values_queryset
        return super().get_queryset()

    @action(detail=True, methods=['post'], url_path='modify_instance_spec')
    def modify_instance_spec(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance:
                return JsonResponse({'status': False, 'message': '实例不存在'})
            server_spec = request.data.get('serverSpec')
            if not server_spec:
                return JsonResponse({'status': False, 'message': '缺少必要参数'})
            logger.info(f"修改实例规格: {instance.instance_id}, 规格: {server_spec}")
            modify= ModifyInstanceSpec(instance.account)
            modify_result = modify.modify_instance_spec(
                instance_id=instance.instance_id,
                server_spec=server_spec,
            )
            if not modify_result.get('status'):
                return JsonResponse({"message": "修改失败", "status": False})
            sleep(2)
            task__update_consoles.apply_async().get()
            return JsonResponse({"message": "修改成功", "status": True})
        except Exception as e:
            return JsonResponse({"message": f"服务器错误: {e}", "status": False})

    @action(detail=False, methods=['post'], url_path='create_instances')
    def create_instances(self, request):
        try:
            server_image = request.data.get('serverImage')
            server_spec = request.data.get('serverSpec')
            game_name = request.data.get('gameName')
            sub_domain = request.data.get('subDomain')

            if not server_image or not server_spec or not game_name or not sub_domain:
                return JsonResponse({"message": "缺少必要参数", "status": False})
            console_run = ConsoleRun()
            create_result = console_run.run_instances(
                name=game_name,
                new_name=sub_domain,
                image_id=server_image,
                server_spec=server_spec,
                dry_run=False
            )
            if not create_result:
                return JsonResponse({"message": f"创建失败", "status": False})
            instanceids = create_result.instance_ids
            if not instanceids:
                return JsonResponse({"message": "创建失败: 未返回实例ID", "status": False})
            ipv4_result = console_run.get_ipv4_from_instance(instanceids[0])
            if not ipv4_result.get('status'):
                return JsonResponse({"message": "创建失败: 未返回IPv4地址", "status": False})
            ipv4 = ipv4_result.get('result')
            record_result = create_record(ipv4, sub_domain)
            if not record_result.get('status'):
                return JsonResponse({"message": f"dnspod映射失败: {record_result.get('result')}", "status": False})
            else:
                webhook_key = "efd58ff8-22ab-44b1-b5fa-f494868ebfc0"
                wechat_bot = WeChatBot(webhook_key)
                message = (
                    f"实例创建成功\n"
                    f"实例ID: {instanceids[0]}\n"
                    f"IPv4地址: {ipv4}\n"
                    f"域名解析: {sub_domain}.jingtanggame.com"
                )
                wechat_bot.send_text(message)
                return JsonResponse({"message": "创建成功", "status": True})
        except Exception as e:
            return JsonResponse({"message": f"服务器错误: {e}", "status": False})

    @action(detail=False, methods=['get'])
    def manual_refresh(self, request):
        try:
            task__update_consoles.apply_async().get()
            return JsonResponse({"message": "更新操作已提交", "status": True})
        except Exception as e:
            return JsonResponse({"message": f"服务器错误: {e}", "status": False})

    @action(detail=True, methods=['put'])
    def renew(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.renewal_status:
                return JsonResponse({'status': False, 'message': '续费失败', 'data': '服务器正在续费中，请稍后再试'})

            response = task__renew.apply_async((instance.instance_id, instance.account)).get()
            sleep(5)
            task__update_consoles.apply_async().get()
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'status': False, 'message': '续费失败', 'data': str(e)})
