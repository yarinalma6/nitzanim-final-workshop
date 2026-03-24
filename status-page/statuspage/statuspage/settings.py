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
    raise RuntimeError(f"Status-Page requires Python 3.10 or later.")

config_path = os.getenv('STATUS_PAGE_CONFIGURATION', 'statuspage.configuration')
try:
    configuration = importlib.import_module(config_path)
except ModuleNotFoundError:
    raise ImproperlyConfigured(f"Configuration module {config_path} not found.")

for parameter in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY', 'REDIS', 'SITE_URL']:
    if not hasattr(configuration, parameter):
        raise ImproperlyConfigured(f"Required parameter {parameter} is missing.")

ALLOWED_HOSTS = getattr(configuration, 'ALLOWED_HOSTS', ['*'])
DATABASE = getattr(configuration, 'DATABASE')
REDIS = getattr(configuration, 'REDIS')
SECRET_KEY = getattr(configuration, 'SECRET_KEY')
SITE_URL = getattr(configuration, 'SITE_URL')

# --- הגדרות אבטחה ל-AWS ALB (זו התוספת היחידה שלנו לאבטחה) ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

CSRF_TRUSTED_ORIGINS = getattr(configuration, 'CSRF_TRUSTED_ORIGINS', [SITE_URL, 'https://status.yarin-noa.site'])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE.get('NAME'),
        'USER': DATABASE.get('USER'),
        'PASSWORD': DATABASE.get('PASSWORD'),
        'HOST': DATABASE.get('HOST'),
        'PORT': DATABASE.get('PORT'),
        'CONN_MAX_AGE': DATABASE.get('CONN_MAX_AGE', 300),
    },
}

TASKS_REDIS_HOST = os.environ.get('REDIS_HOST', REDIS.get('tasks', {}).get('HOST', 'localhost'))
TASKS_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', REDIS.get('tasks', {}).get('PASSWORD', ''))

RQ_QUEUES = {
    'high': {'HOST': TASKS_REDIS_HOST, 'PORT': 6379, 'DB': 0, 'PASSWORD': TASKS_REDIS_PASSWORD},
    'default': {'HOST': TASKS_REDIS_HOST, 'PORT': 6379, 'DB': 0, 'PASSWORD': TASKS_REDIS_PASSWORD},
    'low': {'HOST': TASKS_REDIS_HOST, 'PORT': 6379, 'DB': 0, 'PASSWORD': TASKS_REDIS_PASSWORD},
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{TASKS_REDIS_HOST}:6379/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': TASKS_REDIS_PASSWORD,
        }
    }
}

# --- טעינה של כל הפרמטרים מהקונפיגורציה (זה מה שיתקן את השגיאה של FIELD_CHOICES) ---
for param in PARAMS:
    if hasattr(configuration, param.name):
        globals()[param.name] = getattr(configuration, param.name)

# הבטחה ש-FIELD_CHOICES מוגדר, גם אם הוא חסר בקונפיגורציה
if 'FIELD_CHOICES' not in globals():
    FIELD_CHOICES = {}

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
    'otp_yubikey',
]

if 'PLUGINS' in globals():
    for plugin in PLUGINS:
        INSTALLED_APPS.append(plugin)

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
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
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
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'project-static', 'dist'),
    os.path.join(BASE_DIR, 'project-static', 'img'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# חובה להוסיף כדי שה-choices של המערכת יעבדו (אם לא נטענו מהקונפיג)
if not hasattr(sys.modules[__name__], 'FIELD_CHOICES'):
    FIELD_CHOICES = {}