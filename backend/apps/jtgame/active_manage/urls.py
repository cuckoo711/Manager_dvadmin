"""
Creation Date: 2025/2/27
Creation Time: 上午5:07
Dir Path: backend/apps/jtgame/active_manage/
Project Name: Manager_dvadmin_my
File Name: urls.py
Editor: cuckoo
"""
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'activity_game', views.ActivityGameSet)
router.register(r'activity_content', views.ActivityContentSet)
urlpatterns = router.urls
