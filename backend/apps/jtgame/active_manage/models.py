from django.db import models

from dvadmin.utils.models import table_prefix


class ActivityGame(models.Model):
    id = models.AutoField(primary_key=True)
    game_name = models.CharField(max_length=255, unique=True, default='')
    up_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.game_name

    class Meta:
        db_table = table_prefix + 'activity_game'
        verbose_name = '活动游戏'
        verbose_name_plural = verbose_name
        ordering = ('-up_date',)


class ActivityContent(models.Model):
    id = models.AutoField(primary_key=True)
    game_name = models.CharField(max_length=255)
    activity_name = models.CharField(max_length=255)
    activity_value = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('activity_name', 'game_name')
        db_table = table_prefix + 'activity_content'
        verbose_name = '活动内容'
        verbose_name_plural = verbose_name
        ordering = ('-id',)

    def __str__(self):
        return f"{self.activity_name} - {self.game_name}"
