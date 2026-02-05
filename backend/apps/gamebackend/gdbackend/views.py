import json
from copy import deepcopy
from datetime import datetime
from urllib.parse import urlparse, urljoin

from _socket import gethostbyname
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action

from apps.gamebackend.gdbackend.models import GDUser, GDServer, GDActiveConfig, GDToken, GDLog, GDActiveLog, GDRebateAudit
from apps.gamebackend.gdbackend.tasks import async_export_data
from apps.gamebackend.gdbackend.utils.addGifts import ApiAddGifts
from apps.gamebackend.gdbackend.utils.addWifes import ApiAddWifes
from apps.gamebackend.gdbackend.utils.delActivity import ApiDelActivity
from apps.gamebackend.gdbackend.utils.delGifts import ApiDelGifts
from apps.gamebackend.gdbackend.utils.delWifes import ApiDelWifes
from apps.gamebackend.gdbackend.utils.editActivity import ApiEditActivity
from apps.gamebackend.gdbackend.utils.editServerName import ApiEditServerName
from apps.gamebackend.gdbackend.utils.editWifes import ApiEditWifes
from apps.gamebackend.gdbackend.utils.getActivity import ApiGetActivity
from apps.gamebackend.gdbackend.utils.getGiftslist import ApiGetGiftsList
from apps.gamebackend.gdbackend.utils.getGiftslogs import ApiGetGiftsLogs
from apps.gamebackend.gdbackend.utils.getInfos import ApiGDInfos
from apps.gamebackend.gdbackend.utils.getLatestServers import ApiGetLatestServers
from apps.gamebackend.gdbackend.utils.getPinfo import ApiGDPInfos
from apps.gamebackend.gdbackend.utils.getWifesList import ApiGetWifesList
from apps.gamebackend.gdbackend.utils.sendGifts import ApiSendGifts
from apps.gamebackend.gdbackend.utils.uploadActivity import ApiUploadActivity
from apps.gamebackend.gdbackend.utils.util import process_lists
from dvadmin.system.models import DownloadCenter
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


# Create your views here.

class GDUserSerializer(CustomModelSerializer):
    class Meta:
        model = GDUser
        fields = '__all__'
        extra_kwargs = {
            "password": {"write_only": True},
        }


class GDUserViewSet(CustomModelViewSet):
    queryset = GDUser.objects.all()
    serializer_class = GDUserSerializer


class GDServerSerializer(CustomModelSerializer):
    class Meta:
        model = GDServer
        fields = '__all__'
        extra_kwargs = {
            "sql_pwd": {"write_only": True},
        }


