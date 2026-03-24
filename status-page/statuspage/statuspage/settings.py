import importlib
import os
import sys
import platform
from django.core.exceptions import ImproperlyConfigured
from statuspage.config import PARAMS

VERSION = '2.0.17-dev'
HOSTNAME = platform.node()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config_path = os.getenv('STATUS_PAGE_CONFIGURATION', 'statuspage.configuration')
try:
    configuration = importlib.import_module(config_path)
except ModuleNotFoundError:
    raise ImproperlyConfigured(f"Configuration module {config_path} not found.")

for parameter in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY', 'REDIS', 'SITE_URL']:
    if not hasattr(configuration, parameter):
        raise ImproperlyConfigured(f"Required parameter {parameter} is missing.")

# --- הגדרות אבטחה ו-Proxy (קריטי ל-AWS ALB) ---
ALLOWED_HOSTS = ['*']
# אומר ל-Django לסמוך על ה-Header של ה-ALB שמעיד על HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# הגדרות URL מתוך הקונפיגורציה
SECRET_KEY = getattr(configuration, 'SECRET_KEY')
SITE_URL = getattr(configuration, 'SITE_URL')
CSRF_TRUSTED_ORIGINS = [SITE_URL, 'https://status.yarin-noa.site']

# --- מסדי נתונים ---
DATABASE = getattr(configuration, 'DATABASE')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE.get('NAME'),
        'USER': DATABASE.get('USER'),
        'PASSWORD': DATABASE.get('PASSWORD'),
        'HOST': DATABASE.get('HOST'),
        'PORT': DATABASE.get('PORT'),
    },
}

# --- Redis וקאש ---
REDIS = getattr(configuration, 'REDIS')
TASKS_REDIS_HOST = os.environ.get('REDIS_HOST', REDIS.get('tasks', {}).get('HOST', 'localhost'))
TASKS_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', REDIS.get('tasks', {}).get('PASSWORD', ''))

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

# --- אפליקציות ו-Middleware (כולל WhiteNoise) ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # WhiteNoise מטפל בסטטיק
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # חובה מיד אחרי SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'statuspage.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
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

# --- קבצים סטטיים (נתיבים סופיים) ---
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'project-static', 'dist'),
    os.path.join(BASE_DIR, 'project-static', 'img'),
]

# אחסון WhiteNoise עם דחיסה וניהול Cache
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'