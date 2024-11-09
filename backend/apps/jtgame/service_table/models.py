import os

from django.db import models

from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.

class ServiceTableChannel(CoreModel):
    name = models.CharField(max_length=50, verbose_name='渠道名称')
    column = models.CharField(max_length=50, verbose_name='列名', null=True, default='')

    class Meta:
        db_table = table_prefix + 'service_table_channel'
        verbose_name = '开服表渠道'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class ServiceTableMap(CoreModel):
    game_name = models.CharField(max_length=50, verbose_name='游戏名称')
    channel = models.ForeignKey(ServiceTableChannel, on_delete=models.CASCADE, verbose_name='渠道')
    game_map_name = models.CharField(max_length=50, verbose_name='游戏映射名称')


# 开服表模板
class ServiceTableTemplate(CoreModel):
    IS_SPLIT = (
        ('2', '否'),
        ('1', '是'),
    )
    IS_ENABLE = (
        ('0', '否'),
        ('1', '是'),
    )
    OUTPUT_FORMAT = (
        ('0', 'xls'),
        ('1', 'xlsx'),
        ('2', 'csv'),
    )
    # 输出引擎
    OUTPUT_ENGINE = (
        ('0', 'ExcelWriter'),
        ('1', 'DataFrame'),
        ('2', 'Workbook'),
    )

    channel = models.ForeignKey(ServiceTableChannel, on_delete=models.CASCADE, verbose_name='渠道')
    template_name = models.CharField(max_length=255, verbose_name='模板名字', null=True)
    template_fields = models.TextField(verbose_name='模板字段')
    is_split = models.CharField(max_length=1, choices=IS_SPLIT, verbose_name='是否分表', default='0')
    output_format = models.CharField(max_length=1, choices=OUTPUT_FORMAT, verbose_name='输出格式', default='0')
    output_engine = models.CharField(max_length=1, choices=OUTPUT_ENGINE, verbose_name='输出引擎', default='0')
    is_enable = models.CharField(max_length=1, choices=IS_ENABLE, verbose_name='是否启用', default='1')

    class Meta:
        db_table = table_prefix + 'service_table_template'
        verbose_name = '开服表模板'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def clean(self):
        self.check_template_fields()

    def __str__(self):
        return self.channel.name + '模板:' + self.template_name

    def check_template_fields(self):
        self.template_fields = self.template_fields.strip()
        if not (self.template_fields.startswith('{') and self.template_fields.endswith('}')):
            self.template_fields = self.template_fields.replace(
                ' ', '').replace('\n', '').replace('，', ',')


# 开服表通用
class ServiceTableNormal(CoreModel):
    GENERATE_STATUS = (
        ('0', '未生成'),
        ('1', '已生成'),
    )
    game_name = models.CharField(max_length=50, verbose_name='游戏名称')
    open_name = models.CharField(max_length=10, verbose_name='初始区服名称')
    open_datetime = models.DateTimeField(verbose_name='开服时间')
    open_frequency = models.IntegerField(verbose_name='开服频率', default=1)
    open_count = models.IntegerField(verbose_name='开服数量', default=1)
    copy_content = models.CharField(max_length=2048, verbose_name='复制内容', null=True)
    first_service_path = models.CharField(max_length=255, verbose_name='首服文件路径', null=True)
    no_first_service_path = models.CharField(max_length=255, verbose_name='无首服文件路径', null=True)
    generate_status = models.CharField(max_length=1, choices=GENERATE_STATUS, verbose_name='生成状态', default='0')

    class Meta:
        db_table = table_prefix + 'service_table_normal'
        verbose_name = '开服表通用'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def __str__(self):
        return self.game_name + '开服表:' + self.open_name

    # 删除条目时删除文件
    def delete(self, *args, **kwargs):
        if os.path.exists(self.first_service_path):
            os.remove(self.first_service_path)
        if os.path.exists(self.no_first_service_path):
            os.remove(self.no_first_service_path)
        super().delete(*args, **kwargs)


class ServiceTableSplit(CoreModel):
    GENERATE_STATUS = (
        ('0', '未生成'),
        ('1', '已生成'),
        ('2', '生成失败'),
        ('3', '生成中'),
    )
    output_dir = models.CharField(max_length=255, verbose_name='输出目录', null=True)
    service_table_normals = models.ManyToManyField(ServiceTableNormal, verbose_name='开服表通用')
    service_table_split_zip = models.CharField(max_length=255, verbose_name='分表压缩包路径', null=True)
    generate_log = models.TextField(verbose_name='生成日志', null=True, default='')
    generate_status = models.CharField(max_length=1, choices=GENERATE_STATUS, verbose_name='生成状态', default='0')

    class Meta:
        db_table = table_prefix + 'service_table_split'
        verbose_name = '开服表分表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
