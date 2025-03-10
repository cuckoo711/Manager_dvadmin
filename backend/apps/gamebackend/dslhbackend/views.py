import json
import re

import uuid6
from _socket import gethostbyname
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action

from apps.gamebackend.dslhbackend.models import DSLHServer, DSLHConfig, DSLHLog, DSLHMergeTask
from apps.gamebackend.dslhbackend.tasks import async_merge_task
from apps.gamebackend.dslhbackend.utils.default import DSLHDefault
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


# Create your views here.


class DSLHServerSerializer(CustomModelSerializer):
    class Meta:
        model = DSLHServer
        fields = '__all__'


class DSLHServerViewSet(CustomModelViewSet):
    queryset = DSLHServer.objects.all()
    serializer_class = DSLHServerSerializer

    def create(self, request, *args, **kwargs):
        web_url = request.data.get('web_url').strip()

        if not web_url.startswith('http'):
            raise serializers.ValidationError('网页地址必须以http或https开头')
        url_match = re.match(r"(?:https?://)?([^/]+)", web_url)
        if url_match:
            url = url_match.group(1).strip('/')
        else:
            raise serializers.ValidationError('网页地址格式错误')

        try:
            host = gethostbyname(url)
            request.data['server_host'] = host
        except Exception as e:
            logger.error(f"后台地址无法解析: {e}\n地址: {web_url}({url})")
            raise serializers.ValidationError('后台地址无法解析')
        url = f"https://{url}/gmop/"
        request.data['web_url'] = url
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='get_servers', url_name='get_servers')
    def get_servers(self, request, *args, **kwargs):
        servers = DSLHServer.objects.all()
        server_info = [{'gamename': server.gamename, 'id': server.id} for server in servers]
        return JsonResponse({'status': 2000, 'message': '获取成功', 'data': server_info})

    @action(methods=['get'], detail=True, url_path='get_admin_info', url_name='get_admin_info')
    def get_admin_info(self, request, *args, **kwargs):
        server = self.get_object()
        dslh = DSLHDefault(server.web_url, 'crcadmin', 'cCxy*jw1{sPsscaonima')
        server_info = {
            'servers': dslh.servers,
            'has_recharges': dslh.has_recharges,
            'no_recharges': dslh.no_recharges,
            'server_config': dslh.server_config,
            'gamename': server.gamename,
            'server_id': server.id
        }
        return JsonResponse({'status': 2000, 'message': '获取成功', 'data': server_info})

    @action(methods=['get'], detail=True, url_path='set_info', url_name='set_info')
    def set_info(self, request, *args, **kwargs):
        server = self.get_object()
        dslh = DSLHDefault(server.web_url, server.username, server.password)
        server_info = {
            'gamename': server.gamename,
            'servers': dslh.servers,
            'id': server.id
        }
        return JsonResponse({'status': 2000, 'message': '获取成功', 'data': server_info})

    @action(methods=['post'], detail=True, url_path='megeropt', url_name='megeropt')
    def megeropt(self, request, *args, **kwargs):
        server = self.get_object()
        dslh = DSLHDefault(server.web_url, server.username, server.password)
        startserverid = request.data.get('startserverid')
        endserverid = request.data.get('endserverid')
        sqlip = request.data.get('sqlip')
        isshow = request.data.get('isshow')
        gameip = request.data.get('gameip')
        gameport = request.data.get('gameport')
        ismerge = request.data.get('ismerge')
        state = request.data.get('state')
        if not all([startserverid, endserverid, sqlip, isshow, gameip, gameport, ismerge, state]):
            return JsonResponse({'status': 4000, 'message': '参数不全'})
        try:
            dslh.megeropt(
                startserverid,
                endserverid,
                sqlip,
                isshow,
                gameip,
                gameport,
                ismerge,
                state
            )
            return JsonResponse({'status': 2000, 'message': '合服操作成功'})
        except Exception as e:
            logger.error(f"合服失败: {e}")
            return JsonResponse({'status': 4000, 'message': '合服操作失败, 请检查参数并前往后台查看详情'})

    @action(methods=['post'], detail=False, url_path='megersql', url_name='megersql')
    def megersql(self, request, *args, **kwargs):
        remote_ip = request.data.get('remote_ip')
        remote_password = request.data.get('remote_password', "H^Fr%4NT^T*&3alo")
        mysql_password = request.data.get('mysql_password')
        prefix = request.data.get('prefix')
        start_id = request.data.get('start_id')
        end_id = request.data.get('end_id')
        dest_id = request.data.get('dest_id')
        merge_ids = request.data.get('merge_ids')
        merged_ids = request.data.get('merged_ids')

        async_merge_task.delay(
            DSLHMergeTask.objects.create(
                start_id=int(start_id),
                end_id=int(end_id),
                dest_id=dest_id,
                merge_ids=json.loads(json.dumps(merge_ids)),
                merged_ids=json.loads(json.dumps(merged_ids)),
                mysql_password=mysql_password,
                remote_ip=remote_ip,
                remote_password=remote_password,
                prefix=prefix,
                output_dir=uuid6.uuid6(),
                creator=request.user,
                dept_belong_id=request.user.dept.id if request.user.dept else None,
            ).pk
        )

        return JsonResponse({'status': 2000, 'message': '合服任务已提交'})


class DSLHConfigSerializer(CustomModelSerializer):
    class Meta:
        model = DSLHConfig
        fields = '__all__'
        extra_kwargs = {
            "config_value": {"write_only": True},
        }


class DSLHConfigViewSet(CustomModelViewSet):
    queryset = DSLHConfig.objects.all()
    serializer_class = DSLHConfigSerializer


class DSLHLogSerializer(CustomModelSerializer):
    class Meta:
        model = DSLHLog
        fields = '__all__'


class DSLHLogViewSet(CustomModelViewSet):
    queryset = DSLHLog.objects.all()
    serializer_class = DSLHLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        creator_name = self.request.query_params.get('creator_name')
        if creator_name:
            queryset = queryset.filter(creator__username=creator_name)
        return queryset

    @action(methods=['post'], detail=False, url_path='addlog', url_name='addlog')
    def add(self, request, *args, **kwargs):
        log_data = request.data
        serializer = self.get_serializer(data=log_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'status': 2000, 'message': '添加成功'})
        return JsonResponse({'status': 4000, 'message': '添加失败'})


class DSLHMergeTaskSerializer(CustomModelSerializer):
    class Meta:
        model = DSLHMergeTask
        exclude = ('mysql_password', 'remote_password')


class DSLHMergeTaskViewSet(CustomModelViewSet):
    queryset = DSLHMergeTask.objects.all()
    serializer_class = DSLHMergeTaskSerializer
