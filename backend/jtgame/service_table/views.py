"""
Creation date: 2024/10/10
Creation Time: 上午10:28
DIR PATH: backend/jtgame/service_table
Project Name: Manager_dvadmin
FILE NAME: views.py
Editor: 30386
"""

from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.game_manage.models import Channel
from jtgame.service_table.models import ServiceTableTemplate
from jtgame.service_table.utils import build_output_path


# Create your views here.
class ServiceTableTemplateSerializer(CustomModelSerializer):
    channel_name = serializers.SlugRelatedField(slug_field='name', source='channel', read_only=True, label='渠道名称')

    class Meta:
        model = ServiceTableTemplate
        fields = '__all__'


class ServiceTableTemplateViewSet(CustomModelViewSet):
    queryset = ServiceTableTemplate.objects.all()
    serializer_class = ServiceTableTemplateSerializer

    @action(methods=['post'], detail=False, name='上传服务表模板', url_path='uploadTemplate')
    def upload_template(self, request):
        """
        上传开服表模板
        """
        if request.user.is_anonymous:
            return JsonResponse({"error": "未登录用户无法上传文件"}, status=200)

        if request.method == 'POST':
            try:
                template_file = request.FILES.get('file')
                channel_id = request.POST.get('channel_id')
                if not channel_id:
                    return JsonResponse({"error": "未选择渠道"}, status=200)
                channel = Channel.objects.filter(id=channel_id).first()
                if not channel:
                    return JsonResponse({"error": "未找到渠道"}, status=200)
                template_fields = request.POST.get('fields')
                if not template_fields:
                    return JsonResponse({"error": "未填写字段"}, status=200)
                is_split = request.POST.get('is_split')
                if not is_split:
                    return JsonResponse({"error": "未选择是否分表"}, status=200)

                output_path = build_output_path()
                if template_file:
                    template_file_path = f"{output_path}/{template_file.name}"
                    with open(template_file_path, 'wb') as f:
                        for chunk in template_file.chunks():
                            f.write(chunk)
                    template_fields = template_fields.strip().replace(
                        ' ', '').replace('\n', '').replace('，', ',')
                    template = ServiceTableTemplate.objects.create(
                        channel=channel,
                        template_path=template_file_path,
                        template_fields=template_fields,
                        is_split=is_split,
                        is_enable=True,
                        creator=request.user
                    )

                    return JsonResponse({"message": f"上传成功, 模板ID: {template.id}"}, status=200)
                else:
                    return JsonResponse({"error": "未找到文件"}, status=200)
            except Exception as e:
                logger.error(f"上传服务表模板失败，错误信息：{str(e)}")
                return JsonResponse({"error": "上传失败"}, status=200)
        return JsonResponse({"error": "请求方式错误"}, status=200)
