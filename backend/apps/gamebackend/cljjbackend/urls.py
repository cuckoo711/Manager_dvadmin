from rest_framework.routers import DefaultRouter

from .views import CLJJServerViewSet, CLJJLogViewSet, MetroViewSet

router = DefaultRouter()
router.register('CLJJServer', CLJJServerViewSet)
router.register('CLJJLog', CLJJLogViewSet)
router.register('cljj/metro', MetroViewSet, basename='cljj-metro')

urlpatterns = router.urls
