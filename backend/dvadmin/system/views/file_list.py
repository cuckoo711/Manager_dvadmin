import hashlib

from rest_framework import serializers

from application import dispatch
from dvadmin.system.models import FileList
from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class FileSerializer(CustomModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, instance):
        # base_url = f"{self.request.scheme}://{self.request.get_host()}/"
        base_url = dispatch.get_system_config_values(
            "base.base_url") or f"{self.request.scheme}://{self.request.get_host()}/"
        # print(f"base_url: {base_url}\n"
        #       f"instance.url: {instance.url}\n"
        #       f"instance.file_url: {instance.file_url}")
        if str(instance.url).startswith('http'):
            return instance.url
        return base_url + (instance.file_url or f'media/{str(instance.url)}')

    class Meta:
        model = FileList
        fields = "__all__"

    def create(self, validated_data):
        file_engine = dispatch.get_system_config_values("fileStorageConfig.file_engine") or 'local'
        file_backup = dispatch.get_system_config_values("fileStorageConfig.file_backup")
        file = self.initial_data.get('file')
        file_size = file.size
        validated_data['name'] = str(file)
        validated_data['size'] = file_size
        md5 = hashlib.md5()
        for chunk in file.chunks():
            md5.update(chunk)
        validated_data['md5sum'] = md5.hexdigest()
        validated_data['engine'] = file_engine
        validated_data['mime_type'] = file.content_type
        if file_backup:
            validated_data['url'] = file
        # 审计字段
        try:
            request_user = self.request.user
            validated_data['dept_belong_id'] = request_user.dept.id
            validated_data['creator'] = request_user.id
            validated_data['modifier'] = request_user.id
        except Exception as e:
            logger.error(f"创建文件审计字段异常: {e}")
        return super().create(validated_data)


class FileViewSet(CustomModelViewSet):
    """
    文件管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = FileList.objects.all()
    serializer_class = FileSerializer
    filter_fields = ['name', ]
    permission_classes = []
