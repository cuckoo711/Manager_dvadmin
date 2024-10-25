import json
from datetime import datetime
from time import sleep

from django.http import JsonResponse
from rest_framework.decorators import action

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from apps.jtgame.daily_report.models import ConsoleAccount, QuickAccount, ReportData, Consoles
from apps.jtgame.daily_report.tasks import task__update_consoles, task__renew


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
                return JsonResponse(result.data if result else {}, status=200)
            except Exception as e:
                return JsonResponse({"error": f"Server error: {e}"}, status=500)
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            result = self.queryset.filter(date=date).first()
            return JsonResponse(result.data if result else {}, status=200)


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

    @action(detail=False, methods=['get'])
    def manual_refresh(self, request):
        try:
            task__update_consoles.apply_async().get()
            return JsonResponse({"message": "更新操作已提交", "status": True})
        except Exception as e:
            return JsonResponse({"message": f"服务器错误: {e}", "status": False})

    @action(detail=True, methods=['put'])
    def renew(self, request, pk=None):
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
