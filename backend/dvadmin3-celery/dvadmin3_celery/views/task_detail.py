import ast
import json

from django_celery_results.models import TaskResult
import django_filters
from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class CeleryTaskDetailSerializer(CustomModelSerializer):
    """定时任务详情 序列化器"""
    name = serializers.SerializerMethodField(read_only=True)
    task_kwargs = serializers.SerializerMethodField(read_only=True)
    result = serializers.SerializerMethodField(read_only=True)

    def get_name(self, instance):
        return instance.task_name

    def get_task_kwargs(self, instance):
        task_kwargs = instance.task_kwargs
        if task_kwargs:
            try:
                task_kwargs = json.loads(json.loads(task_kwargs).replace("'", '"'))
            except Exception as e:
                pass
        return task_kwargs
    def get_result(self, instance):
        result = instance.result
        if result:
            try:
                result = json.loads(result)
            except Exception as e:
                pass
        return result

    class Meta:
        model = TaskResult
        fields = '__all__'


class CeleryTaskDetailViewSet(CustomModelViewSet):
    """
    定时任务详情
    """
    queryset = TaskResult.objects.all()
    serializer_class = CeleryTaskDetailSerializer
