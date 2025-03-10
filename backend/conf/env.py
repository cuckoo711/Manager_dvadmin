# ================================================= #
# *************** mysql数据库 配置  *************** #
# ================================================= #
# 使用mysql时，改为此配置
DATABASE_ENGINE = "django.db.backends.mysql"
# 数据库名
DATABASE_NAME = 'manage_jtgame'  # mysql 时使用
# 数据库地址
DATABASE_HOST = '180.184.172.138'
# 数据库端口
DATABASE_PORT = 3306
# 数据库用户名
DATABASE_USER = "manage_jtgame"
# 数据库密码
DATABASE_PASSWORD = 'srnHNzXzjTE5pCaH'

# 表前缀
TABLE_PREFIX = "jtadmin_"
# =========================================
# ******** redis配置，无redis 可不进行配置  ******** #
# ================================================= #
REDIS_DB = 1
REDIS_PASSWORD = 'CUCKOONB'
REDIS_HOST = '127.0.0.1'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'
# ================================================= #
# *************** celery配置  *************** #
# ================================================= #
CELERY_BROKER_DB = 2
CELERY_RESULT_DB = 3
CELERY_BROKER_URL = f'{REDIS_URL}/{CELERY_BROKER_DB}'
CELERY_RESULT_BACKEND = 'django-db'
CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'  # Backend数据库
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'  # Backend数据库
# ================================================= #
# *************** 邮箱配置  *************** #
# ================================================= #
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'jtmail.jingtanggame.com'        # SMTP服务器地址
EMAIL_USE_TLS = False                   # 使用TLS加密传输
EMAIL_USE_SSL = False                  # 使用SSL加密传输（TLS和SSL二选一）
EMAIL_HOST_USER = 'jtadmin@jingtanggame.com'  # 发件邮箱
EMAIL_HOST_PASSWORD = 'JTadmin250110'       # 发件邮箱的密码
EMAIL_PORT = 25                         # SMTP服务端口
EMAIL_TIMEOUT = 5                       # 超时时间
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# ================================================= #
# ****************** 功能 启停  ******************* #
# ================================================= #
DEBUG = True
# 启动登录详细概略获取(通过调用api获取ip详细地址。如果是内网，关闭即可)
ENABLE_LOGIN_ANALYSIS_LOG = True
# 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
LOGIN_NO_CAPTCHA_AUTH = True
# ================================================= #
# ****************** 其他 配置  ******************* #
# ================================================= #

ALLOWED_HOSTS = ["*"]
# 列权限中排除App应用
COLUMN_EXCLUDE_APPS = []
