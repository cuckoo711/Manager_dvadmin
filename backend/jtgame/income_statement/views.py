# Create your views here.

import json
from datetime import datetime, timedelta

from django.http import JsonResponse, FileResponse
from rest_framework.decorators import action

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.income_statement.models import IncomeData
from jtgame.income_statement.tasks import task__make_daily_detail_report
from jtgame.income_statement.utils import IncomeExport


class IncomeDataSerializer(CustomModelSerializer):
    class Meta:
        model = IncomeData
        fields = '__all__'


class IncomeDataViewSet(CustomModelViewSet):
    queryset = IncomeData.objects.all()
    serializer_class = IncomeDataSerializer

    @action(detail=False, methods=['get', 'post'])
    def get_income(self, request, *args, **kwargs):
        """
        获取收入数据
        """
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

    @action(detail=False, methods=['get'])
    def manual_refresh(self, request, *args, **kwargs):
        """
        手动更新数据
        """
        try:
            result = task__make_daily_detail_report.delay()
            return JsonResponse({"message": f"任务已提交，任务ID: {result.id}", "status": True})
        except Exception as e:
            return JsonResponse({"error": f"Server error: {e}", "status": False})

    # 导出数据
    @action(detail=False, methods=['post'])
    def export_data(self, request, *args, **kwargs):
        """
        导出数据
        """

        try:
            post_data = json.loads(request.body)
            if not post_data or 'date' not in post_data:
                return JsonResponse({"status": False, "error": "无效数据"})

            date = datetime.strptime(post_data.get('date'), '%Y-%m-%d')
            yesterday_str = (date - timedelta(days=1)).strftime('%Y-%m-%d')
            last_week_str = (date - timedelta(days=7)).strftime('%Y-%m-%d') + ' ~ ' + yesterday_str
            last_month_str = (((date.replace(day=1) - timedelta(days=1)).replace(day=1)).strftime('%Y-%m-%d') +
                              ' ~ ' + yesterday_str)
            this_month_str = date.replace(day=1).strftime('%Y-%m-%d') + ' ~ ' + yesterday_str
            current_month_str = ((date.replace(day=1) - timedelta(days=1)).replace(day=1)).strftime('%Y年%m月')
            type_dict = {
                '0': ['yesterday_income', yesterday_str],
                '1': ['last_week_income', last_week_str],
                '2': ['last_month_income', last_month_str],
                '3': ['this_month_income', this_month_str],
                '4': ['current_month_income', current_month_str],
            }
            if 'type' not in post_data or post_data.get('type') not in type_dict:
                return JsonResponse({"status": False, "message": "无效数据"})
            _type, _date = type_dict[post_data.get('type')]
            file_name = f"{_date}流水报表.xlsx"
            return JsonResponse({
                "status": True,
                "data": {"type": _type, "date": date.strftime('%Y-%m-%d'), "date_str": _date},
                "filename": file_name})
        except Exception as e:
            return JsonResponse({"status": False, "message": f"服务器错误: {e}, {e.__class__.__name__}"})

    @action(detail=False, methods=['post'])
    def get_income_export(self, request, *args, **kwargs):
        """
        获取导出数据
        """
        try:
            post_data = json.loads(request.body)
            date = post_data.get('date')
            _type = post_data.get('type')
            date_str = post_data.get('date_str')
            result: IncomeData = self.queryset.filter(date=date).first()
            if not result:
                return JsonResponse({"status": False, "message": "没有找到数据"})
            data = result.data
            if not data or _type not in data:
                return JsonResponse({"status": False, "message": "没有数据"})
            build = IncomeExport(data[_type], date_str)
            build.write()
            response = FileResponse(
                build.save(),
                content_type=f'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;',
            )
            return response
        except Exception as e:
            return JsonResponse({"status": False, "message": f"服务器错误: {e}, {e.__class__.__name__}"})

# @csrf_exempt
# def get_income(request):
#     """
#     获取收入数据
#     """
#     if request.method == 'POST':
#         try:
#             post_data = json.loads(request.body)
#             if not post_data or 'date' not in post_data:
#                 return JsonResponse({"error": "Invalid data"}, status=400)
#             result = IncomeData.objects.filter(date=post_data.get('date')).first()
#             return JsonResponse(result.data if result else {}, status=200)
#         except Exception as e:
#             return JsonResponse({"error": f"Server error: {e}"}, status=500)
#     else:
#         date = datetime.now().strftime('%Y-%m-%d')
#         result = IncomeData.objects.filter(date=date).first()
#         return JsonResponse(result.data if result else {}, status=200)
