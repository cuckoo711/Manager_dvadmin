"""
Creation date: 2024/10/10
Creation Time: 上午10:28
DIR PATH: backend/jtgame/service_table
Project Name: Manager_dvadmin
FILE NAME: views.py
Editor: 30386
"""
import os
import shutil
from datetime import datetime

from celery import chain
from django.http import JsonResponse, HttpResponse
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.game_manage.models import Channel
from jtgame.service_table.models import ServiceTableTemplate, ServiceTableNormal
from jtgame.service_table.tasks import task__generate_service_table
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
                    template_fields = template_fields.strip().replace(' ', '').replace('\n', '').replace(
                        '，', ',').replace('、', ',')
                    template = ServiceTableTemplate.objects.create(
                        channel=channel,
                        template_path=template_file_path,
                        template_fields=template_fields,
                        is_split=is_split,
                        is_enable="1",
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

                response = task__generate_service_table(normal.id).apply_async().get()
                return JsonResponse(response, status=200)
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
                    response[
                        'Content-Disposition'] = f'attachment; filename={os.path.basename(normal.first_service_path)}'
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
                    response[
                        'Content-Disposition'] = f'attachment; filename={os.path.basename(normal.no_first_service_path)}'
                    return response
            except Exception as e:
                logger.error(f"下载不带首服表失败，错误信息：{str(e)}")
                return JsonResponse({"error": "下载失败"}, status=200)
        return JsonResponse({"error": "请求方式错误"}, status=200)

    @action(methods=['post'], detail=False, name='批量下载开服表', url_path='batchDownloadServiceTable')
    def batch_download_service_table(self, request, pk=None):
        """
        批量下载开服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"error": "未登录用户无法下载文件"}, status=200)

        if request.method == 'POST':
            data = request.data
            if "ids" not in data:
                return JsonResponse({"error": "未选择开服表"}, status=200)
            ids = data.get("ids")
            first_service_path_list = []
            no_first_service_path_list = []
            for id_ in ids:
                normal = ServiceTableNormal.objects.filter(id=id_).first()
                if not normal:
                    continue
                if not normal.first_service_path:
                    continue
                first_service_path_list.append(normal.first_service_path)
                if not normal.no_first_service_path:
                    continue
                no_first_service_path_list.append(normal.no_first_service_path)
            temp_path = build_output_path()
            today = datetime.now().strftime("%Y-%m-%d")
            today_path = f"{temp_path}/{today}开服表"
            today_path_zip = f"{temp_path}/{today}开服表.zip"
            first_service_path = f"{today_path}/{today}开服表_带首服"
            no_first_service_path = f"{today_path}/{today}开服表_不带首服"
            os.makedirs(first_service_path, exist_ok=True)
            os.makedirs(no_first_service_path, exist_ok=True)

            for path in first_service_path_list:
                shutil.copy(path, first_service_path)
            for path in no_first_service_path_list:
                shutil.copy(path, no_first_service_path)

            shutil.make_archive(today_path, 'zip', today_path)
            shutil.rmtree(today_path)

            with open(today_path_zip, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                return response

        return JsonResponse({"error": "请求方式错误"}, status=200)
