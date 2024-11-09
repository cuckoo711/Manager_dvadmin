"""
Creation date: 2024/5/20
Creation Time: 下午2:06
DIR PATH: backend/dvadmin/game_manage
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'game_manage', GameViewSet)
router.register(r'channel_manage', ChannelViewSet)
router.register(r'research_manage', ResearchViewSet)
router.register(r'revenue_split_manage', RevenueSplitViewSet)
router.register(r'research_split_manage', ResearchSplitViewSet)

urlpatterns = router.urls
