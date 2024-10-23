import hashlib

from django.db import models

from dvadmin.system.models import Users
from dvadmin.utils.models import CoreModel, table_prefix
from jtgame.game_manage.models import Games


# Create your models here.


class GDUser(CoreModel):
    # 所属用户
    users = models.ForeignKey(Users, related_name="gd_user_related", on_delete=models.CASCADE, db_constraint=False,
                              verbose_name="关联用户表", help_text="关联用户表")
    # 用户名
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    # 密码
    password = models.CharField(max_length=50, verbose_name='密码')
    # token
    token = models.CharField(max_length=50, verbose_name='token')

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
    game = models.CharField(max_length=50, verbose_name='游戏名')
    game_foreign = models.ForeignKey(Games, related_name="关联游戏", on_delete=models.CASCADE,
                                     db_constraint=False, verbose_name="关联游戏",
                                     help_text="关联游戏", null=True)
    server_host = models.CharField(max_length=50, verbose_name='服务器地址')
    server_port = models.CharField(max_length=50, verbose_name='服务器端口')
    web_url = models.CharField(max_length=150, verbose_name='网页地址')

    class Meta:
        db_table = table_prefix + 'gd_server'
        verbose_name = '官斗后台服务器'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']


class GDActiveConfig(CoreModel):
    game = models.ForeignKey(GDServer, related_name="关联游戏", on_delete=models.CASCADE,
                             db_constraint=False, verbose_name="关联游戏", help_text="关联游戏")
    configs = models.JSONField(verbose_name='活动配置', help_text='活动配置', default=dict)

    class Meta:
        db_table = table_prefix + 'gd_active_config'
        verbose_name = '官斗后台活动配置'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']