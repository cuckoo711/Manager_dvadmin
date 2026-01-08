# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework import routers

from .views.crontab_schedule import CrontabScheduleModelViewSet
from .views.interval_schedule import IntervalScheduleModelViewSet
from .views.periodic_task import PeriodicTaskModelViewSet
from .views.task import CeleryTaskModelViewSet
from .views.task_detail import CeleryTaskDetailViewSet

router = routers.SimpleRouter()
# 调度间隔
router.register('intervalschedule', IntervalScheduleModelViewSet)
router.register('crontabschedule', CrontabScheduleModelViewSet)
router.register('periodictask', PeriodicTaskModelViewSet, basename='periodictasks')
router.register('task', CeleryTaskModelViewSet)
urlpatterns = [
    path('tasks_as_choices/', PeriodicTaskModelViewSet.as_view({'get': 'tasks_as_choices'})),
    path('operate_celery/', PeriodicTaskModelViewSet.as_view({'post': 'operate_celery'})),

    path('task/job_list/',CeleryTaskModelViewSet.as_view({'get':'job_list'})),
    path('task/update_status/<str:pk>/',CeleryTaskModelViewSet.as_view({'post':'update_status'})),
    path('task/<str:pk>/delete_task/',CeleryTaskModelViewSet.as_view({'delete':'destroy'})),  #注释编号: django-vue3-admin-urls202416:添加删除定时任务的URL
    
    path('task_detail/',CeleryTaskDetailViewSet.as_view({'get':'list'})),
]
urlpatterns += router.urls
