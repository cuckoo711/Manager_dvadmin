from django_celery_beat.models import IntervalSchedule
from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class IntervalScheduleSerializer(CustomModelSerializer):
    described = serializers.SerializerMethodField(read_only=True)

    def get_described(self, instance):
        period_dict = {
            'days': '天',
            'hours': '小时',
            'minutes': '分钟',
            'seconds': '秒',
            'microseconds': '毫秒'
        }

        return f'每 {instance.every} {period_dict[instance.period]}执行一次'

    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class IntervalScheduleModelViewSet(CustomModelViewSet):
    """
    IntervalSchedule 调度间隔模型  间隔性时间定时器
    every 次数
    period 时间(天,小时,分钟,秒.毫秒)
    """
    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSerializer
    ordering = 'every'  # 默认排序
