from django_celery_beat.models import IntervalSchedule
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class IntervalScheduleSerializer(ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class IntervalScheduleModelViewSet(ModelViewSet):
    """
    IntervalSchedule 调度间隔模型
    every 次数
    period 时间(天,小时,分钟,秒.毫秒)
    """
    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSerializer
    ordering = 'every'  # 默认排序
