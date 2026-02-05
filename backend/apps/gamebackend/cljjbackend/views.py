import json
from copy import deepcopy
from datetime import datetime
from urllib.parse import urlparse, urljoin

from _socket import gethostbyname
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action

from apps.gamebackend.cljjbackend.models import CLJJServer, CLJJLog
from dvadmin.system.models import DownloadCenter
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


# Create your views here.

class CLJJServerSerializer(CustomModelSerializer):
    class Meta:
        model = CLJJServer
        fields = '__all__'


class CLJJServerViewSet(CustomModelViewSet):
    queryset = CLJJServer.objects.all()
    serializer_class = CLJJServerSerializer

    def create(self, request, *args, **kwargs):
        web_url = request.data.get('web_url', '').strip()
        if not web_url.startswith('http'):
            raise serializers.ValidationError('网页地址必须以http或https开头')
        parsed_url = urlparse(web_url)
        host_url = parsed_url.netloc if parsed_url.netloc else parsed_url.path.split("/")[0]
        base_url = parsed_url.scheme + "://" + host_url
        # 假设登录页也是 /GmTool/page/login.html，如果不是需要修改
        request.data['web_url'] = urljoin(base_url, '/GmTool/page/login.html')

        try:
            host = gethostbyname(host_url)
            request.data['server_host'] = host
        except Exception as e:
            logger.error(f"后台地址无法解析: {e}\n地址: {web_url}")
            raise serializers.ValidationError('后台地址无法解析')
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='get_servers', url_name='get_servers')
    def get_servers(self, request, *args, **kwargs):
        servers = CLJJServer.objects.filter(is_active=True).all().order_by('-gamename')
        server_info = [{'gamename': server.gamename, 'id': server.id} for server in servers]
        return JsonResponse({'status': 2000, 'message': '获取成功', 'data': server_info})

    @action(methods=['get'], detail=True, url_path='set_info', url_name='set_info')
    def set_info(self, request, *args, **kwargs):
        instance = self.get_object()
        # 暂时返回空数据
        infos = {} 
        return JsonResponse({"data": infos, "status": 2000})


class CLJJLogSerializer(CustomModelSerializer):
    class Meta:
        model = CLJJLog
        fields = '__all__'


class CLJJLogViewSet(CustomModelViewSet):
    queryset = CLJJLog.objects.all()
    serializer_class = CLJJLogSerializer

    filter_fields = ['~log']

    def get_queryset(self):
        queryset = super().get_queryset()
        creator_name = self.request.query_params.get('creator_name')
        if creator_name:
            queryset = queryset.filter(creator__username__contains=creator_name)
        return queryset

    @action(methods=['post'], detail=False, url_path='addlog', url_name='addlog')
    def add(self, request, *args, **kwargs):
        log_data = request.data
        serializer = self.get_serializer(data=log_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'status': 2000, 'message': '添加成功'})
        return JsonResponse({'status': 4000, 'message': '添加失败'})
