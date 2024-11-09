"""
Creation date: 2024/7/24
Creation Time: 下午2:41
DIR PATH: backend/jtgame/tencent_docx
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'ServiceTableChannel', ServiceTableChannelViewSet)
router.register(r'ServiceTableMap', ServiceTableMapViewSet)
router.register(r'ServiceTableTemplate', ServiceTableTemplateViewSet)
router.register(r'ServiceTableNormal', ServiceTableNormalViewSet)
router.register(r'ServiceTableSplit', ServiceTableSplitViewSet)

urlpatterns = router.urls
