from rest_framework.routers import DefaultRouter
from .views import MetroViewSet

router = DefaultRouter()
router.register(r'canglan/metro', MetroViewSet, basename='canglan-metro')

urlpatterns = router.urls
