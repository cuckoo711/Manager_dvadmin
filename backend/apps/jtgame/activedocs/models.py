"""
Creation Date: 2025/2/10
Creation Time: 15:00
Dir Path: backend/apps/jtgame/activedocs
Project Name: Manager_dvadmin
File Name: models.py
Editor: buguniao
"""
from django.db import models
from django.utils import timezone

from dvadmin.utils.models import CoreModel, table_prefix
from apps.jtgame.utils import parse_iso_datetime


class ActiveDocs(CoreModel):
    # 文档标题
    title = models.CharField(max_length=100, verbose_name='文档标题')
    # 文档内容
    content = models.TextField(verbose_name='文档内容')

    class Meta:
        db_table = table_prefix + 'activedocs_content'
        verbose_name = '文档管理'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']


class ActiveDocsConfig(CoreModel):
    config_key = models.CharField(max_length=100, verbose_name='配置键')
    config_value = models.CharField(max_length=100, verbose_name='配置值')

    class Meta:
        db_table = table_prefix + 'activedocs_config'
        verbose_name = '文档配置'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']