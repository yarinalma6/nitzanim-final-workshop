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

# ניקוי BASE_PATH כדי למנוע סלאשים כפולים בתחילת הכתובת
BASE_PATH = getattr(configuration, 'BASE_PATH', '').strip('/')
if BASE_PATH:
    BASE_PATH += '/'

CORS_ORIGIN_ALLOW_ALL = getattr(configuration, 'CORS_ORIGIN_ALLOW_ALL', False)
CORS_ORIGIN_REGEX_WHITELIST = getattr(configuration, 'CORS_ORIGIN_REGEX_WHITELIST', [])
CORS_ORIGIN_WHITELIST = getattr(configuration, 'CORS_ORIGIN_WHITELIST', [])
CSRF_COOKIE_NAME = getattr(configuration, 'CSRF_COOKIE_NAME', 'csrftoken')

# הוספת הדומיין לרשימת המהימנים עבור ה-ALB
CSRF_TRUSTED_ORIGINS = [SITE_URL, 'https://status.yarin-noa.site']

DATE_FORMAT = getattr(configuration, 'DATE_FORMAT', 'N j, Y')
DATETIME_FORMAT = getattr(configuration, 'DATETIME_FORMAT', 'N j, Y g:i a')
DEBUG = getattr(configuration, 'DEBUG', False)
DEVELOPER = getattr(configuration, 'DEVELOPER', False)
EMAIL = getattr(configuration, 'EMAIL', {})
EXEMPT_VIEW_PERMISSIONS = []
FIELD_CHOICES = getattr(configuration, 'FIELD_CHOICES', {})
INTERNAL_IPS = getattr(configuration, 'INTERNAL_IPS', ('127.0.0.1', '::1'))
LOGGING = getattr(configuration, 'LOGGING', {})
LOGIN_REQUIRED = True
LOGIN_TIMEOUT = getattr(configuration, 'LOGIN_TIMEOUT', None)

MEDIA_ROOT = getattr(configuration, 'MEDIA_ROOT', os.path.join(BASE_DIR, 'media')).rstrip('/')

PLUGINS = getattr(configuration, 'PLUGINS', [])
PLUGINS_CONFIG = getattr(configuration, 'PLUGINS_CONFIG', {})
RQ_DEFAULT_TIMEOUT = getattr(configuration, 'RQ_DEFAULT_TIMEOUT', 300)
SESSION_COOKIE_NAME = getattr(configuration, 'SESSION_COOKIE_NAME', 'sessionid')
SHORT_DATE_FORMAT = getattr(configuration, 'SHORT_DATE_FORMAT', 'Y-m-d')
SHORT_DATETIME_FORMAT = getattr(configuration, 'SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
SHORT_TIME_FORMAT = getattr(configuration, 'SHORT_TIME_FORMAT', 'H:i:s')
TIME_FORMAT = getattr(configuration, 'TIME_FORMAT', 'g:i a')
TIME_ZONE = getattr(configuration, 'TIME_ZONE', 'UTC')

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

# --- לוגיקת REDIS מתוקנת (עם Socket Timeouts לאבחון) ---
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
            'SOCKET_CONNECT_TIMEOUT': 10,  # זמן המתנה מקסימלי לחיבור
            'SOCKET_TIMEOUT': 10,          # זמן המתנה מקסימלי לתגובה
        }
    }
}

RQ_PARAMS = {
    'HOST': TASKS_REDIS_HOST,
    'PORT': TASKS_REDIS_PORT,
    'DB': TASKS_REDIS_DATABASE,
    'PASSWORD': TASKS_REDIS_PASSWORD,
    'DEFAULT_TIMEOUT': RQ_DEFAULT_TIMEOUT,
    'SOCKET_TIMEOUT': 10,              # מונע מהוורקר "לקפוא" לנצח
}

RQ_QUEUES = {
    'high': RQ_PARAMS,
    'default': RQ_PARAMS,
    'low': RQ_PARAMS,
}

# --- המשך הגדרות סטנדרטיות ---
if LOGIN_TIMEOUT is not None:
    SESSION_COOKIE_AGE = LOGIN_TIMEOUT

