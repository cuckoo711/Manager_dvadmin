from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from apps.xiaoqi.canglan.utils.metro_client import MetroClient


class MetroViewSet(ViewSet):
    permission_classes = []

    @action(detail=False, methods=['GET'])
    def search_user_info(self, request, *args, **kwargs):
        uid = str(request.query_params.get('uid', '')).strip()
        if not uid:
            return JsonResponse({'status': False, 'message': '缺少参数 uid', 'data': None})
        client = MetroClient()
        if not client.login():
            return JsonResponse({'status': False, 'message': '登录失败', 'data': None})
        html = client.search_user(uid=uid)
        data = client.parse_search_result(html)
        return JsonResponse({'status': True, 'message': 'success', 'data': data})

    @action(detail=False, methods=['POST'])
    def delete_mails(self, request, *args, **kwargs):
        uid = str(request.data.get('uid', '')).strip()
        mail_ids = request.data.get('mail_ids', [])
        if isinstance(mail_ids, str):
            mail_ids = [s.strip() for s in mail_ids.split(',') if s.strip()]
        if not uid or not isinstance(mail_ids, list):
            return JsonResponse({'status': False, 'message': '参数错误', 'data': None})
        client = MetroClient()
        if not client.login():
            return JsonResponse({'status': False, 'message': '登录失败', 'data': None})
        text = client.delete_mails(uid=uid, mail_ids=[str(x).strip() for x in mail_ids if str(x).strip()])
        return JsonResponse({'status': True, 'message': 'success', 'data': text})

    @action(detail=False, methods=['GET'])
    def mail_backups(self, request, *args, **kwargs):
        user_id = str(request.query_params.get('user_id', '')).strip()
        if not user_id:
            return JsonResponse({'status': False, 'message': '缺少参数 user_id', 'data': None})
        client = MetroClient()
        if not client.login():
            return JsonResponse({'status': False, 'message': '登录失败', 'data': None})
        html = client.get_mail_backups(char_id=user_id)
        data = client.parse_mail_backups(html)
        return JsonResponse({'status': True, 'message': 'success', 'data': data})

    @action(detail=False, methods=['POST'])
    def recover_mail_backups(self, request, *args, **kwargs):
        user_id = str(request.data.get('user_id', '')).strip()
        backup_ids = request.data.get('backup_ids', [])
        if isinstance(backup_ids, str):
            backup_ids = [s.strip() for s in backup_ids.split(',') if s.strip()]
        if not user_id or not isinstance(backup_ids, list):
            return JsonResponse({'status': False, 'message': '参数错误', 'data': None})
        client = MetroClient()
        if not client.login():
            return JsonResponse({'status': False, 'message': '登录失败', 'data': None})
        text = client.recover_mail_backups(user_id=user_id, backup_ids=[str(x).strip() for x in backup_ids if str(x).strip()])
        return JsonResponse({'status': True, 'message': 'success', 'data': text})
