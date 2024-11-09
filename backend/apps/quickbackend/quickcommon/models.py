from datetime import datetime, timedelta

from django.db import models

from apps.quickbackend.quickcommon.utils.quickapi import QuickLogin
from dvadmin.system.models import Users
from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


class QuickUser(CoreModel):
    ACCOUNT_STATUS = (
        ('0', '正常'),
        ('1', '失效'),
    )
    # 用户名
    username = models.CharField(max_length=50, verbose_name='用户名')
    # 密码
    password = models.CharField(max_length=50, verbose_name='密码')
    # cookie
    cookie = models.CharField(max_length=512, verbose_name='cookie', null=True)
    # 过期时间
    expire_time = models.DateTimeField(verbose_name='过期时间', null=True)
    # 用户状态
    status = models.CharField(max_length=1, choices=ACCOUNT_STATUS, verbose_name='状态', default='1')

    class Meta:
        db_table = table_prefix + 'quick_user'
        verbose_name = 'Quick后台用户'
        verbose_name_plural = verbose_name
        ordering = ('-update_datetime',)

    # 创建时更新cookie
    def save(self, *args, **kwargs):
        if not self.id:
            cookie, expires_time = QuickLogin().get_cookie(self.username, self.password)
            if cookie and expires_time:
                self.cookie = cookie
                self.expire_time = expires_time
                self.status = '0'
            else:
                self.status = '1'
        super(QuickUser, self).save(*args, **kwargs)

    def check_cookie(self):
        """
        检查cookie是否过期
        :return: True: 未过期 False: 已过期
        """
        if not self.expire_time or self.expire_time.replace(tzinfo=None) < datetime.now() + timedelta(hours=1):
            return False
        return True

    def update_cookie(self, force=False):
        """
        更新cookie
        :return: True: 更新成功 False: 更新失败 None: 无需更新
        """
        if self.check_cookie() or force:
            cookie, expires_time = QuickLogin().get_cookie(self.username, self.password)
            if cookie and expires_time:
                self.cookie = cookie
                self.expire_time = expires_time
                self.status = '0'
                self.save()
                return True
            else:
                self.status = '1'
                self.save()
                return False
        else:
            return None

