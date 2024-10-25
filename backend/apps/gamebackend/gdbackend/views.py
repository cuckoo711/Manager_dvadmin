from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from apps.gamebackend.gdbackend.models import GDUser, GDServer, GDActiveConfig


# Create your views here.

class GDUserSerializer(CustomModelSerializer):
    class Meta:
        model = GDUser
        fields = '__all__'
        read_only_fields = ["id"]


class GDUserViewSet(CustomModelViewSet):
    queryset = GDUser.objects.all()
    serializer_class = GDUserSerializer


class GDServerSerializer(CustomModelSerializer):
    class Meta:
        model = GDServer
        fields = '__all__'
        read_only_fields = ["id"]


class GDServerViewSet(CustomModelViewSet):
    queryset = GDServer.objects.all()
    serializer_class = GDServerSerializer


class GDActiveConfigSerializer(CustomModelSerializer):
    class Meta:
        model = GDActiveConfig
        fields = '__all__'
        read_only_fields = ["id"]


class GDActiveConfigViewSet(CustomModelViewSet):
    queryset = GDActiveConfig.objects.all()
    serializer_class = GDActiveConfigSerializer


class GDBackSerializer(CustomModelSerializer):
    class Meta:
        model = GDUser
        fields = '__all__'
        read_only_fields = ["id"]


class GDBackViewSet(CustomModelViewSet):
    queryset = GDUser.objects.all()
    serializer_class = GDBackSerializer
