from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix

# Create your models here.

class CLJJServer(CoreModel):
    gamename = models.CharField(max_length=50, verbose_name='游戏名', unique=True)
    server_host = models.CharField(max_length=50, verbose_name='服务器地址')
    web_url = models.CharField(max_length=150, verbose_name='网页地址')
    is_active = models.BooleanField(verbose_name='是否激活', default=True)

    class Meta:
        db_table = table_prefix + 'cljj_server'
        verbose_name = '苍蓝境界后台服务器'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']


class CLJJLog(CoreModel):
    log = models.TextField(verbose_name='日志', help_text='日志', blank=True)

    class Meta:
        db_table = table_prefix + 'cljj_log'
        verbose_name = '苍蓝境界后台日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
