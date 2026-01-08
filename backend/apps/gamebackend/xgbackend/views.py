from urllib.parse import urlparse, urljoin

from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action

from apps.gamebackend.xgbackend.models import XGServer, XGUser, XGToken
from apps.gamebackend.xgbackend.utils.getInfos import ApiXGInfos
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


# Create your views here.
class XGUserSerializer(CustomModelSerializer):
    class Meta:
        model = XGUser
        fields = '__all__'
        extra_kwargs = {
            "password": {"write_only": True},
        }


class XGUserViewSet(CustomModelViewSet):
    queryset = XGUser.objects.all()
    serializer_class = XGUserSerializer


class XGServerSerializer(CustomModelSerializer):
    class Meta:
        model = XGServer
        fields = '__all__'
        read_only_fields = ["id"]


class XGServerViewSet(CustomModelViewSet):
    queryset = XGServer.objects.all()
    serializer_class = XGServerSerializer

    def create(self, request, *args, **kwargs):
        web_url = request.data.get('web_url').strip()
        if not web_url.startswith('http'):
            raise serializers.ValidationError('网页地址必须以http或https开头')
        parsed_url = urlparse(web_url)
        host_url = parsed_url.netloc if parsed_url.netloc else parsed_url.path.split("/")[0]
        base_url = parsed_url.scheme + "://" + host_url
        request.data['server_host'] = base_url
        request.data['web_url'] = urljoin(base_url, '/master/login.html')

        if not request.data.get('server_port'):
            request.data['server_port'] = '8080'
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='get_servers', url_name='get_servers')
    def get_servers(self, request, *args, **kwargs):
        servers = XGServer.objects.all()
        server_info = [{'gamename': server.gamename, 'id': server.id} for server in servers]
        return JsonResponse({'status': 2000, 'message': '获取成功', 'data': server_info})

    @action(methods=['get'], detail=True, url_path='set_info', url_name='set_info')
    def set_info(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        token = XGToken.objects.filter(user=user, game_server=instance).first()
        if not token:
            token = XGToken.objects.create(user=user, game_server=instance)
            token.update_token()

        infos = ApiXGInfos(token.id).run()
        return JsonResponse({"data": infos, "token": token.id, "status": 2000})