class GDServerViewSet(CustomModelViewSet):
    queryset = GDServer.objects.all()
    serializer_class = GDServerSerializer

    def create(self, request, *args, **kwargs):
        web_url = request.data.get('web_url').strip()
        if not web_url.startswith('http'):
            raise serializers.ValidationError('网页地址必须以http或https开头')
        parsed_url = urlparse(web_url)
        host_url = parsed_url.netloc if parsed_url.netloc else parsed_url.path.split("/")[0]
        base_url = parsed_url.scheme + "://" + host_url
        request.data['web_url'] = urljoin(base_url, '/GmTool/page/login.html')

        try:
            host = gethostbyname(host_url)
            request.data['server_host'] = host
        except Exception as e:
            logger.error(f"后台地址无法解析: {e}\n地址: {web_url}")
            raise serializers.ValidationError('后台地址无法解析')
        if not request.data.get('server_port'):
            request.data['server_port'] = '8801'
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='get_servers', url_name='get_servers')
    def get_servers(self, request, *args, **kwargs):
        servers = GDServer.objects.filter(is_active=True).all().order_by('-gamename')
        server_info = [{'gamename': server.gamename, 'id': server.id} for server in servers]
        return JsonResponse({'status': 2000, 'message': '获取成功', 'data': server_info})

    @action(methods=['get'], detail=True, url_path='set_info', url_name='set_info')
    def set_info(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        token = GDToken.objects.filter(user=user, game_server=instance).first()
        if not token:
            token = GDToken.objects.create(
                user=user,
                game_server=instance,
                creator=user,
                dept_belong_id=user.dept.id if user.dept else None
            )
            token.update_token()

        infos = ApiGDInfos(token.id).run()
        return JsonResponse({"data": infos, "token": token.id, "status": 2000})


class GDTokensSerializer(CustomModelSerializer):
    user_name = serializers.SerializerMethodField()
    game_server_name = serializers.SerializerMethodField()

    class Meta:
        model = GDToken
        exclude = ['token', 'user', 'game_server']

    @staticmethod
    def get_user_name(obj):
        return obj.user.username

    @staticmethod
    def get_game_server_name(obj):
        return obj.game_server.gamename


class GDTokensViewSet(CustomModelViewSet):
    queryset = GDToken.objects.all()
    serializer_class = GDTokensSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_name = self.request.query_params.get('user_name')
        if user_name:
            queryset = queryset.filter(user__username=user_name)
        game_server_name = self.request.query_params.get('game_server_name')
        if game_server_name:
            queryset = queryset.filter(game_server__gamename=game_server_name)
        return queryset

    @action(methods=['post'], detail=True, url_path='get_pinfo', url_name='get_pinfo')
    def get_pinfo(self, request, *args, **kwargs):
        instance = self.get_object()
        pid = request.query_params.get('pid')
        if not pid:
            raise serializers.ValidationError('请填写pid')
        sid = request.query_params.get('sid')
        if not sid:
            raise serializers.ValidationError('请填写sid')
        pinfo = ApiGDPInfos(instance.id).run(server=sid, pid=pid)
        return JsonResponse({"data": {"roleName": pinfo[0], "charge": pinfo[1]}, "status": 2000})

    @action(methods=['post'], detail=True, url_path='del_gifts', url_name='del_gifts')
    def del_gifts(self, request, *args, **kwargs):
        instance = self.get_object()
        gift_ids = request.data.get('gift_ids')
        if not gift_ids or not isinstance(gift_ids, list):
            raise serializers.ValidationError('请填写gift_ids')
        result = ApiDelGifts(instance.id).run(gift_ids=gift_ids)
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['post'], detail=True, url_path='send_gifts', url_name='send_gifts')
    def send_gifts(self, request, *args, **kwargs):
        instance = self.get_object()
        server = request.data.get('server')
        if not server:
            raise serializers.ValidationError('请填写server')
        gifts_name = request.data.get('gifts_name')
        if not gifts_name:
            raise serializers.ValidationError('请填写gifts_name')
        pname = request.data.get('pname')
        gifts_id = request.data.get('gifts_id')
        if not gifts_id:
            raise serializers.ValidationError('请填写gifts_id')
        des = request.data.get('des')
        if not des:
            raise serializers.ValidationError('请填写des')
        # 查询角色名称
        role_name = None
        try:
            pinfo = ApiGDPInfos(instance.id).run(server=str(server), pid=str(pname))
            role_name = pinfo[0]
        except Exception:
            role_name = None
        # 查询或接收礼包名称
        gift_label = request.data.get('gifts_label')
        if not gift_label:
            try:
                infos = ApiGDInfos(instance.id).run()
                gifts_list = infos.get('Gifts', [])
                for g in gifts_list:
                    if str(g.get('value')) == str(gifts_id):
                        gift_label = g.get('label')
                        break
            except Exception:
                gift_label = None
        audit = GDRebateAudit.objects.create(
            game_server=instance.game_server,
            serverid=str(server),
            pid=str(pname),
            pname=role_name,
            gifts_name=gifts_name,
            gifts_id=str(gifts_id),
            gifts_label=gift_label,
            des=des,
            status=0,
            creator=request.user,
            dept_belong_id=request.user.dept.id if request.user.dept else None,
            description=f"""
            用户【{request.user.username}】提交了返利申请
            区服：【{server}】{instance.game_server}
            玩家：【{role_name}】（PID: {pname}）
            礼包：【{gifts_name}】（ID: {gifts_id}）
            备注：{des}
            时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
        )
        return JsonResponse({"msg": "已提交审核", "audit_id": audit.id, "status": 2000})

    @action(methods=['get'], detail=True, url_path='get_giftslogs', url_name='get_giftslogs')
    def get_giftslogs(self, request, *args, **kwargs):
        instance = self.get_object()
        start_time = request.query_params.get('startTime', '')
        stop_time = request.query_params.get('stopTime', '')
        prop = request.query_params.get('prop', '')
        server_name = request.query_params.get('serverName', '')
        player_name = request.query_params.get('playerNames', '')

        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') if start_time else ''
        stop_time = datetime.strptime(stop_time, '%Y-%m-%d %H:%M:%S') if stop_time else ''

        result = ApiGetGiftsLogs(instance.id).run(
            start_time=start_time,
            stop_time=stop_time,
            server_name=server_name,
            player_name=player_name,
            prop=prop
        )

        datas = {
            "code": 2000,
            "data": result.get('logs', []),
            "isNext": False,
            "is_previous": False,
            "limit": result.get('totalCount', 0),
            "msg": "success",
            "page": 1,
            "total": result.get('totalCount', 0)
        }
        return JsonResponse(datas)

    @action(methods=['get'], detail=True, url_path='get_giftslist', url_name='get_giftslist')
    def get_giftslist(self, request, *args, **kwargs):
        instance = self.get_object()
        name = request.query_params.get('name', '')
        gift_des = request.query_params.get('giftDes', '')
        gift = request.query_params.get('gift', '')

        result = ApiGetGiftsList(instance.id).run(
            name=name,
            giftDes=gift_des,
            gift=gift
        )
        datas = {
            "code": 2000,
            "data": result.get('logs', []),
            "isNext": False,
            "is_previous": False,
            "limit": result.get('totalCount', 0),
            "msg": "success",
            "page": 1,
            "total": result.get('totalCount', 0)
        }
        return JsonResponse(datas)

    @action(methods=['get'], detail=True, url_path='del_gift', url_name='del_gift')
    def del_gift(self, request, *args, **kwargs):
        instance = self.get_object()
        gift = request.query_params.get('gift', '')
        if not gift:
            raise serializers.ValidationError('请填写gift')
        result = ApiDelGifts(instance.id).run(gift_ids=[gift])
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['post'], detail=True, url_path='add_gifts', url_name='add_gifts')
    def add_gifts(self, request, *args, **kwargs):
        instance = self.get_object()
        gift_name = request.data.get('gift_name', '')
        if not gift_name:
            raise serializers.ValidationError('请填写gift_name')
        gift_des = request.data.get('gift_des', '')
        if not gift_des:
            raise serializers.ValidationError('请填写gift_des')
        gift_content = request.data.get('gift_content', '')
        if not gift_content:
            raise serializers.ValidationError('请填写gift_content')

        result = ApiAddGifts(instance.id).run(
            gift_name=gift_name,
            gift_des=gift_des,
            gift_content=gift_content
        )
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['post'], detail=True, url_path='edit_server_name', url_name='edit_server_name')
    def edit_server_name(self, request, *args, **kwargs):
        instance = self.get_object()
        serverid = request.data.get('serverid', '')
        if not serverid:
            raise serializers.ValidationError('请填写serverid')
        newname = request.data.get('newname', '')
        if not newname:
            raise serializers.ValidationError('请填写newname')
        combined_services = request.data.get('combinedServices', None)
        if combined_services is None:
            raise serializers.ValidationError('请填写combinedServices')
        result = ApiEditServerName(instance.id).run(
            serverid=serverid,
            newname=newname,
            combinedServices=combined_services
        )
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['get'], detail=True, url_path='get_wifes_list', url_name='get_wifes_list')
    def get_wifes_list(self, request, *args, **kwargs):
        instance = self.get_object()
        server = request.query_params.get('server', '')
        if not server:
            raise serializers.ValidationError('请填写server')
        pname = request.query_params.get('pname', '')
        if not pname:
            raise serializers.ValidationError('请填写pname')
        result = ApiGetWifesList(instance.id).run(
            server=server,
            pname=pname
        )
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['post'], detail=True, url_path='del_wifes', url_name='del_wifes')
    def del_wifes(self, request, *args, **kwargs):
        instance = self.get_object()
        server = request.data.get('server', '')
        if not server:
            raise serializers.ValidationError('请填写server')
        pname = request.data.get('pname', '')
        if not pname:
            raise serializers.ValidationError('请填写pname')
        wifeid = request.data.get('wifeid', '')
        if not wifeid:
            raise serializers.ValidationError('请填写wifeid')
        result = ApiDelWifes(instance.id).run(
            server=server,
            pname=pname,
            wifeid=wifeid
        )
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['post'], detail=True, url_path='add_wifes', url_name='add_wifes')
    def add_wifes(self, request, *args, **kwargs):
        instance = self.get_object()
        server = request.data.get('server', '')
        if not server:
            raise serializers.ValidationError('请填写server')
        pname = request.data.get('pname', '')
        if not pname:
            raise serializers.ValidationError('请填写pname')
        wifeid = request.data.get('wifeid', '')
        if not wifeid:
            raise serializers.ValidationError('请填写wifeid')
        result = ApiAddWifes(instance.id).run(
            server=server,
            pname=pname,
            wifeid=wifeid
        )
        return JsonResponse({"data": result, "status": 2000})

    # edit_wifes
    @action(methods=['post'], detail=True, url_path='edit_wifes', url_name='edit_wifes')
    def edit_wifes(self, request, *args, **kwargs):
        instance = self.get_object()
        server = request.data.get('server', '')
        if not server:
            raise serializers.ValidationError('请填写server')
        pname = request.data.get('pname', '')
        if not pname:
            raise serializers.ValidationError('请填写pname')
        wifeid = request.data.get('wifeid', '')
        if not wifeid:
            raise serializers.ValidationError('请填写wifeid')
        value = request.data.get('value', '')
        if not value:
            raise serializers.ValidationError('请填写value')
        attrtype = request.data.get('attrtype', '')
        if not attrtype:
            raise serializers.ValidationError('请填写attrtype')
        result = ApiEditWifes(instance.id).run(
            server=server,
            pname=pname,
            wifeid=wifeid,
            value=value,
            attrtype=attrtype
        )
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['get'], detail=True, url_path='get_logs', url_name='get_logs')
    def get_logs(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action = request.query_params.get('log_action', '')
        if not log_action:
            raise serializers.ValidationError('请填写log_action')
        log_reason = request.query_params.get('log_reason', '')
        if not log_reason:
            raise serializers.ValidationError('请填写log_reason')
        log_server = request.query_params.get('log_server', '')
        if not log_server:
            raise serializers.ValidationError('请填写log_server')

        log_pname = request.query_params.get('log_pname', '')
        log_pid = request.query_params.get('log_pid', '')

        run_kwargs = {
            "log_action": log_action,
            "log_reason": log_reason,
            "log_server": log_server,
            "log_pname": log_pname,
            "log_pid": log_pid,
        }
        export_field_label = {
            "id": "日志ID",
            "serverid": "服务器ID",
            "time": "日志时间",
            "useid": "用户ID",
            "username": "用户名称",
            "pid": "角色ID",
            "pname": "角色名称",
            "level": "角色等级",
            "reason_id": "操作类型ID",
            "reasonname": "操作类型名称",
            "exp": "获得经验",
            "des": "描述",
        }
        async_export_data.delay(
            "ApiGetLogs",
            deepcopy(instance.id),
            deepcopy(run_kwargs),
            str(f"[{instance.game_server.gamename}] 官斗游戏日志-{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"),
            DownloadCenter.objects.create(
                creator=request.user,
                task_name=f'[{instance.game_server.gamename}]官斗日志数据导出任务',
                dept_belong_id=request.user.dept.id if request.user.dept else None,
            ).pk,
            export_field_label
        )
        return JsonResponse({"msg": "导出任务已创建，请前往‘下载中心’等待下载", "status": 2000})

    @action(methods=['get'], detail=True, url_path='get_activitylogs', url_name='get_activitylogs')
    def get_activitylogs(self, request, *args, **kwargs):
        instance = self.get_object()
        serverid = request.query_params.get('serverid', None)
        if not serverid:
            serverid = '-1'
        actid = request.query_params.get('type', None)
        if not actid:
            actid = '-1'
        qstime = request.query_params.get('qstime', None)
        if not qstime:
            qstime = '1990-01-01 00:00:00'
        qetime = request.query_params.get('qetime', None)
        if not qetime:
            qetime = '2030-12-31 23:59:59'

        result = ApiGetActivity(instance.id).run(
            serverid=serverid,
            actid=actid,
            qstime=qstime,
            qetime=qetime
        )
        datas = {
            "code": 2000,
            "data": result.get('logs', []),
            "isNext": False,
            "is_previous": False,
            "limit": result.get('totalCount', 0),
            "msg": "success",
            "page": 1,
            "total": result.get('totalCount', 0)
        }
        return JsonResponse(datas)

    @action(methods=['post'], detail=True, url_path='edit_activity', url_name='edit_activity')
    def edit_activity(self, request, *args, **kwargs):
        instance = self.get_object()
        activity_id = request.data.get('id', None)
        if not activity_id:
            raise serializers.ValidationError('请填写activityId')
        name = request.data.get('name', None)
        if not name:
            raise serializers.ValidationError('请填写name')
        des = request.data.get('des', None)
        if not des:
            raise serializers.ValidationError('请填写des')
        start_time = request.data.get('startTime', None)
        if not start_time:
            raise serializers.ValidationError('请填写startTime')
        end_time = request.data.get('endTime', None)
        if not end_time:
            raise serializers.ValidationError('请填写endTime')
        dis_time = request.data.get('disTime', None)
        if not dis_time:
            raise serializers.ValidationError('请填写disTime')
        param = request.data.get('param', None)
        if not param:
            raise serializers.ValidationError('请填写param')

        result = ApiEditActivity(instance.id).run(
            activityId=activity_id,
            name=name,
            des=des,
            startTime=start_time,
            endTime=end_time,
            disTime=dis_time,
            param=param
        )
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['post'], detail=True, url_path='delete_activity', url_name='delete_activity')
    def delete_activity(self, request, *args, **kwargs):
        instance = self.get_object()
        activity_id = request.data.get('id', None)
        if not activity_id:
            raise serializers.ValidationError('请填写activityId')
        result = ApiDelActivity(instance.id).run(
            activityId=activity_id
        )
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['get'], detail=True, url_path='get_latest_servers', url_name='get_latest_servers')
    def get_latest_servers(self, request, *args, **kwargs):
        instance = self.get_object()
        result = ApiGetLatestServers(instance.id).run()
        return JsonResponse({"data": result, "status": 2000})

    @action(methods=['post'], detail=True, url_path='upload_server_activity', url_name='upload_server_activity')
    def upload_server_activity(self, request, *args, **kwargs):
        instance: GDToken = self.get_object()
        active_config = GDActiveConfig.objects.filter(game_server=instance.game_server).first()
        if not active_config:
            raise serializers.ValidationError('该服务器未记录活动配置, 请先上传')
        upload_server = request.data.get('uploadServer')
        if not upload_server:
            raise serializers.ValidationError('请填写uploadServer')
        range_start = request.data.get('rangeStart')
        if not range_start:
            raise serializers.ValidationError('请填写rangeStart')
        range_end = request.data.get('rangeEnd')
        if not range_end:
            raise serializers.ValidationError('请填写rangeEnd')
        start_date = request.data.get('startDate')
        if not start_date:
            raise serializers.ValidationError('请填写startDate')
        upload_config = process_lists(active_config.configs, start_date)
        result = ApiUploadActivity(instance.id).run(
            servers=upload_server,
            range_start=range_start,
            range_end=range_end,
            datas=upload_config
        )
        GDActiveLog.objects.create(
            log=result['log'],
            game_name=instance.game_server.gamename,
            upload_type=0,
            status=1 if result['status'] else 0,
            creator=request.user,
            dept_belong_id=request.user.dept.id if request.user.dept else None,
            description="手动上传活动"
        )
        return JsonResponse({"data": result, "status": 2000})


class GDActiveConfigSerializer(CustomModelSerializer):
    game_server_name = serializers.SerializerMethodField()

    class Meta:
        model = GDActiveConfig
        exclude = ['configs']

    @staticmethod
    def get_game_server_name(obj):
        return obj.game_server.gamename


class GDActiveConfigViewSet(CustomModelViewSet):
    queryset = GDActiveConfig.objects.all()
    serializer_class = GDActiveConfigSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        game_server_name = self.request.query_params.get('game_server_name')
        if game_server_name:
            queryset = queryset.filter(game_server__gamename=game_server_name)
        return queryset

    @action(methods=['get'], detail=False, url_path='check_config_exist', url_name='check_config_exist')
    def check_config_exist(self, request, *args, **kwargs):
        token_id = request.query_params.get('token_id')
        if not token_id:
            raise serializers.ValidationError('请填写token_id')
        token = GDToken.objects.filter(id=token_id).first()
        if not token:
            raise serializers.ValidationError('token不存在')
        instance = GDActiveConfig.objects.filter(game_server=token.game_server).first()
        if not instance:
            return JsonResponse({"exist": False, "status": 2000})
        return JsonResponse({"exist": True, "status": 2000})

    @action(methods=['post'], detail=False, url_path='upload_config', url_name='upload_config')
    def upload_config(self, request, *args, **kwargs):
        token_id = request.data.get('token_id')
        if not token_id:
            raise serializers.ValidationError('请填写token_id')
        token = GDToken.objects.filter(id=token_id).first()
        if not token:
            raise serializers.ValidationError('token不存在')
        config = request.data.get('config')
        if not config:
            raise serializers.ValidationError('请填写config')
        try:
            config_json = json.loads(config)
        except Exception as e:
            raise serializers.ValidationError(f'config格式错误: {e}')
        instance = GDActiveConfig.objects.filter(game_server=token.game_server).first()
        if not instance:
            GDActiveConfig.objects.create(
                game_server=token.game_server,
                configs=config_json,
                creator=request.user,
                modifier=request.user.id
            )
        else:
            instance.configs = config_json
            instance.modifier = request.user.id
            instance.save()
        return JsonResponse({"msg": "上传成功", "status": 2000})


class GDLogSerializer(CustomModelSerializer):
    class Meta:
        model = GDLog
        fields = '__all__'


class GDLogViewSet(CustomModelViewSet):
    queryset = GDLog.objects.all()
    serializer_class = GDLogSerializer

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


class GDActiveLogSerializer(CustomModelSerializer):
    class Meta:
        model = GDActiveLog
        fields = '__all__'


class GDActiveLogViewSet(CustomModelViewSet):
    queryset = GDActiveLog.objects.all()
    serializer_class = GDActiveLogSerializer

    filter_fields = ['~log', '~game_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        creator_name = self.request.query_params.get('creator_name')
        if creator_name:
            queryset = queryset.filter(creator__username__contains=creator_name)
        return queryset


class GDRebateAuditSerializer(CustomModelSerializer):
    game_server_name = serializers.SerializerMethodField()
    role_info = serializers.SerializerMethodField()
    mail_info = serializers.SerializerMethodField()
    issued_time_text = serializers.SerializerMethodField()
    gift_info = serializers.SerializerMethodField()

    class Meta:
        model = GDRebateAudit
        fields = '__all__'

    @staticmethod
    def get_game_server_name(obj):
        return obj.game_server.gamename
    @staticmethod
    def get_role_info(obj):
        role = obj.pname or ''
        return f"【{obj.serverid}】{obj.pid or ''}（{role or ''}）"
    @staticmethod
    def get_mail_info(obj):
        return f"【{obj.gifts_name or ''}】{obj.des or ''}"
    @staticmethod
    def get_issued_time_text(obj):
        return obj.issued_time.strftime('%Y-%m-%d %H:%M:%S') if obj.issued_time else '-'
    @staticmethod
    def get_gift_info(obj):
        return f"【{obj.gifts_id or ''}】{obj.gifts_label or ''}"


class GDRebateAuditViewSet(CustomModelViewSet):
    queryset = GDRebateAudit.objects.all()
    serializer_class = GDRebateAuditSerializer

    filter_fields = ['~pname', '~pid', '~serverid', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        game_server_name = params.get('game_server_name')
        if game_server_name:
            queryset = queryset.filter(game_server__gamename__icontains=game_server_name)
        serverid = params.get('serverid')
        if serverid:
            queryset = queryset.filter(serverid__icontains=serverid)
        pid = params.get('pid')
        if pid:
            queryset = queryset.filter(pid__icontains=pid)
        pname = params.get('pname')
        if pname:
            queryset = queryset.filter(pname__icontains=pname)
        gifts_name = params.get('gifts_name')
        if gifts_name:
            queryset = queryset.filter(gifts_name__icontains=gifts_name)
        des = params.get('des')
        if des:
            queryset = queryset.filter(des__icontains=des)
        gift_label = params.get('gift_label')
        if gift_label:
            queryset = queryset.filter(gifts_label__icontains=gift_label)
        gifts_id = params.get('gifts_id')
        if gifts_id:
            queryset = queryset.filter(gifts_id__icontains=gifts_id)
        issued = params.get('issued')
        if issued == '1':
            queryset = queryset.filter(issued_time__isnull=False)
        if issued == '0':
            queryset = queryset.filter(issued_time__isnull=True)
        return queryset

    @action(methods=['post'], detail=True, url_path='approve', url_name='approve')
    def approve(self, request, *args, **kwargs):
        instance: GDRebateAudit = self.get_object()
        if instance.status in [2, 3]:
            raise serializers.ValidationError('当前状态不可允许发放')
        instance.status = 1
        instance.modifier = request.user.id
        instance.save()
        return JsonResponse({"msg": "已允许发放", "status": 2000})

    @action(methods=['post'], detail=True, url_path='cancel', url_name='cancel')
    def cancel(self, request, *args, **kwargs):
        instance: GDRebateAudit = self.get_object()
        if instance.status == 3:
            raise serializers.ValidationError('已发放不可取消')
        instance.status = 2
        instance.modifier = request.user.id
        instance.save()
        return JsonResponse({"msg": "已取消发放", "status": 2000})

    @action(methods=['post'], detail=True, url_path='issue', url_name='issue')
    def issue(self, request, *args, **kwargs):
        instance: GDRebateAudit = self.get_object()
        if instance.status != 1:
            raise serializers.ValidationError('仅在允许发放状态下可进行发放')
        # 执行实际发放逻辑
        token = GDToken.objects.filter(user=request.user, game_server=instance.game_server).first()
        if not token:
            raise serializers.ValidationError('未找到对应的游戏凭据，无法发放')
        result = ApiSendGifts(token.id).run(
            server=instance.serverid,
            gifts_name=instance.gifts_name or "",
            pname=instance.pid or "",
            gifts_id=instance.gifts_id or "",
            des=instance.des or ""
        )
        from django.utils import timezone
        instance.status = 3
        instance.issued_time = timezone.now()
        instance.modifier = request.user.id
        instance.save()
        return JsonResponse({"msg": "发放成功", "result": result, "status": 2000})

    @action(methods=['post'], detail=False, url_path='batch_approve', url_name='batch_approve')
    def batch_approve(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            raise serializers.ValidationError('ids格式错误')
        audits = GDRebateAudit.objects.filter(id__in=ids, status__in=[0, 1]).all()
        for item in audits:
            item.status = 1
            item.modifier = request.user.id
            item.save()
        return JsonResponse({"msg": f"批量允许发放成功，共处理{audits.count()}条", "status": 2000})

    @action(methods=['post'], detail=False, url_path='batch_cancel', url_name='batch_cancel')
    def batch_cancel(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            raise serializers.ValidationError('ids格式错误')
        audits = GDRebateAudit.objects.filter(id__in=ids).exclude(status=3).all()
        for item in audits:
            item.status = 2
            item.modifier = request.user.id
            item.save()
        return JsonResponse({"msg": f"批量取消发放成功，共处理{audits.count()}条", "status": 2000})

    @action(methods=['post'], detail=False, url_path='batch_issue', url_name='batch_issue')
    def batch_issue(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            raise serializers.ValidationError('ids格式错误')
        from django.utils import timezone
        audits = GDRebateAudit.objects.filter(id__in=ids, status=1).all()
        for item in audits:
            item.status = 3
            item.issued_time = timezone.now()
            item.modifier = request.user.id
            item.save()
        return JsonResponse({"msg": f"批量发放成功，共处理{audits.count()}条", "status": 2000})
