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

import pandas as pd
from django.http import JsonResponse, HttpResponse
from rest_framework import serializers
from rest_framework.decorators import action

from application import settings
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.service_table.models import ServiceTableTemplate, ServiceTableNormal, ServiceTableSplit, \
    ServiceTableChannel, ServiceTableMap
from jtgame.service_table.tasks import task__generate_service_table, task__generate_service_split_table
from jtgame.service_table.utils.buildpath import build_template_output_path, build_server_table_output_path, \
    build_server_split_output_path


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
                header = map_pd.columns[1:]
                count = 0

                # 清空原有数据
                ServiceTableMap.objects.all().delete()

                for index, row in map_pd.iterrows():
                    for i in range(len(header)):
                        if not row[header[i]] or row[header[i]] == 'nan' or pd.isnull(row[header[i]]):
                            continue
                        channel = ServiceTableChannel.objects.filter(column=header[i]).first()
                        if not channel:
                            continue
                        ServiceTableMap.objects.create(
                            game_name=row['游戏名'],
                            channel=channel,
                            game_map_name=row[header[i]]
                        )
                        count += 1
                return JsonResponse({"message": f"上传成功, 共上传{count}条数据, 有效列名: {header}"}, status=200)
            except Exception as e:
                logger.error(f"上传开服表映射失败，错误信息：{str(e)}")
                return JsonResponse({"message": "上传失败"}, status=200)


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

    @action(methods=['post'], detail=False, name='上传服务表模板', url_path='uploadTemplate')
    def upload_template(self, request):
        """
        上传开服表模板
        """
        if request.user.is_anonymous:
            return JsonResponse({"message": "未登录用户无法上传文件"}, status=200)

        if request.method == 'POST':
            try:
                template_file = request.FILES.get('file')
                channel_id = request.POST.get('channel_id')
                if not channel_id:
                    return JsonResponse({"message": "未选择渠道"}, status=200)
                channel = ServiceTableChannel.objects.filter(id=channel_id).first()
                if not channel:
                    return JsonResponse({"message": "未找到渠道"}, status=200)
                template_fields = request.POST.get('fields')
                if not template_fields:
                    return JsonResponse({"message": "未填写字段"}, status=200)
                is_split = request.POST.get('is_split')
                if not is_split:
                    return JsonResponse({"message": "未选择是否分表"}, status=200)

                output_path = build_template_output_path()
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
                    return JsonResponse({"message": "未找到文件"}, status=200)
            except Exception as e:
                logger.error(f"上传服务表模板失败，错误信息：{str(e)}")
                return JsonResponse({"message": "上传失败"}, status=200)
        return JsonResponse({"message": "请求方式错误"}, status=200)


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
    class Meta:
        model = ServiceTableSplit
        fields = '__all__'


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
