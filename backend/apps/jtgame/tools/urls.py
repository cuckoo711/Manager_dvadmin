"""
Creation Date: 2025/2/27
Creation Time: 下午9:23
Dir Path: backend/apps/jtgame/tools
Project Name: Manager_dvadmin_my
File Name: urls.py
Editor: cuckoo
"""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'tools', views.ToolsSet, basename='tools')

urlpatterns = router.urls
