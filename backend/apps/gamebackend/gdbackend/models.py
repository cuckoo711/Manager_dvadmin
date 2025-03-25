import hashlib

from django.db import models
from django.utils import timezone

from apps.gamebackend.gdbackend.utils.login import update_token
from dvadmin.system.models import Users
from dvadmin.utils.backends import logger
from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


class GDUser(CoreModel):
    username = models.CharField(max_length=50, verbose_name='用户名')
    password = models.CharField(max_length=50, verbose_name='密码')

    class Meta:
        db_table = table_prefix + 'gd_user'
        verbose_name = '官斗后台用户'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']

    def save(self, *args, **kwargs):
        if self.password and any([i.islower() for i in self.password]):
            self.password = hashlib.new('md5', self.password.encode()).hexdigest().upper()
        super().save(*args, **kwargs)


class GDServer(CoreModel):
    gamename = models.CharField(max_length=50, verbose_name='游戏名', unique=True)
    server_host = models.CharField(max_length=50, verbose_name='服务器地址')
    server_port = models.CharField(max_length=50, verbose_name='服务器端口')
    web_url = models.CharField(max_length=150, verbose_name='网页地址')
    is_active = models.BooleanField(verbose_name='是否激活', default=True)
    sql_pwd = models.CharField(max_length=50, verbose_name='数据库密码', blank=True)

    class Meta:
        db_table = table_prefix + 'gd_server'
        verbose_name = '官斗后台服务器'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']


class GDToken(CoreModel):
    user = models.ForeignKey(Users, related_name="关联用户", on_delete=models.CASCADE,
                             db_constraint=False, verbose_name="关联用户", help_text="关联用户")
    game_server = models.ForeignKey(GDServer, related_name="tokens", on_delete=models.CASCADE,
                                    db_constraint=False, verbose_name="关联游戏", help_text="关联游戏")
    token = models.CharField(max_length=255, verbose_name='Token')
    last_use_time = models.DateTimeField(verbose_name='最后使用时间', default=timezone.now)
    is_active = models.BooleanField(verbose_name='是否激活', default=False)

    class Meta:
        db_table = table_prefix + 'gd_token'
        verbose_name = '官斗后台Token'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']
        unique_together = ('user', 'game_server')

    def get_token(self) -> str:
        self.last_use_time = timezone.now()
        self.save()
        return self.token

    def update_token(self) -> bool:
        try:
            token_user = GDUser.objects.get(creator=self.user)
            self.token = update_token(self.game_server.server_host, token_user.username, token_user.password)
            logger.debug(f"更新token成功:{self.token}")
            self.last_use_time = timezone.now()
            self.is_active = True
            self.save()
            return True
        except Exception as e:
            logger.error(f"更新token失败:{e}")
            self.token = ""
            self.is_active = False
            self.save()
            return False


class GDActiveConfig(CoreModel):
    game_server = models.OneToOneField(GDServer, related_name="active_configs", on_delete=models.CASCADE,
                                       db_constraint=False, verbose_name="关联游戏", help_text="关联游戏")
    configs = models.JSONField(verbose_name='活动配置', help_text='活动配置', default=dict)

    class Meta:
        db_table = table_prefix + 'gd_active_config'
        verbose_name = '官斗后台活动配置'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']


class GDLog(CoreModel):
    log = models.TextField(verbose_name='日志', help_text='日志', blank=True)

    class Meta:
        db_table = table_prefix + 'gd_log'
        verbose_name = '官斗后台日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']


class GDActiveLog(CoreModel):
    UPLOAD_TYPE = (
        (0, '手动'),
        (1, '自动'),
    )
    STATUS = (
        (0, '失败'),
        (1, '成功'),
    )

    log = models.TextField(verbose_name='日志', help_text='日志')
    game_name = models.CharField(max_length=50, verbose_name='游戏名', help_text='游戏名')
    upload_type = models.IntegerField(choices=UPLOAD_TYPE, verbose_name='上传类型', help_text='上传类型', default=0)
    status = models.IntegerField(choices=STATUS, verbose_name='状态', help_text='状态', default=0)

    class Meta:
        db_table = table_prefix + 'gd_active_log'
        verbose_name = '官斗后台活动日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
