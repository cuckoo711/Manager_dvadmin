from django.db import models
from django.utils import timezone

from apps.gamebackend.xgbackend.utils.login import update_token
from dvadmin.utils.backends import logger
from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.

class XGUser(CoreModel):
    username = models.CharField(max_length=50, verbose_name='用户名')
    password = models.CharField(max_length=50, verbose_name='密码')

    class Meta:
        db_table = table_prefix + 'xg_user'
        verbose_name = '雪糕后台用户'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']


class XGServer(CoreModel):
    gamename = models.CharField(max_length=50, verbose_name='游戏名', unique=True)
    server_host = models.CharField(max_length=50, verbose_name='服务器地址')
    server_port = models.CharField(max_length=50, verbose_name='服务器端口')
    web_url = models.CharField(max_length=150, verbose_name='网页地址')

    class Meta:
        db_table = 'xg_server'
        verbose_name = '雪糕后台服务器'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']


class XGToken(CoreModel):
    user = models.ForeignKey(XGUser, related_name="关联用户", on_delete=models.CASCADE,
                             db_constraint=False, verbose_name="关联用户", help_text="关联用户")
    game_server = models.ForeignKey(XGServer, related_name="tokens", on_delete=models.CASCADE,
                                    db_constraint=False, verbose_name="关联游戏", help_text="关联游戏")
    token = models.CharField(max_length=255, verbose_name='Token')
    last_use_time = models.DateTimeField(verbose_name='最后使用时间', auto_now=True)
    is_active = models.BooleanField(verbose_name='是否激活', default=False)

    class Meta:
        db_table = table_prefix + 'xg_token'
        verbose_name = '雪糕后台Token'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']
        unique_together = ('user', 'game_server')

    def get_token(self) -> str:
        self.last_use_time = timezone.now()
        self.save()
        return self.token

    def update_token(self) -> bool:
        try:
            token_user = XGUser.objects.get(creator=self.user)
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
