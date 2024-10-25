from django.http import JsonResponse
from rest_framework.decorators import action

from apps.quickbackend.quickcommon.models import QuickUser
from apps.quickbackend.quickcommon.utils.quickapi import QuickLogin
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
        instance = self.get_object()
        instance.update_cookie()
        return JsonResponse({'status': True, 'message': '更新成功!'})

    @action(methods=['get'], detail=False, url_path='GetUser', name='获取用户')
    def get_user(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!'})
        return JsonResponse({'status': True, 'username': user.username})

    @action(methods=['get'], detail=False, url_path='GetGameList', name='获取游戏列表')
    def get_game_list(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!', 'data': {}})
        quick_sdk = QuickLogin()
        quick_sdk.load_cookie(user.cookie)
        data = quick_sdk.load_game_data()
        return JsonResponse({'status': True, 'data': data})

    @action(methods=['Post'], detail=False, url_path='SwitchGame', name='切换游戏')
    def switch_game(self, request):
        user: QuickUser = self.queryset.filter(creator=request.user, status='0').first()
        if not user:
            return JsonResponse({'status': False, 'message': '用户不存在或无有效用户!', 'data': {}})
        game_id = request.data.get('game_id', None)
        if not game_id:
            return JsonResponse({'status': False, 'message': '游戏ID不能为空!'})
        quick_sdk = QuickLogin()
        quick_sdk.load_cookie(user.cookie)
        switch_data = quick_sdk.switch_game(game_id)
        if not switch_data:
            return JsonResponse({'status': False, 'message': '切换游戏失败!'})
        channel_data = quick_sdk.get_channel_list(game_id)
        return JsonResponse({'status': True, 'data': channel_data})

