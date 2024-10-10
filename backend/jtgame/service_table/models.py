import hashlib
import os

import pandas
from django.db import models

from dvadmin.utils.models import CoreModel, table_prefix
from jtgame.game_manage.models import Channel


# Create your models here.


# 开服表模板
class ServiceTableTemplate(CoreModel):
    IS_SPLIT = (
        ('2', '否'),
        ('1', '是'),
    )
    IS_ENABLE = (
        ('0', '否'),
        ('1', '是'),
    )
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, verbose_name='所属渠道')
    template_path = models.CharField(max_length=255, verbose_name='模板路径', null=True)
    template_fields = models.TextField(verbose_name='模板字段')
    is_split = models.CharField(max_length=1, choices=IS_SPLIT, verbose_name='是否分表', default='0')
    is_enable = models.CharField(max_length=1, choices=IS_ENABLE, verbose_name='是否启用', default='1')

    class Meta:
        db_table = table_prefix + 'service_table_template'
        verbose_name = '开服表模板'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def clean(self):
        self.check_template_fields()

    def __str__(self):
        return self.channel.name + '模板:' + self.template_path

    def check_template_fields(self):
        self.template_fields = self.template_fields.strip().replace(
            ' ', '').replace('\n', '').replace('，', ',')

    # 删除条目时删除文件
    def delete(self, *args, **kwargs):
        if os.path.exists(self.template_path):
            os.remove(self.template_path)
        super().delete(*args, **kwargs)
