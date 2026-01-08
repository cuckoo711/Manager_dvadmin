import json
import importlib

from celery import current_app
from django_celery_beat.models import PeriodicTask, CrontabSchedule, cronexp
from django_celery_results.models import TaskResult
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.utils.json_response import SuccessResponse

from dvadmin.utils.serializers import CustomModelSerializer

from dvadmin.utils.viewset import CustomModelViewSet
from django.conf import settings

if "django_tenants" in settings.INSTALLED_APPS:
    from tenant_schemas_celery.app import CeleryApp
else:
    from celery import Celery as CeleryApp
def get_job_list():
    from application import settings
    task_list = []
    task_dict_list = []
    for app in settings.INSTALLED_APPS:
        try:
            module = importlib.import_module(f'{app}.tasks')
        except ImportError as e:
            continue
        for name, obj in vars(module).items():
            if name.startswith('__'):
                continue
            # 检查绑定任务装饰器的函数
            if callable(obj):
                _app = getattr(obj, 'app', None)
                if _app and hasattr(obj, '__wrapped__'):
                    if isinstance(_app, CeleryApp):
                        task_list.append(f'{app}.tasks.{name}')
                        task_dict_list.append({
                            "label": f'{app}.tasks.{name}',
                            "value": f'{app}.tasks.{name}'
                        })
    return {'task_list': task_list, 'task_dict_list': task_dict_list}


class CeleryCrontabScheduleSerializer(CustomModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ('timezone',)


class PeriodicTasksSerializer(CustomModelSerializer):
    kwargs = serializers.SerializerMethodField(read_only=True)
    cron = serializers.SerializerMethodField(read_only=True)

    def get_kwargs(self, instance):
        if not instance.kwargs:
            return {}
        return json.loads(instance.kwargs)

    def get_cron(self, instance: PeriodicTask):
        if not instance.crontab:
            return ""
        crontab = instance.crontab
        return '{} {} {} {} {}'.format(
            cronexp(crontab.minute), cronexp(crontab.hour),
            cronexp(crontab.day_of_month), cronexp(crontab.month_of_year),
            cronexp(crontab.day_of_week)
        )

    class Meta:
        model = PeriodicTask
        fields = '__all__'


class PeriodicTasksCreateSerializer(CustomModelSerializer):

    def save(self, **kwargs):
        cron = self.initial_data.get('cron', None)
        description = self.initial_data.get('description', None)
        cron_list = cron.split(' ')
        if description:
            crontab_schedule_obj = CrontabSchedule.objects.filter(id=description).first()
        else:
            crontab_schedule_obj = CrontabSchedule()
        crontab_schedule_obj.minute = cron_list[0]
        crontab_schedule_obj.hour = cron_list[1]
        crontab_schedule_obj.day_of_month = cron_list[2]
        crontab_schedule_obj.month_of_year = cron_list[3]
        crontab_schedule_obj.day_of_week = cron_list[4]
        crontab_schedule_obj.timezone = 'Asia/Shanghai'
        crontab_schedule_obj.save()
        try:
            self.validated_data["kwargs"] = json.loads(self.request.data.get('kwargs', {}))
        except:
            pass
        self.validated_data["crontab"] = crontab_schedule_obj
        self.validated_data["description"] = crontab_schedule_obj.id
        return super().save(**kwargs)

    class Meta:
        model = PeriodicTask
        fields = '__all__'


class CeleryTaskModelViewSet(CustomModelViewSet):
    """
    CeleryTask 添加任务调度
    """

    queryset = PeriodicTask.objects.exclude(name="celery.backend_cleanup").order_by('-id')
    serializer_class = PeriodicTasksSerializer
    create_serializer_class = PeriodicTasksCreateSerializer
    update_serializer_class = PeriodicTasksCreateSerializer
    filter_fields = ['name', 'task', 'enabled']
    extra_filter_class = []

    def job_list(self, request, *args, **kwargs):
        """获取所有任务"""
        result = get_job_list()
        task_list = result.get('task_dict_list')
        return SuccessResponse(msg='获取成功', data=task_list, total=len(task_list))

    def destroy(self, request, *args, **kwargs):
        """删除定时任务"""
        instance = self.get_object()
        TaskResult.objects.filter(periodic_task_name=instance.name).delete()
        # 删除任务 Crontab
        if instance.description:
            CrontabSchedule.objects.filter(id=instance.description).delete()
        self.perform_destroy(instance)
        return SuccessResponse(data=[], msg="删除成功")

    @action(detail=True, methods=['post'])
    def update_status(self, request, *args, **kwargs):
        """开始/暂停任务"""
        instance = self.get_object()
        body_data = request.data
        instance.enabled = body_data.get('enabled')
        instance.save()
        return SuccessResponse(msg="修改成功", data=None)

    @action(detail=True, methods=['post'])
    def run_task(self, request, *args, **kwargs):
        """执行任务"""
        instance = self.get_object()
        task_kwargs = json.loads(instance.kwargs)
        task_kwargs["periodic_task_name"] = instance.name
        return SuccessResponse(msg="运行成功", data=None)
