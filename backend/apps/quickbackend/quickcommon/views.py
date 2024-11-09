from django.http import JsonResponse
from rest_framework.decorators import action

from apps.jtgame.game_manage.utils import get_channel_suffix
from apps.quickbackend.quickcommon.models import QuickUser
from apps.quickbackend.quickcommon.utils.quickapi import QuickLogin
from apps.quickbackend.quickcommon.utils.utils import mix_channel_status, replace_game_data
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


# Create your views here.


class QuickUserSerializer(CustomModelSerializer):
    class Meta:
        model = QuickUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'cookie': {'write_only': True},
        }


class QuickUserViewSet(CustomModelViewSet):
    queryset = QuickUser.objects.all()
    serializer_class = QuickUserSerializer

    def get_object(self) -> QuickUser:
        filter_kwargs = {'id': self.kwargs['pk']}
        obj = self.queryset.filter(**filter_kwargs).first()
        return obj

    @action(methods=['get'], detail=True, url_path='UpdateCookie', name='更新cookie')
    def update_cookie(self, request, pk=None):
        account = self.get_object()
        account.update_cookie(force=True)
        return JsonResponse({'status': True, 'message': '更新成功!', 'code': 2000})

    @action(methods=['get'], detail=False, url_path='GetUser', name='获取用户')
    def get_user(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!', 'code': 2000})
        return JsonResponse({'status': True, 'username': user.username, 'code': 2000})

    @action(methods=['get'], detail=False, url_path='GetGameList', name='获取游戏列表')
    def get_game_list(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!', 'data': {}, 'code': 2000})
        quick_sdk = QuickLogin()
        quick_sdk.load_cookie(user.cookie)
        data = quick_sdk.load_game_data()
        if not data:
            return JsonResponse({'status': False, 'message': '获取游戏列表失败!', 'data': {}, 'code': 2000})
        replace_data = replace_game_data(data)
        return JsonResponse({'status': True, 'data': replace_data, 'code': 2000})

    @action(methods=['get'], detail=False, url_path='GetChannelSuffix', name='获取渠道后缀')
    def get_channel_suffix(self, request):
        return JsonResponse({'status': True, 'data': get_channel_suffix(), 'code': 2000})

    @action(methods=['Post'], detail=False, url_path='SwitchGame', name='切换游戏')
    def switch_game(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!', 'data': {}, 'code': 2000})
        game_id = request.data.get('game_id', None)
        if not game_id:
            return JsonResponse({'status': False, 'message': '游戏ID不能为空!', 'code': 2000})
        channel_suffix = request.data.get('channel_suffix', None)
        if not channel_suffix:
            channel_suffixs = ['全部']
        else:
            channel_suffixs = [channel_suffix]
        quick_sdk = QuickLogin()
        quick_sdk.load_cookie(user.cookie)
        switch_data = quick_sdk.switch_game(game_id)
        if not switch_data:
            return JsonResponse({'status': False, 'message': '切换游戏失败!', 'code': 2000})
        if channel_suffix == '无后缀':
            channel_suffixs += get_channel_suffix()
        channel_data = quick_sdk.get_channel_list(game_id, channel_suffixs)
        return JsonResponse({'status': True, 'data': channel_data, 'code': 2000})

    #     update_channel_status
    @action(methods=['Post'], detail=False, url_path='UpdateChannelStatus', name='更新渠道状态')
    def update_channel_status(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!', 'data': {}, 'code': 2000})

        batch_switch_type = request.data.get('batch_switch_type', None)
        if not batch_switch_type:
            return JsonResponse({'status': False, 'message': '批量切换类型不能为空!', 'code': 2000})

        game_id = request.data.get('game_id', None)
        if not game_id:
            return JsonResponse({'status': False, 'message': '游戏ID不能为空!', 'code': 2000})

        multiple_selection = request.data.get('multiple_selection', None)
        if not multiple_selection:
            return JsonResponse({'status': False, 'message': '多选数据不能为空!', 'code': 2000})

        quick_sdk = QuickLogin()
        quick_sdk.load_cookie(user.cookie)
        switch_data = quick_sdk.switch_game(game_id)
        if not switch_data:
            return JsonResponse({'status': False, 'message': '切换游戏失败!', 'code': 2000})
        channel_data = quick_sdk.get_channel_list(game_id)

        update_channel_status = mix_channel_status(channel_data, multiple_selection, batch_switch_type)
        if not update_channel_status:
            return JsonResponse({'status': False, 'message': '合并状态失败!', 'code': 2000})

        update_result = quick_sdk.update_channel_status(game_id, update_channel_status)
        if not update_result:
            return JsonResponse({'status': False, 'message': '更新状态失败!', 'code': 2000})
        return JsonResponse({
            'status': True, 'message': '更新状态成功!', 'code': 2000
        })

    @action(methods=['Post'], detail=False, url_path='GetPlayerDataByAny', name='获取玩家数据')
    def get_player_data_by_any(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!', 'data': {}, 'code': 2000})
        game_id = request.data.get('game_id', None)
        if not game_id:
            return JsonResponse({'status': False, 'message': '游戏ID不能为空!', 'code': 2000})
        check_view = request.data.get('check_view', None)
        if not check_view:
            return JsonResponse({'status': False, 'message': '查看视图不能为空!', 'code': 2000})
        check_txt = request.data.get('check_txt', '')

        quick_sdk = QuickLogin()
        quick_sdk.load_cookie(user.cookie)
        switch_data = quick_sdk.switch_game(game_id)
        if not switch_data:
            return JsonResponse({'status': False, 'message': '切换游戏失败!', 'code': 2000})

        player_data = quick_sdk.get_player_data_by_any(check_view, check_txt)
        if isinstance(player_data, str):
            return JsonResponse({'status': False, 'message': player_data, 'code': 2000})
        else:
            player_data_full, player_data_mix = player_data
        return JsonResponse({
            'status': True, 'data': player_data_full, 'mix_data': player_data_mix, 'code': 2000
        })
