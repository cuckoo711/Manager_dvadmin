# dvadmin3_celery

#### 介绍
dvadmin3-celery 插件是集成 django-celery-beat、tenant-schemas-celery、django-redis、django-celery-results 的一个后端插件，
安装可快速使用异步任务，包含在线添加任务、启停任务、查看任务记录等功能。<br>
与之相对应的是 dvadmin3-celery-web 前端插件

## 安装包


目录结构：<br>
```
dvadmin-celery
|   dvdadmin_celery
|   |   fixtures
|   |   |   __init__.py
|   |   |   init_menu.json
|   |   |   initialize.py
|   |   views
|   |   |   __init__.py
|   |   |   crontab_schedule.py
|   |   |   interval_schedule.py
|   |   |   periodic_task.py
|   |   |   task.py
|   |   |   task_detail.py
|   |   __init__.py
|   |   admin.py
|   |   apps.py
|   |   settings.py
|   |   tasks.py
|   |   urls.py
|   setup.py
```

### 方式一: 一键导入注册配置
在 application / settings.py 插件配置中下导入默认配置
```python
...
from dvadmin3_celery.settings import *
```
### 方式二: 手动配置
在INSTALLED_APPS 中注册app（注意先后顺序）

```python
INSTALLED_APPS = [
    ...
    'django_celery_beat',
    'django_celery_results',
    'dvadmin3_celery',
]
```

在 application / urls.py 中注册url地址

```python
urlpatterns = [
    ...
    path(r'api/dvadmin_celery/', include('dvadmin3_celery.urls')),
]
```

如果没有系统redis，请启动redis并添加配置 (./conf/env.example.py 及 ./conf/env.py中添加如下配置)

```python
# redis 配置
REDIS_PASSWORD = '' # 如果没密码就为空
REDIS_HOST = '127.0.0.1'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'

```

在 application / settings.py 下添加配置

```python
...
CACHES = { # 配置缓存
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'{REDIS_URL}/1', # 库名可自选1~16
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
BROKER_URL = f'{REDIS_URL}/2' # 库名可自选1~16
CELERY_RESULT_BACKEND = 'django-db' # celery结果存储到数据库中
CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'  # Backend数据库
```

进行迁移及初始化
```python
python3 manage.py migrate 
# 注意备份初始化信息
python3 manage.py init -y 
```

其他配置请参考 django_celery_beat 和 celery 文档

#### 使用说明

``` python
mac/linux:
celery -A application.celery worker -B --loglevel=info

win:
需要安装: pip install eventlet,需要启动两个程序（worker + beat 顺序不分先后）
celery -A application.celery worker -P eventlet --loglevel=info
celery -A application.celery beat --loglevel=info
```

#### 注意
``` python
如果 celery worker 报错 KeyError,可尝试在django_vue_admin/application/celery.py文件里将
app = Celery(f"application")
改为
app = Celery(f"application", include=['dvadmin_celery.tasks'])
再重启尝试
```
redis下载地址：<br>
Mac/Linux下载 http://download.redis.io/releases/ <br>
Windows下载 https://github.com/tporadowski/redis/releases/ <br>
