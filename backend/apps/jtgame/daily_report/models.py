from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


# 服务器账号
class ConsoleAccount(CoreModel):
    account = models.CharField(max_length=50, verbose_name='账号')
    access_key = models.CharField(max_length=100, verbose_name='Access Key')
    secret_key = models.CharField(max_length=100, verbose_name='Secret Key')

    def __str__(self):
        return self.account

    class Meta:
        db_table = table_prefix + 'daily_report_console_account'
        verbose_name = '服务器账号'
        verbose_name_plural = verbose_name
        ordering = ['account']


# quick账号
class QuickAccount(CoreModel):
    account = models.CharField(max_length=50, verbose_name='账号')
    password = models.CharField(max_length=50, verbose_name='密码')

    def __str__(self):
        return self.account

    class Meta:
        db_table = table_prefix + 'daily_report_quick_account'
        verbose_name = 'quick账号'
        verbose_name_plural = verbose_name
        ordering = ['account']


class ReportData(CoreModel):
    date = models.DateField(verbose_name='日期', unique=True)
    data = models.JSONField(verbose_name='数据', null=True, blank=True)
    wash_data = models.JSONField(verbose_name='清洗数据', null=True, blank=True)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总收入', default=0)

    def __str__(self):
        return str(self.date)

    class Meta:
        db_table = table_prefix + 'daily_report_data'
        verbose_name = '日报信息'
        verbose_name_plural = verbose_name
        ordering = ['-date']

    def clean(self):
        try:
            datetime.strptime(str(self.date), '%Y-%m-%d')
        except ValueError:
            raise ValidationError("日期格式错误。请使用YYYY-MM-DD格式。")

    def save(self, *args, **kwargs):
        self.clean()
        self.data = self.data or {}
        super().save(*args, **kwargs)


class DayliData(CoreModel):
    DATA_TYPE = (
        (0, '前1天数据'),
        (1, '前7天数据'),
        (2, '前30天数据'),
        (3, '上月数据'),
        (4, '本月数据'),
    )

    date = models.DateField(verbose_name='日期', db_index=True)  # 已经有索引
    game_name = models.CharField(max_length=50, verbose_name='游戏名称')
    banhao = models.CharField(max_length=50, verbose_name='版号', db_index=True)  # 为 banhao 添加索引
    data_type = models.IntegerField(choices=DATA_TYPE, verbose_name='数据类型', db_index=True)  # 为 data_type 添加索引
    actives = models.IntegerField(verbose_name='今日日活', default=0)
    recharge = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='充值', default=0)
    channels = models.IntegerField(verbose_name='渠道数', default=0)
    subscribers = models.IntegerField(verbose_name='用户数', default=0)
    devices = models.IntegerField(verbose_name='设备数', default=0)
    payments = models.IntegerField(verbose_name='付费用户数', default=0)
    online_days = models.IntegerField(verbose_name='在线天数', default=0)

    class Meta:
        db_table = table_prefix + 'daily_report_daily_data'
        verbose_name = '日报详细数据'
        verbose_name_plural = verbose_name
        ordering = ['-date']
        unique_together = ('game_name', 'date', 'data_type')  # 保持原来的唯一约束
        indexes = [
            models.Index(fields=['banhao', 'data_type', 'date']),  # 为 banhao, data_type, date 创建复合索引
            models.Index(fields=['game_name', 'date', 'data_type']),  # 为 game_name, date, data_type 创建复合索引
            models.Index(fields=['banhao']),  # 为 banhao 字段创建单字段索引
            models.Index(fields=['data_type']),  # 为 data_type 字段创建单字段索引
        ]

    def __str__(self):
        return f'{self.game_name} - {self.get_data_type_display()} - {self.date}'


class Consoles(CoreModel):
    account = models.CharField(max_length=50, verbose_name='所属账号')
    instance_id = models.CharField(max_length=50, verbose_name='实例ID')
    instance_name = models.CharField(max_length=50, verbose_name='实例名称')
    status = models.CharField(max_length=50, verbose_name='状态')
    instance_type_id = models.CharField(max_length=50, verbose_name='规格')
    cpus = models.CharField(max_length=50, verbose_name='CPU')
    memory_size = models.CharField(max_length=50, verbose_name='内存')
    eip_address = models.CharField(max_length=50, verbose_name='主IPv4地址')
    primary_ip_address = models.CharField(max_length=50, verbose_name='次IPv4地址')
    instance_charge_type = models.CharField(max_length=50, verbose_name='实例计费类型')
    expired_at = models.DateTimeField(verbose_name='到期时间', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='创建时间', null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', null=True, blank=True)
    renewal_status = models.BooleanField(default=False, verbose_name='续费状态')

    def __str__(self):
        return self.instance_name

    class Meta:
        db_table = table_prefix + 'daily_report_consoles'
        verbose_name = '实例信息'
        verbose_name_plural = verbose_name
        ordering = ['expired_at']

    def save(self, *args, **kwargs):
        if isinstance(self.expired_at, str):
            self.expired_at = datetime.strptime(self.expired_at, '%Y-%m-%d %H:%M:%S')
        if self.expired_at and timezone.is_naive(self.expired_at):
            self.expired_at = timezone.make_aware(self.expired_at)
        super().save(*args, **kwargs)
