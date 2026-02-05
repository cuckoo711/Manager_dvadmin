from rest_framework.routers import DefaultRouter

from .views import CLJJServerViewSet, CLJJLogViewSet

router = DefaultRouter()
router.register('CLJJServer', CLJJServerViewSet)
router.register('CLJJLog', CLJJLogViewSet)

urlpatterns = router.urls
