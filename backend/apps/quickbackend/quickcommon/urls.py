"""
Creation date: 2024/10/25
Creation Time: 下午2:13
DIR PATH: backend/apps/quickbackend/quickcommon
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('QuickUser', QuickUserViewSet)

urlpatterns = router.urls
