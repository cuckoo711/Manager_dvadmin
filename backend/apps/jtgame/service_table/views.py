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
from copy import deepcopy
from datetime import datetime

import pandas as pd
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action

from application import settings
from apps.jtgame.service_table.models import ServiceTableChannel, ServiceTableMap, ServiceTableNormal, \
    ServiceTableSplit, ServiceTableTemplate
from apps.jtgame.service_table.tasks import async_updload_map, task__generate_service_split_table, \
    task__generate_service_table
from apps.jtgame.service_table.utils.buildpath import build_server_split_output_path, build_server_table_output_path
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


# Create your views here.

class ServiceTableChannelSerializer(CustomModelSerializer):
    class Meta:
        model = ServiceTableChannel
        fields = '__all__'

    #    列名可以为空
    def validate(self, attrs):
        if not attrs.get('column'):
            attrs['column'] = ''
        return attrs


class ServiceTableChannelViewSet(CustomModelViewSet):
    queryset = ServiceTableChannel.objects.all()
    serializer_class = ServiceTableChannelSerializer

    # 列名可以为空
    def perform_create(self, serializer):
        if not serializer.validated_data.get('column'):
            serializer.validated_data['column'] = ''
        serializer.save()


class ServiceTableMapSerializer(CustomModelSerializer):
    channel_name = serializers.SlugRelatedField(
        slug_field='name', source='channel', read_only=True, label='渠道')
    channel_column = serializers.SlugRelatedField(
        slug_field='column', source='channel', read_only=True, label='列名')

    class Meta:
        model = ServiceTableMap
        fields = '__all__'


class ServiceTableMapViewSet(CustomModelViewSet):
    queryset = ServiceTableMap.objects.all()
    serializer_class = ServiceTableMapSerializer

    def get_queryset(self):
        queryset = self.queryset
        channel_name = self.request.query_params.get('channel_name')
        if channel_name:
            queryset = queryset.filter(channel__name=channel_name)
        channel_column = self.request.query_params.get('channel_column')
        if channel_column:
            queryset = queryset.filter(channel__column=channel_column)
        return queryset

    @action(methods=['post'], detail=False, name='上传开服表映射', url_path='uploadMap')
    def upload_map(self, request):
        if request.user.is_anonymous:
            return JsonResponse({"detail": "未登录用户无法上传文件"}, status=200)

        if request.method == 'POST':
            try:
                map_file = request.FILES.get('file')
                if not map_file:
                    return JsonResponse({"message": "未找到文件"}, status=200)
                map_pd = pd.read_excel(map_file, dtype=str)
                header = map_pd.columns[1:].tolist()
                datas = [(index, row.to_dict()) for index, row in map_pd.iterrows()]

                with transaction.atomic():
                    ServiceTableMap.objects.all().delete()

                async_updload_map.delay(deepcopy(header), deepcopy(datas))
                return JsonResponse({"message": f"任务已提交,旧数据已清除,请稍后刷新页面查看新数据", "status": True},
                                    status=200)
            except Exception as e:
                logger.error(f"上传开服表映射失败,错误信息：{str(e)}")
                return JsonResponse({"message": "上传失败,请联系管理员", "status": False}, status=200)


class ServiceTableTemplateSerializer(CustomModelSerializer):
    channel_name = serializers.SlugRelatedField(
        slug_field='name', source='channel', read_only=True, label='渠道')

    class Meta:
        model = ServiceTableTemplate
        fields = '__all__'


