from django.db import models

from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


class QQBotMain(CoreModel):
    """
    QQBot主表
    """
    qq = models.CharField(max_length=20, verbose_name='QQ号', unique=True)
    name = models.CharField(max_length=50, verbose_name='QQ昵称')
    is_active = models.BooleanField(verbose_name='是否激活', default=True)

    class Meta:
        db_table = table_prefix + 'qqbot_main'
        verbose_name = 'QQBot主表'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']


class QQBotGroup(CoreModel):
    """
    QQBot群组表
    """
    qqbot = models.ForeignKey(QQBotMain, related_name="groups", on_delete=models.CASCADE,
                              db_constraint=False, verbose_name="关联QQBot", help_text="关联QQBot")
    group_id = models.CharField(max_length=20, verbose_name='群号')
    group_name = models.CharField(max_length=50, verbose_name='群名称')
    is_active = models.BooleanField(verbose_name='是否激活', default=True)

    class Meta:
        db_table = table_prefix + 'qqbot_group'
        verbose_name = 'QQBot群组表'
        verbose_name_plural = verbose_name
        ordering = ['-update_datetime']
        unique_together = ('qqbot', 'group_id')


class QQBotManage(CoreModel):
    """
    QQBot管理表
    """
    qqbot = models.ForeignKey(QQBotMain, related_name="manages", on_delete=models.CASCADE,
                              db_constraint=False, verbose_name="关联QQBot", help_text="关联QQBot")
    manager_qq = models.CharField(max_length=20, verbose_name='管理员QQ号')

