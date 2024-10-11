"""
Creation date: 2024/10/10
Creation Time: 上午10:28
DIR PATH: backend/jtgame/service_table
Project Name: Manager_dvadmin
FILE NAME: views.py
Editor: 30386
"""
import os
import re
from datetime import timedelta

import pandas as pd
from django.http import JsonResponse, HttpResponse
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.game_manage.models import Channel
from jtgame.service_table.models import ServiceTableTemplate, ServiceTableNormal
from jtgame.service_table.utils import build_output_path


# Create your views here.
class ServiceTableTemplateSerializer(CustomModelSerializer):
    channel_name = serializers.SlugRelatedField(slug_field='name', source='channel', read_only=True, label='渠道名称')

    class Meta:
        model = ServiceTableTemplate
        fields = '__all__'


class ServiceTableTemplateViewSet(CustomModelViewSet):
    queryset = ServiceTableTemplate.objects.all()
    serializer_class = ServiceTableTemplateSerializer

    @action(methods=['post'], detail=False, name='上传服务表模板', url_path='uploadTemplate')
    def upload_template(self, request):
        """
        上传开服表模板
        """
        if request.user.is_anonymous:
            return JsonResponse({"error": "未登录用户无法上传文件"}, status=200)

        if request.method == 'POST':
            try:
                template_file = request.FILES.get('file')
                channel_id = request.POST.get('channel_id')
                if not channel_id:
                    return JsonResponse({"error": "未选择渠道"}, status=200)
                channel = Channel.objects.filter(id=channel_id).first()
                if not channel:
                    return JsonResponse({"error": "未找到渠道"}, status=200)
                template_fields = request.POST.get('fields')
                if not template_fields:
                    return JsonResponse({"error": "未填写字段"}, status=200)
                is_split = request.POST.get('is_split')
                if not is_split:
                    return JsonResponse({"error": "未选择是否分表"}, status=200)

                output_path = build_output_path()
                if template_file:
                    template_file_path = f"{output_path}/{template_file.name}"
                    with open(template_file_path, 'wb') as f:
                        for chunk in template_file.chunks():
                            f.write(chunk)
                    template_fields = template_fields.strip().replace(' ', '').replace('\n', '').replace('，', ',')
                    template = ServiceTableTemplate.objects.create(
                        channel=channel,
                        template_path=template_file_path,
                        template_fields=template_fields,
                        is_split=is_split,
                        is_enable=True,
                        creator=request.user,
                        dept_belong_id=request.user.dept_belong_id
                    )

                    return JsonResponse({"message": f"上传成功, 模板ID: {template.id}"}, status=200)
                else:
                    return JsonResponse({"error": "未找到文件"}, status=200)
            except Exception as e:
                logger.error(f"上传服务表模板失败，错误信息：{str(e)}")
                return JsonResponse({"error": "上传失败"}, status=200)
        return JsonResponse({"error": "请求方式错误"}, status=200)


class ServiceTableNormalSerializer(CustomModelSerializer):
    class Meta:
        model = ServiceTableNormal
        fields = '__all__'


class ServiceTableNormalViewSet(CustomModelViewSet):
    queryset = ServiceTableNormal.objects.all()
    serializer_class = ServiceTableNormalSerializer

    def get_object(self) -> ServiceTableNormal:
        filter_kwargs = {'id': self.kwargs['pk']}
        obj = self.queryset.filter(**filter_kwargs).first()
        return obj

    @action(methods=['get'], detail=True, name='生成开服表', url_path='generateServiceTable')
    def generate_service_table(self, request, pk=None):
        """
        生成开服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"error": "未登录用户无法生成开服表"}, status=200)

        if request.method == 'GET':
            try:
                normal = self.get_object()
                if not normal:
                    return JsonResponse({"error": "未找到开服表"}, status=200)

                output_path = build_output_path()
                first_service_path = f"{output_path}/{normal.game_name}_带首服.xlsx"
                no_first_service_path = f"{output_path}/{normal.game_name}.xlsx"
                start_datetime = normal.open_datetime
                frequency = normal.open_frequency
                count = normal.open_count
                normal.copy_content = ''
                data = []

                server_name_match = re.search(r"(\D+)(\d+)(\D*)", normal.open_name)
                if not server_name_match:
                    return JsonResponse({"error": "开服名称格式错误"}, status=200)
                server_name_prefix = server_name_match.group(1) + '{}' + server_name_match.group(3)
                server_name_suffix = int(server_name_match.group(2))

                for _ in range(count + 1):
                    server_name = server_name_prefix.format(server_name_suffix)
                    current_date = start_datetime.strftime("%Y/%m/%d")
                    current_time = start_datetime.strftime("%H:%M:%S")
                    current_datetime = start_datetime.strftime("%Y/%m/%d %H:%M")
                    data.append([normal.game_name, current_date, current_time,
                                 current_datetime, server_name, server_name_suffix])
                    normal.copy_content += f"{server_name}\t{current_time}" + '\n'.join('' for _ in range(frequency)) + '\n'
                    start_datetime += timedelta(days=frequency)
                    server_name_suffix += 1

                columns = ['游戏名', '日期', '时间', '开服时间', '区服名称', '区服序号']
                df = pd.DataFrame(data, columns=columns)
                df.to_excel(first_service_path, index=False)
                df.iloc[1:].to_excel(no_first_service_path, index=False)

                normal.first_service_path = first_service_path
                normal.no_first_service_path = no_first_service_path

                normal.generate_status = '1'
                normal.save()
                return JsonResponse({"message": "生成成功"}, status=200)
            except Exception as e:
                logger.error(f"生成开服表失败，错误信息：{str(e)}")
                return JsonResponse({"error": f"生成失败: {e}"}, status=200)
        return JsonResponse({"error": "请求方式错误"}, status=200)

    @action(methods=['get'], detail=True, name='下载带首服表', url_path='DownloadFirst')
    def download_first_service(self, request, pk=None):
        """
        下载带首服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"error": "未登录用户无法下载文件"}, status=200)

        if request.method == 'GET':
            try:
                normal = self.get_object()
                if not normal:
                    return JsonResponse({"error": "未找到开服表"}, status=200)

                if not normal.first_service_path:
                    return JsonResponse({"error": "未找到带首服表"}, status=200)

                with open(normal.first_service_path, 'rb') as f:
                    response = HttpResponse(
                        f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(normal.first_service_path)}'
                    return response
            except Exception as e:
                logger.error(f"下载带首服表失败，错误信息：{str(e)}")
                return JsonResponse({"error": "下载失败"}, status=200)
        return JsonResponse({"error": "请求方式错误"}, status=200)

    @action(methods=['get'], detail=True, name='下载不带首服表', url_path='DownloadNoFirst')
    def download_no_first_service(self, request, pk=None):
        """
        下载不带首服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"error": "未登录用户无法下载文件"}, status=200)

        if request.method == 'GET':
            try:
                normal = self.get_object()
                if not normal:
                    return JsonResponse({"error": "未找到开服表"}, status=200)

                if not normal.no_first_service_path:
                    return JsonResponse({"error": "未找到不带首服表"}, status=200)

                with open(normal.no_first_service_path, 'rb') as f:
                    response = HttpResponse(
                        f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(normal.no_first_service_path)}'
                    return response
            except Exception as e:
                logger.error(f"下载不带首服表失败，错误信息：{str(e)}")
                return JsonResponse({"error": "下载失败"}, status=200)
        return JsonResponse({"error": "请求方式错误"}, status=200)