EMAIL_HOST = EMAIL.get('SERVER')
EMAIL_HOST_USER = EMAIL.get('USERNAME')
EMAIL_HOST_PASSWORD = EMAIL.get('PASSWORD')
EMAIL_PORT = EMAIL.get('PORT', 25)
EMAIL_SUBJECT_PREFIX = '[Status-Page] '
EMAIL_USE_SSL = EMAIL.get('USE_SSL', False)
EMAIL_USE_TLS = EMAIL.get('USE_TLS', False)
EMAIL_TIMEOUT = EMAIL.get('TIMEOUT', 10)
SERVER_EMAIL = EMAIL.get('FROM_EMAIL')
DEFAULT_FROM_EMAIL = EMAIL.get('FROM_EMAIL')

LOGIN_URL = f'/{BASE_PATH}dashboard/login/'
LOGIN_REDIRECT_URL = f'/{BASE_PATH}dashboard/'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_browser_reload',
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
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'statuspage.middleware.APIVersionMiddleware',
    'statuspage.middleware.ObjectChangeMiddleware',
    'statuspage.middleware.DynamicConfigMiddleware',
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

AUTHENTICATION_BACKENDS = [
    'statuspage.authentication.ObjectPermissionBackend',
]

OTP_ADMIN_HIDE_SENSITIVE_DATA = True
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = False
USE_TZ = True
USE_DEPRECATED_PYTZ = True

WSGI_APPLICATION = 'statuspage.wsgi.application'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = f'/{BASE_PATH}static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'project-static', 'dist'),
    os.path.join(BASE_DIR, 'project-static', 'img'),
    ('docs', os.path.join(BASE_DIR, 'project-static', 'docs')),
)

MEDIA_URL = '/{}media/'.format(BASE_PATH)
DATA_UPLOAD_MAX_NUMBER_FIELDS = None
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK_VERSION = '.'.join(VERSION.split('-')[0].split('.')[:2])
REST_FRAMEWORK = {
    'ALLOWED_VERSIONS': [REST_FRAMEWORK_VERSION],
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'statuspage.api.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_METADATA_CLASS': 'statuspage.api.metadata.BulkOperationMetadata',
    'DEFAULT_PAGINATION_CLASS': 'statuspage.api.pagination.OptionalLimitOffsetPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'statuspage.api.authentication.TokenPermissions',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'statuspage.api.renderers.FormlessBrowsableAPIRenderer',
    ),
    'DEFAULT_VERSION': REST_FRAMEWORK_VERSION,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
}

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'utilities.custom_inspectors.StatusPageSwaggerAutoSchema',
    'DEFAULT_INFO': 'statuspage.urls.openapi_info',
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'VALIDATOR_URL': None,
}

for plugin_name in PLUGINS:
    try:
        plugin = importlib.import_module(plugin_name)
    except ModuleNotFoundError as e:
        if getattr(e, 'name') == plugin_name:
            raise ImproperlyConfigured(f"Unable to import plugin {plugin_name}: Module not found.")
        raise e

    try:
        plugin_config = plugin.config
        INSTALLED_APPS.append("{}.{}".format(plugin_config.__module__, plugin_config.__name__))
    except AttributeError:
        raise ImproperlyConfigured(f"Plugin {plugin_name} does not provide a 'config' variable.")

    if plugin_name not in PLUGINS_CONFIG:
        PLUGINS_CONFIG[plugin_name] = {}
    plugin_config.validate(PLUGINS_CONFIG[plugin_name], VERSION)

    plugin_middleware = plugin_config.middleware
    if plugin_middleware and type(plugin_middleware) in (list, tuple):
        MIDDLEWARE.extend(plugin_middleware)

    if type(plugin_config.queues) is not list:
        raise ImproperlyConfigured(f"Plugin {plugin_name} queues must be a list.")

    RQ_QUEUES.update({
        f"{plugin_name}.{queue}": RQ_PARAMS for queue in plugin_config.queues
    })