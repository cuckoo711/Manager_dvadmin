from datetime import datetime, timedelta

from django.db import models

from apps.quickbackend.quickcommon.utils.quickapi import QuickLogin
from apps.quickbackend.quickcommon.utils.utils import mix_channel_status
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


class QuickLog(CoreModel):
    log = models.TextField(verbose_name='日志', help_text='日志', blank=True)

    class Meta:
        db_table = table_prefix + 'quick_log'
        verbose_name = 'Quick后台日志'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class QuickRegularTask(CoreModel):
    TaskType = (
        ('0', '批量关注册'),
        ('1', '批量关支付'),
        ('2', '批量关登录'),
        ('3', '批量开注册'),
        ('4', '批量开支付'),
        ('5', '批量开登录'),
    )
    TASK_STATUS = (
        ('0', '未执行'),
        ('1', '已执行'),
        ('2', '执行失败'),
    )
    # 游戏id
    game_id = models.CharField(max_length=10, verbose_name='游戏ID')
    # 游戏名
    game_name = models.CharField(max_length=30, verbose_name='游戏名')
    # 任务类型
    task_type = models.CharField(max_length=1, choices=TaskType, verbose_name='任务类型')
    # 任务描述
    task_desc = models.TextField(verbose_name='任务描述')
    # 任务参数
    task_params = models.JSONField(verbose_name='任务参数')
    # 任务执行日期
    task_date = models.DateField(verbose_name='执行日期')
    # 任务状态
    status = models.CharField(max_length=1, choices=TASK_STATUS, verbose_name='状态', default='0')

    class Meta:
        db_table = table_prefix + 'quick_regular_task'
        verbose_name = 'Quick后台定时任务'
        verbose_name_plural = verbose_name
        ordering = ('-update_datetime',)

    def execute_task(self):
        self.description = '开始执行任务\n'
        self.save()
        user: QuickUser = QuickUser.objects.filter(creator=self.creator, status='0').first()
        if not user:
            self.description += '未找到可用账号'
            self.status = '2'
            self.save()
            return
        self.description += f'使用账号：{user.username}\n'

        if not user.check_cookie():
            if not user.update_cookie():
                self.description += '账号cookie过期'
                self.status = '2'
                self.save()
                return
        self.description += f'账号cookie状态正常\n'

        quick_sdk = QuickLogin()
        quick_sdk.load_cookie(user.cookie)
        switch_data = quick_sdk.switch_game(self.game_id)
        if not switch_data:
            self.description += '切换游戏失败'
            self.status = '2'
            self.save()
            return
        self.description += '切换游戏成功\n'

        channel_data = quick_sdk.get_channel_list(self.game_id)
        update_channel_status = mix_channel_status(channel_data, self.task_params, self.task_type)
        if not update_channel_status:
            self.description += '合并状态失败'
            self.status = '2'
            self.save()
            return
        self.description += '合并状态成功\n'

        update_result = quick_sdk.update_channel_status(self.game_id, update_channel_status)
        if not update_result:
            self.description += '更新状态失败'
            self.status = '2'
            self.save()
            return
        self.description += '任务执行成功'
        self.status = '1'
        self.save()
