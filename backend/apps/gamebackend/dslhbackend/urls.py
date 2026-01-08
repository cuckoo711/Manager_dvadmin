"""
Creation date: 2024/12/26
Creation Time: 上午10:06
DIR PATH: backend/apps/gamebackend/dslhbackend
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('DSLHServer', DSLHServerViewSet)
router.register('DSLHConfig', DSLHConfigViewSet)
router.register('DSLHLog', DSLHLogViewSet)
router.register('DSLHMergeTask', DSLHMergeTaskViewSet)

urlpatterns = router.urls
