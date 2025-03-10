from django.http import JsonResponse
from rest_framework import serializers, viewsets
from rest_framework.decorators import action

from apps.jtgame.active_manage.models import ActivityGame, ActivityContent


class ActivityGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityGame
        fields = '__all__'


class ActivityContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityContent
        fields = '__all__'


class ActivityGameSet(viewsets.ModelViewSet):
    queryset = ActivityGame.objects.all()
    serializer_class = ActivityGameSerializer
    permission_classes = []

    @action(detail=False, methods=['get'])
    def get_all_activities_game_names(self, request):
        games = ActivityGame.objects.all().values_list('game_name', flat=True)
        return JsonResponse({"game_names": list(games)})


class ActivityContentSet(viewsets.ModelViewSet):
    queryset = ActivityContent.objects.all()
    serializer_class = ActivityContentSerializer
    permission_classes = []

    @action(detail=False, methods=['post'])
    def get_activities_by_game_name(self, request):
        game_name = request.data.get('game_name', '').strip()
        activity_name = request.data.get('activity_name', '').strip()
        keyword = request.data.get('keyword', '').strip()

        queryset = self.queryset
        if game_name:
            queryset = self.queryset.filter(game_name__icontains=game_name)
        if activity_name:
            queryset = queryset.filter(activity_name__icontains=activity_name)
        if keyword:
            queryset = queryset.filter(activity_value__icontains=keyword)
        activity_list = [{
            'id': activity['id'],
            'activity_name': activity['activity_name'],
            'game_name': activity['game_name']
        }
            for activity in queryset.values('id', 'activity_name', 'game_name')]
        return JsonResponse({"activities": activity_list})

    @action(detail=False, methods=['post'])
    def get_activity_content(self, request):
        activity_id = request.data.get('activity_id')
        if activity_id:
            try:
                activity = self.queryset.get(id=activity_id)
                return JsonResponse({
                    "activity_name": activity.activity_name,
                    "game_name": activity.game_name,
                    "activity_value": activity.activity_value
                })
            except ActivityContent.DoesNotExist:
                return JsonResponse({"error": "未找到活动"}, status=404)
        return JsonResponse({"error": "活动ID是必需的"}, status=400)
