from datetime import datetime

from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from apps.jtgame.game_manage.models import Games, Channel, Research, RevenueSplit, ResearchSplit
from apps.jtgame.game_manage.utils import parse_request_data, handle_game, \
    handle_scheduling


# Create your views here.


class ChannelSerializer(CustomModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'
        read_only_fields = ["id"]


class ResearchSerializer(CustomModelSerializer):
    class Meta:
        model = Research
        fields = '__all__'
        read_only_fields = ["id"]


class GameSerializer(CustomModelSerializer):
    class Meta:
        model = Games
        fields = '__all__'
        read_only_fields = ["id"]


class RevenueSplitSerializer(CustomModelSerializer):
    game_name = serializers.SlugRelatedField(slug_field='name', source='game', read_only=True, label='游戏名称')
    game_release_date = serializers.SlugRelatedField(slug_field='release_date', source='game', read_only=True, label='发行日期')
    channel_name = serializers.SlugRelatedField(slug_field='name', source='channel', read_only=True, label='渠道名称')

    class Meta:
        model = RevenueSplit
        fields = '__all__'
        read_only_fields = ["id"]


class RevenueSplitExoprtSerializer(CustomModelSerializer):
    game_name = serializers.SlugRelatedField(slug_field='name', source='game', read_only=True, label='游戏名称')
    game_release_date = serializers.SlugRelatedField(slug_field='release_date', source='game', read_only=True, label='发行日期')
    channel_name = serializers.SlugRelatedField(slug_field='name', source='channel', read_only=True, label='渠道名称')
    
    class Meta:
        model = RevenueSplit
        fields = '__all__'


class ResearchSplitSerializer(CustomModelSerializer):
    game_name = serializers.SlugRelatedField(slug_field='name', source='game', read_only=True, label='游戏名称')
    game_release_date = serializers.SlugRelatedField(slug_field='release_date', source='game', read_only=True, label='发行日期')
    research_name = serializers.SlugRelatedField(slug_field='name', source='research', read_only=True, label='研发名称')

    class Meta:
        model = ResearchSplit
        fields = '__all__'
        read_only_fields = ["id"]


class ResearchSplitExoprtSerializer(CustomModelSerializer):
    game_name = serializers.SlugRelatedField(slug_field='name', source='game', read_only=True, label='游戏名称')
    game_release_date = serializers.SlugRelatedField(slug_field='release_date', source='game', read_only=True, label='发行日期')
    research_name = serializers.SlugRelatedField(slug_field='name', source='research', read_only=True, label='研发名称')

    class Meta:
        model = ResearchSplit
        fields = '__all__'


class GameViewSet(CustomModelViewSet):
    queryset = Games.objects.all()
    serializer_class = GameSerializer

    @action(detail=False, methods=['post'])
    def upload_dddd(self, request, *args, **kwargs):
        data = parse_request_data(request)
        sheets = data.get('sheets', [])
        coverList = data.get('coverList', [])
        messages = {'info': [
            '覆盖列表: ' + ', '.join(coverList) if coverList else '无覆盖列表',
            'sheet页数量: ' + str(len(sheets))
        ], 'update': [], 'error': []}

        remove_sheets = []
        for index, sheet in enumerate(sheets):
            # logger.info(f'处理sheet页: {sheet.get("sheet_name")}')
            if handle_game(sheet, messages, coverList):
                remove_sheets.append(index)
        sheets = [sheet for index, sheet in enumerate(sheets) if index not in remove_sheets]
        remove_sheets.clear()
        for index, sheet in enumerate(sheets):
            if handle_scheduling(sheet, messages, coverList):
                remove_sheets.append(index)
        sheets = [sheet for index, sheet in enumerate(sheets) if index not in remove_sheets]

        logger.info(f'上传共{len(sheets)}个sheet页')
        if not sheets:
            logger.info('所有sheet页处理完成')
        else:
            logger.error(f'有{len(sheets)}个sheet页未处理: {sheets}')

        datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        messages_str = f'上传对接表 - {datetime_now}\n'
        messages_str += '信息:\n' + '\n'.join(messages['info']) + '\n'
        messages_str += '更新:\n' + '\n'.join(messages['update']) + '\n'
        messages_str += '错误:\n' + '\n'.join(messages['error']) + '\n'

        return JsonResponse({'message': messages_str, 'data': 'success'})


class ChannelViewSet(CustomModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


class ResearchViewSet(CustomModelViewSet):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer


class RevenueSplitViewSet(CustomModelViewSet):
    queryset = RevenueSplit.objects.all()
    serializer_class = RevenueSplitSerializer

    def get_queryset(self):
        if getattr(self, 'values_queryset', None):
            return self.values_queryset
        elif self.action == 'export_data':
            self.queryset = RevenueSplit.objects.all().select_related(*self.export_foreignKey__value_column)
        return super().get_queryset()

    export_field_label = {
        'game_name': '游戏名称',
        'game_release_date': '发行日期',
        'channel_name': '渠道名称',
        'our_ratio': '我方分成比例',
        'channel_ratio': '渠道分成比例',
        'channel_fee_ratio': '渠道费比例',
        'channel_tips': '分成备注',
    }
    export_foreignKey__value_column = ('game', 'channel')
    export_serializer_class = RevenueSplitExoprtSerializer


class ResearchSplitViewSet(CustomModelViewSet):
    queryset = ResearchSplit.objects.all()
    serializer_class = ResearchSplitSerializer

    def get_queryset(self):
        if getattr(self, 'values_queryset', None):
            return self.values_queryset
        elif self.action == 'export_data':
            self.queryset = ResearchSplit.objects.all().select_related(*self.export_foreignKey__value_column)
        return super().get_queryset()

    export_field_label = {
        'game_name': '游戏名称',
        'game_release_date': '发行日期',
        'research_name': '研发名称',
        'research_ratio': '研发分成比例',
        'research_fee_ratio': '研发费比例',
        'research_tips': '分成备注',
    }
    export_foreignKey__value_column = ('game', 'research')
