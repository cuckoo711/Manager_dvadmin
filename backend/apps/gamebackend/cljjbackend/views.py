import json
from copy import deepcopy
from datetime import datetime
from urllib.parse import urlparse, urljoin

from _socket import gethostbyname
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from apps.gamebackend.cljjbackend.models import CLJJServer, CLJJLog
from apps.gamebackend.cljjbackend.utils.metro_client import MetroClient
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





class MetroViewSet(ViewSet):
    # permission_classes = []  # 需要登录才能操作

    def get_client(self, server_id):
        if not server_id:
            return None, "缺少参数 server_id"
        try:
            server = CLJJServer.objects.get(id=server_id)
        except CLJJServer.DoesNotExist:
            return None, "游戏服不存在"
        
        parsed = urlparse(server.web_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        client = MetroClient(base_url=base_url)
        if not client.login():
             return None, "登录游戏后台失败"
        return client, None

    def log_operation(self, request, content):
        try:
            user = request.user if request.user.is_authenticated else None
            CLJJLog.objects.create(creator=user, log=content)
        except Exception as e:
            logger.error(f"日志记录失败: {e}")

    @action(detail=False, methods=['GET'])
    def search_user_info(self, request, *args, **kwargs):
        server_id = request.query_params.get('server_id')
        uid = str(request.query_params.get('uid', '')).strip()
        
        client, error = self.get_client(server_id)
        if error:
            return JsonResponse({'status': False, 'message': error, 'data': None})
            
        if not uid:
            return JsonResponse({'status': False, 'message': '缺少参数 uid', 'data': None})

        try:
            html = client.search_user(uid=uid)
            data = client.parse_search_result(html)
            return JsonResponse({'status': True, 'message': 'success', 'data': data})
        except Exception as e:
             return JsonResponse({'status': False, 'message': str(e), 'data': None})

    @action(detail=False, methods=['POST'])
    def delete_mails(self, request, *args, **kwargs):
        server_id = request.data.get('server_id')
        uid = str(request.data.get('uid', '')).strip()
        mail_ids = request.data.get('mail_ids', [])
        
        client, error = self.get_client(server_id)
        if error:
            return JsonResponse({'status': False, 'message': error, 'data': None})

        if isinstance(mail_ids, str):
            mail_ids = [s.strip() for s in mail_ids.split(',') if s.strip()]
        if not uid or not isinstance(mail_ids, list):
            return JsonResponse({'status': False, 'message': '参数错误', 'data': None})
            
        try:
            # 先查询邮件详情，用于日志记录
            mail_details = []
            try:
                html = client.search_user(uid=uid)
                search_data = client.parse_search_result(html)
                all_mails = search_data.get('usermails', [])
                for mail in all_mails:
                    if str(mail.get('mail_id')) in mail_ids:
                        mail_details.append(mail)
            except Exception as e:
                logger.error(f"查询邮件详情失败: {e}")

            text = client.delete_mails(uid=uid, mail_ids=[str(x).strip() for x in mail_ids if str(x).strip()])
            logger.info(f"delete_mails return: {text}")
            
            # 详细日志
            detail_str = f"删除邮件: ServerID={server_id}, UID={uid}, MailIDs={mail_ids}"
            if mail_details:
                detail_str += f", 详情: {json.dumps(mail_details, ensure_ascii=False)}"
            self.log_operation(request, detail_str)
            
            return JsonResponse({'status': True, 'message': 'success', 'data': text})
        except Exception as e:
            return JsonResponse({'status': False, 'message': str(e), 'data': None})

    @action(detail=False, methods=['GET'])
    def mail_backups(self, request, *args, **kwargs):
        server_id = request.query_params.get('server_id')
        user_id = str(request.query_params.get('user_id', '')).strip()
        
        client, error = self.get_client(server_id)
        if error:
            return JsonResponse({'status': False, 'message': error, 'data': None})
            
        if not user_id:
            return JsonResponse({'status': False, 'message': '缺少参数 user_id', 'data': None})
            
        try:
            html = client.get_mail_backups(char_id=user_id)
            data = client.parse_mail_backups(html)
            return JsonResponse({'status': True, 'message': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': False, 'message': str(e), 'data': None})

    @action(detail=False, methods=['POST'])
    def recover_mail_backups(self, request, *args, **kwargs):
        server_id = request.data.get('server_id')
        user_id = str(request.data.get('user_id', '')).strip()
        backup_ids = request.data.get('backup_ids', [])
        
        client, error = self.get_client(server_id)
        if error:
            return JsonResponse({'status': False, 'message': error, 'data': None})

        if isinstance(backup_ids, str):
            backup_ids = [s.strip() for s in backup_ids.split(',') if s.strip()]
        if not user_id or not isinstance(backup_ids, list):
            return JsonResponse({'status': False, 'message': '参数错误', 'data': None})
            
        try:
            # 先查询备份详情，用于日志记录
            backup_details = []
            try:
                html = client.get_mail_backups(char_id=user_id)
                backups = client.parse_mail_backups(html)
                for backup in backups:
                    if str(backup.get('backup_id')) in backup_ids:
                        backup_details.append(backup)
            except Exception as e:
                logger.error(f"查询备份详情失败: {e}")

            text = client.recover_mail_backups(user_id=user_id, backup_ids=[str(x).strip() for x in backup_ids if str(x).strip()])
            logger.info(f"recover_mail_backups return: {text}")
            
            # 详细日志
            detail_str = f"恢复邮件: ServerID={server_id}, UserID={user_id}, BackupIDs={backup_ids}"
            if backup_details:
                detail_str += f", 详情: {json.dumps(backup_details, ensure_ascii=False)}"
            self.log_operation(request, detail_str)

            return JsonResponse({'status': True, 'message': 'success', 'data': text})
        except Exception as e:
            return JsonResponse({'status': False, 'message': str(e), 'data': None})
