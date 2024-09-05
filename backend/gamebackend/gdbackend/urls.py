"""
Creation date: 2024/8/26
Creation Time: 上午9:38
DIR PATH: backend/gamebackend/gdbackend
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('GDUser', GDUserViewSet)
router.register('GDServer', GDServerViewSet)
router.register('GDActiveConfig', GDActiveConfigViewSet)

urlpatterns = router.urls
