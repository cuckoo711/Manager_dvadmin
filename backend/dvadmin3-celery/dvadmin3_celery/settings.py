from datetime import timedelta

from application import settings

# ================================================= #
# ***************** 插件配置区开始 *******************
# ================================================= #
# 路由配置
plugins_url_patterns = [
    {"re_path": r'api/dvadmin_celery/', "include": "dvadmin3_celery.urls"}
]
# app 配置
apps = ['django_celery_beat', 'django_celery_results', 'dvadmin3_celery']
# 租户模式中，public模式共享app配置
tenant_shared_apps = []
# ================================================= #
# ******************* 插件配置区结束 *****************
# ================================================= #

if not hasattr(settings, 'CACHES'):
    _DEFAULT_CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f'{settings.REDIS_URL}/{getattr(settings, "REDIS_DB") or 1}',
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        },
    }
else:
    _DEFAULT_CACHES = settings.CACHES

if not hasattr(settings, 'REDIS_URL'):
    raise Exception("请配置redis地址，否则celery无法使用！")

# ********** 赋值到 settings 中 **********
settings.CACHES = _DEFAULT_CACHES
settings.INSTALLED_APPS += [app for app in apps if app not in settings.INSTALLED_APPS]
settings.TENANT_SHARED_APPS += tenant_shared_apps
# ********** celery 配置 **********
if not hasattr(settings, 'BROKER_URL'):
    settings.BROKER_URL = f'{settings.REDIS_URL}/{getattr(settings, "CELERY_BROKER_DB") or 2}'

# ********** 执行结果保存位置 **********
if not hasattr(settings, 'CELERY_RESULT_BACKEND'):
    settings.CELERY_RESULT_BACKEND = 'django-db'

# ********** Backend数据库 **********
if not hasattr(settings, 'CELERYBEAT_SCHEDULER'):
    settings.CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

if not hasattr(settings, 'CELERY_ACCEPT_CONTENT'):
    settings.CELERY_ACCEPT_CONTENT = ['json']

if not hasattr(settings, 'CELERY_TASK_SERIALIZER'):
    settings.CELERY_TASK_SERIALIZER = 'json'

if not hasattr(settings, 'CELERY_RESULT_SERIALIZER'):
    settings.CELERY_RESULT_SERIALIZER = 'json'

if not hasattr(settings, 'CELERY_TIMEZONE'):
    settings.CELERY_TIMEZONE = 'Asia/Shanghai'

if not hasattr(settings, 'CELERY_ENABLE_UTC'):
    settings.CELERY_ENABLE_UTC = False

if not hasattr(settings, 'DJANGO_CELERY_BEAT_TZ_AWARE'):
    settings.DJANGO_CELERY_BEAT_TZ_AWARE = False

if not hasattr(settings, 'CELERY_TASK_TRACK_STARTED'):
    settings.CELERY_TASK_TRACK_STARTED = True

if not hasattr(settings, 'CELERY_TASK_TIME_LIMIT'):
    settings.CELERY_TASK_TIME_LIMIT = 30 * 60

if not hasattr(settings, 'CELERY_TASK_SOFT_TIME_LIMIT'):
    settings.CELERY_TASK_SOFT_TIME_LIMIT = 30 * 60

settings.CELERY_broker_connection_retry_on_startup = True

# ********** 注册路由 **********
settings.PLUGINS_URL_PATTERNS += plugins_url_patterns

# 避免时区的问题
CELERY_ENABLE_UTC = False
DJANGO_CELERY_BEAT_TZ_AWARE = False
broker_connection_retry_on_startup = True
CELERY_broker_connection_retry_on_startup = True

