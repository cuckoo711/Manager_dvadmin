# Create your views here.

import json
from datetime import datetime

from django.http import JsonResponse
from rest_framework.decorators import action

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.income_statement.models import IncomeData
from jtgame.income_statement.tasks import task__make_daily_detail_report


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
    @action(detail=False, methods=['get'])
    def export_data(self, request, *args, **kwargs):
        """
        导出数据
        """
        try:
            data = self.queryset.all()
            if not data:
                return JsonResponse({"error": "No data"}, status=404)
            data = [i.data for i in data]
            return JsonResponse(data, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Server error: {e}"}, status=500)

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
