from django.db import models

from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


class GameNoticeConfig(CoreModel):
    TYPE_LIST = (
        (0, "text"),
        (1, "number"),
        (2, "date"),
        (6, "boolean"),
    )
    key = models.CharField(max_length=50, verbose_name='配置键', unique=True)
    value = models.TextField(verbose_name='配置值')
    type = models.IntegerField(choices=TYPE_LIST, default=0, verbose_name="数据值类型", help_text="数据值类型")

    def __str__(self):
        return self.key

    class Meta:
        db_table = table_prefix + 'gamenotice_config'
        verbose_name = '公告配置'
        verbose_name_plural = verbose_name
        ordering = ['key']


class GameNoticeFile(CoreModel):
    STATUS_CHOICES = (
        (0, '未生成'),
        (1, '已生成'),
        (2, '正在生成'),
        (3, '生成失败'),
        (4, '发送失败')
    )

    release_date = models.DateField(verbose_name='下架/关服日期')
    game_names = models.ManyToManyField('game_manage.Games', verbose_name='游戏名称')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='状态')
    tips = models.TextField(verbose_name='备注', null=True, blank=True)
    gamenotice_filepath = models.CharField(max_length=255, verbose_name='公告文件路径', null=True, blank=True)

    class Meta:
        db_table = table_prefix + 'gamenotice_file'
        verbose_name = '公告文件'
        verbose_name_plural = verbose_name
        ordering = ['-release_date']

    def __str__(self):
        return self.release_date.strftime('%Y-%m-%d')

    def game_names_display(self):
        return '、'.join([game.name for game in self.game_names.all()])

    def game_names_list(self):
        return [game.name for game in self.game_names.all()]
