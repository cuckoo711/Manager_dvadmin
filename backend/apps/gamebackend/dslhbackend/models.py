from django.db import models

from dvadmin.system.models import Users
from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


class DSLHServer(CoreModel):
    gamename = models.CharField(max_length=50, verbose_name='游戏名', unique=True)
    server_host = models.CharField(max_length=50, verbose_name='服务器地址')
    web_url = models.CharField(max_length=150, verbose_name='网页地址')
    username = models.CharField(max_length=50, verbose_name='用户名', null=True, blank=True)
    password = models.CharField(max_length=50, verbose_name='密码', null=True, blank=True)

    class Meta:
        db_table = table_prefix + 'dslh_server'
        verbose_name = '大圣轮回后台服务器'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class DSLHConfig(CoreModel):
    server = models.ForeignKey(DSLHServer, related_name="configs", on_delete=models.CASCADE,
                               db_constraint=False, verbose_name="关联服务器", help_text="关联服务器")
    config_name = models.CharField(max_length=50, verbose_name='配置名')
    config_value = models.JSONField(verbose_name='配置值')

    class Meta:
        db_table = table_prefix + 'dslh_config'
        verbose_name = '大圣轮回后台配置'
        verbose_name_plural = verbose_name
        ordering = ['-id']
        unique_together = ('server', 'config_name')


class DSLHLog(CoreModel):
    log = models.CharField(verbose_name='日志', help_text='日志', blank=True, max_length=730)

    class Meta:
        db_table = table_prefix + 'dslh_log'
        verbose_name = '大圣轮回后台日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']


class DSLHMergeTask(CoreModel):
    TASK_STATUS = (
        (0, '未开始'),
        (1, '进行中'),
        (2, '已完成'),
        (3, '失败'),
    )

    start_id = models.IntegerField(verbose_name='起始服务器ID')
    end_id = models.IntegerField(verbose_name='结束服务器ID')
    dest_id = models.CharField(verbose_name='目标服务器ID', max_length=50)
    merge_ids = models.JSONField(verbose_name='合服服务器ID列表')
    merged_ids = models.JSONField(verbose_name='已合服服务器ID列表')
    mysql_password = models.CharField(max_length=50, verbose_name='MySQL密码')
    remote_ip = models.CharField(max_length=50, verbose_name='远程服务器IP')
    remote_password = models.CharField(max_length=50, verbose_name='远程服务器密码')
    prefix = models.CharField(max_length=50, verbose_name='数据库前缀')
    output_dir = models.CharField(max_length=220, verbose_name='输出目录')
    task_status = models.IntegerField(choices=TASK_STATUS, default=0, verbose_name='任务状态')
    logs = models.TextField(verbose_name='日志', blank=True, default='')

    class Meta:
        db_table = table_prefix + 'dslh_merge_task'
        verbose_name = '大圣轮回合服任务'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def clean(self):
        if not self.remote_password:
            self.remote_password = 'H^Fr%4NT^T*&3alo'

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def start(self):
        self.task_status = 1
        self.save()

    def finish(self):
        self.task_status = 2
        self.save()

    def fail(self):
        self.task_status = 3
        self.save()

    def add_log(self, log):
        self.logs += log.strip() + '\n'
        self.save()
