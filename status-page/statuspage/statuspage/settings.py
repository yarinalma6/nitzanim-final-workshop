import importlib
import os
import sys
import platform

from django.core.exceptions import ImproperlyConfigured

from statuspage.config import PARAMS

VERSION = '2.0.17-dev'

HOSTNAME = platform.node()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if sys.version_info < (3, 10):
    raise RuntimeError(
        f"Status-Page requires Python 3.10 or later. (Currently installed: Python {platform.python_version()})"
    )

config_path = os.getenv('STATUS_PAGE_CONFIGURATION', 'statuspage.configuration')
try:
    configuration = importlib.import_module(config_path)
except ModuleNotFoundError as e:
    if getattr(e, 'name') == config_path:
        raise ImproperlyConfigured(
            f"Specified configuration module ({config_path}) not found. Please define "
            f"statuspage/statuspage/configuration.py per the documentation, or specify an alternate module "
            f"in the STATUS_PAGE_CONFIGURATION environment variable."
        )
    raise

for parameter in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY', 'REDIS', 'SITE_URL']:
    if not hasattr(configuration, parameter):
        raise ImproperlyConfigured(f"Required parameter {parameter} is missing from configuration.")

# --- תיקון: ALLOWED_HOSTS ו-BASE_PATH ---
ALLOWED_HOSTS = ['*']
DATABASE = getattr(configuration, 'DATABASE')
REDIS = getattr(configuration, 'REDIS')
SECRET_KEY = getattr(configuration, 'SECRET_KEY')
SITE_URL = getattr(configuration, 'SITE_URL')

ADMINS = getattr(configuration, 'ADMINS', [])
AUTH_PASSWORD_VALIDATORS = getattr(configuration, 'AUTH_PASSWORD_VALIDATORS', [])

# ניקוי BASE_PATH
BASE_PATH = getattr(configuration, 'BASE_PATH', '').strip('/')
if BASE_PATH:
    BASE_PATH += '/'

CORS_ORIGIN_ALLOW_ALL = getattr(configuration, 'CORS_ORIGIN_ALLOW_ALL', False)
CSRF_TRUSTED_ORIGINS = [SITE_URL, 'https://status.yarin-noa.site']

DEBUG = getattr(configuration, 'DEBUG', False)
LOGIN_REQUIRED = True

# --- הגדרות חדשות עבור הגרסה הרשמית (תיקון ה-500) ---
QUEUE_MAPPINGS = getattr(configuration, 'QUEUE_MAPPINGS', {
    'webhook': 'default',
})
WEBHOOKS_ENABLED = getattr(configuration, 'WEBHOOKS_ENABLED', True)

for param in PARAMS:
    if hasattr(configuration, param.name):
        globals()[param.name] = getattr(configuration, param.name)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE.get('NAME'),
        'USER': DATABASE.get('USER'),
        'PASSWORD': DATABASE.get('PASSWORD'),
        'HOST': DATABASE.get('HOST'),
        'PORT': DATABASE.get('PORT'),
        'CONN_MAX_AGE': DATABASE.get('CONN_MAX_AGE'),
    },
}

# --- לוגיקת REDIS ---
TASKS_REDIS = REDIS.get('tasks', {})
TASKS_REDIS_HOST = os.environ.get('REDIS_HOST', TASKS_REDIS.get('HOST', 'localhost'))
TASKS_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', TASKS_REDIS.get('PASSWORD', ''))
TASKS_REDIS_PORT = TASKS_REDIS.get('PORT', 6379)
TASKS_REDIS_DATABASE = TASKS_REDIS.get('DATABASE', 0)

CACHING_REDIS = REDIS.get('caching', {})
CACHING_REDIS_HOST = os.environ.get('REDIS_HOST', CACHING_REDIS.get('HOST', 'localhost'))
CACHING_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', CACHING_REDIS.get('PASSWORD', ''))
CACHING_REDIS_PORT = CACHING_REDIS.get('PORT', 6379)
CACHING_REDIS_DATABASE = CACHING_REDIS.get('DATABASE', 0)
CACHING_REDIS_PROTO = 'rediss' if CACHING_REDIS.get('SSL', False) else 'redis'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"{CACHING_REDIS_PROTO}://{CACHING_REDIS_HOST}:{CACHING_REDIS_PORT}/{CACHING_REDIS_DATABASE}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': CACHING_REDIS_PASSWORD,
            'SOCKET_CONNECT_TIMEOUT': 10,
            'SOCKET_TIMEOUT': 10,
        }
    }
}

RQ_DEFAULT_TIMEOUT = getattr(configuration, 'RQ_DEFAULT_TIMEOUT', 300)
RQ_PARAMS = {
    'HOST': TASKS_REDIS_HOST,
    'PORT': TASKS_REDIS_PORT,
    'DB': TASKS_REDIS_DATABASE,
    'PASSWORD': TASKS_REDIS_PASSWORD,
    'DEFAULT_TIMEOUT': RQ_DEFAULT_TIMEOUT,
    'SOCKET_TIMEOUT': 10,
}

RQ_QUEUES = {
    'high': RQ_PARAMS,
    'default': RQ_PARAMS,
    'low': RQ_PARAMS,
}

# --- המשך הגדרות סטנדרטיות ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_tables2',
    'components',
    'extras',
    'incidents',
    'maintenances',
    'users',
    'utilities',
    'metrics',
    'subscribers',
    'django_rq',
    'drf_yasg',
    'queuing',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'statuspage.middleware.APIVersionMiddleware',
    'statuspage.middleware.ObjectChangeMiddleware',
]

ROOT_URLCONF = 'statuspage.urls'
TEMPLATES_DIR = f'{BASE_DIR}/templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': [
                'utilities.templatetags.builtins.filters',
                'utilities.templatetags.builtins.tags',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'statuspage.context_processors.settings_and_registry',
            ],
        },
    },
]

WSGI_APPLICATION = 'statuspage.wsgi.application'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = f'/{BASE_PATH}static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# (יתר ההגדרות נשמרות מהקובץ הקודם שלך)