class ServiceTableTemplateViewSet(CustomModelViewSet):
    queryset = ServiceTableTemplate.objects.all()
    serializer_class = ServiceTableTemplateSerializer

    def update(self, request, *args, **kwargs):
        request.data['template_fields'] = request.data['template_fields'].strip()
        if not (request.data['template_fields'].startswith('{') and request.data['template_fields'].endswith('}')):
            request.data['template_fields'] = request.data['template_fields'].replace(' ', '').replace(
                '\n', '').replace('，', ',').replace('、', ',')
        return super().update(request, *args, **kwargs)


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
            return JsonResponse({"message": "未登录用户无法生成开服表"}, status=200)

        if request.method == 'GET':
            try:
                normal = self.get_object()
                if not normal:
                    return JsonResponse({"message": "未找到开服表"}, status=200)

                response = task__generate_service_table.apply_async(args=([normal.id],)).get()
                return JsonResponse(response, status=200)
            except Exception as e:
                logger.error(f"生成开服表失败，错误信息：{str(e)}")
                return JsonResponse({"message": f"生成失败: {e}"}, status=200)
        return JsonResponse({"message": "请求方式错误"}, status=200)

    @action(methods=['get'], detail=True, name='下载带首服表', url_path='DownloadFirst')
    def download_first_service(self, request, pk=None):
        """
        下载带首服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法下载文件"}, status=200)

        if request.method == 'GET':
            try:
                normal = self.get_object()
                if not normal:
                    return JsonResponse({"message": "未找到开服表"}, status=200)

                if not normal.first_service_path:
                    return JsonResponse({"message": "未找到带首服表"}, status=200)

                with open(normal.first_service_path, 'rb') as f:
                    response = HttpResponse(
                        f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = (f'attachment; '
                                                       f'filename={os.path.basename(normal.first_service_path)}')
                    return response
            except Exception as e:
                logger.error(f"下载带首服表失败，错误信息：{str(e)}")
                return JsonResponse({"message": "下载失败"}, status=200)
        return JsonResponse({"message": "请求方式错误"}, status=200)

    @action(methods=['get'], detail=True, name='下载不带首服表', url_path='DownloadNoFirst')
    def download_no_first_service(self, request, pk=None):
        """
        下载不带首服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法下载文件"}, status=200)

        if request.method == 'GET':
            try:
                normal = self.get_object()
                if not normal:
                    return JsonResponse({"message": "未找到开服表"}, status=200)

                if not normal.no_first_service_path:
                    return JsonResponse({"message": "未找到不带首服表"}, status=200)

                with open(normal.no_first_service_path, 'rb') as f:
                    response = HttpResponse(
                        f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response[
                        'Content-Disposition'] = f'attachment; filename={os.path.basename(normal.no_first_service_path)}'
                    return response
            except Exception as e:
                logger.error(f"下载不带首服表失败，错误信息：{str(e)}")
                return JsonResponse({"message": "下载失败"}, status=200)
        return JsonResponse({"message": "请求方式错误"}, status=200)

    @action(methods=['post'], detail=False, name='批量生成开服表', url_path='batchGenerateServiceTable')
    def batch_generate_service_table(self, request):
        """
        批量生成开服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法生成开服表"}, status=200)

        if request.method == 'POST':
            data = request.data
            if "ids" not in data:
                return JsonResponse({"message": "未选择开服表"}, status=200)
            ids = data.get("ids")
            do_ids = []
            for id_ in ids:
                normal = ServiceTableNormal.objects.filter(id=id_).first()
                if not normal:
                    continue
                do_ids.append(normal.id)
            response = task__generate_service_table.apply_async(args=(do_ids,)).get()
            return JsonResponse(response, status=200)

        return JsonResponse({"message": "请求方式错误"}, status=200)

    @action(methods=['post'], detail=False, name='批量下载开服表', url_path='batchDownloadServiceTable')
    def batch_download_service_table(self, request, pk=None):
        """
        批量下载开服表
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法下载文件"}, status=200)

        if request.method == 'POST':
            data = request.data
            if "ids" not in data:
                return JsonResponse({"message": "未选择开服表"}, status=200)
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
            temp_path = build_server_table_output_path()
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

        return JsonResponse({"message": "请求方式错误"}, status=200)

    @action(methods=['get'], detail=False, name='清理文件', url_path='cleanFiles')
    def clean_files(self, request):
        """
        清理文件
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法清理文件"}, status=200)

        if request.method == 'GET':
            file_list = []
            for normal in ServiceTableNormal.objects.all():
                if normal.first_service_path:
                    file_list.append(normal.first_service_path)
                if normal.no_first_service_path:
                    file_list.append(normal.no_first_service_path)
            try:
                output_path = settings.SERVER_TABLE_FILE_PATH
                for root, dirs, files in os.walk(output_path):
                    for file in files:
                        if os.path.join(root, file) not in file_list:
                            os.remove(os.path.join(root, file))
                return JsonResponse({"message": "清理成功", "status": True}, status=200)
            except Exception as e:
                logger.error(f"清理文件失败，错误信息：{str(e)}")
                return JsonResponse({"message": "清理失败", "status": False}, status=200)

        return JsonResponse({"message": "请求方式错误"}, status=200)

    @action(methods=['post'], detail=False, name='批量创建分表任务', url_path='batchSplitTaskServiceTable')
    def batch_create_split_task(self, request):
        """
        批量创建分表任务
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法创建分表任务"}, status=200)

        if request.method == 'POST':
            data = request.data
            if "ids" not in data:
                return JsonResponse({"message": "未选择开服表"}, status=200)
            ids = data.get("ids")
            normal_list = []
            for id_ in ids:
                normal = ServiceTableNormal.objects.filter(id=id_).first()
                if not normal:
                    continue
                normal_list.append(normal)

            split = ServiceTableSplit.objects.create(
                output_dir=build_server_split_output_path()
            )
            split.service_table_normals.set(normal_list)
            split.save()
            return JsonResponse({"message": f"创建成功, 分表ID: {split.id}"}, status=200)

        return JsonResponse({"message": "请求方式错误"}, status=200)


class ServiceTableSplitSerializer(CustomModelSerializer):
    game_infos = serializers.SerializerMethodField(label='游戏信息')

    class Meta:
        model = ServiceTableSplit
        fields = '__all__'

    @staticmethod
    def get_game_infos(obj):
        return ','.join([f"{normal.game_name}[隔{normal.open_frequency}开{normal.open_count}]" for normal in
                         obj.service_table_normals.all()])


class ServiceTableSplitViewSet(CustomModelViewSet):
    queryset = ServiceTableSplit.objects.all()
    serializer_class = ServiceTableSplitSerializer

    def get_object(self) -> ServiceTableSplit:
        filter_kwargs = {'id': self.kwargs['pk']}
        obj = self.queryset.filter(**filter_kwargs).first()
        return obj

    @action(methods=['get'], detail=True, name='生成分表', url_path='generateServiceSplitTable')
    def generate_service_split_table(self, request, pk=None):
        """
        生成分表
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法生成分表"}, status=200)

        if request.method == 'GET':
            try:
                split = self.get_object()
                if not split:
                    return JsonResponse({"message": "未找到分表"}, status=200)

                task__generate_service_split_table.delay(split.id)
                return JsonResponse({"message": "任务已提交"}, status=200)
            except Exception as e:
                logger.error(f"生成分表失败，错误信息：{str(e)}")
                return JsonResponse({"message": f"生成失败: {e}"}, status=200)
        return JsonResponse({"message": "请求方式错误"}, status=200)

    @action(methods=['get'], detail=True, name='下载分表压缩包', url_path='downloadSplitZip')
    def download_split_zip(self, request, pk=None):
        """
        下载分表压缩包
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法下载文件"}, status=200)

        if request.method == 'GET':
            try:
                split = self.get_object()
                if not split:
                    return JsonResponse({"message": "未找到分表"}, status=200)

                if not split.service_table_split_zip:
                    return JsonResponse({"message": "未找到分表压缩包"}, status=200)

                with open(split.service_table_split_zip, 'rb') as f:
                    response = HttpResponse(
                        f.read(), content_type='application/zip')
                    response['Content-Disposition'] = (f'attachment; '
                                                       f'filename={os.path.basename(split.service_table_split_zip)}')
                    return response
            except Exception as e:
                logger.error(f"下载分表压缩包失败，错误信息：{str(e)}")
                return JsonResponse({"message": "下载失败"}, status=200)
        return JsonResponse({"message": "请求方式错误"}, status=200)
