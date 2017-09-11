import sys
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY', 'test')
DEBUG = os.environ.get('DEBUG', None) == 'True'
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
ALLOWED_HOSTS = [os.environ.get('HOST', '*')]
SECURE_SSL_REDIRECT = os.environ.get('SSL', None) == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_L10N = True
USE_TZ = False
ROOT_URLCONF = 'line.urls'
WSGI_APPLICATION = 'line.wsgi.application'
API_VERSION = str(os.environ.get('API_VERSION', 40))
LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
LINE_ACCESS_SECRET = os.environ.get('LINE_ACCESS_SECRET')
URL = os.environ.get('URL', 'localhost:8000')
EINSTEIN_VISION_URL = os.environ.get('EINSTEIN_VISION_URL')
EINSTEIN_VISION_ACCOUNT_ID = os.environ.get('EINSTEIN_VISION_ACCOUNT_ID')
EINSTEIN_VISION_API_VERSION = os.environ.get('EINSTEIN_VISION_API_VERSION')
EINSTEIN_VISION_MODELID = os.environ.get('EINSTEIN_VISION_MODELID')

if not os.environ.get('EINSTEIN_VISION_PRIVATE_KEY'):
    try:
        with open(BASE_DIR + '/einstein_private.key', 'r') as pf:
            private_key = pf.read()
    except:
        private_key = None
else:
    private_key = os.environ.get('EINSTEIN_VISION_PRIVATE_KEY')

EINSTEIN_VISION_PRIVATE_KEY = private_key


if DEBUG:
    INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

if TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    db = dj_database_url.parse(os.environ.get('DATABASE_URL') +
                               '?currentSchema=salesforce,public')
    try:
        del db['OPTIONS']['currentSchema']
    except:
        pass

    DATABASES = {
        'default': db
    }

LOGGING = {
    'version': 1,
    'formatters': {
        'all': {
            'format': '\t'.join([
                '[%(levelname)s]',
                'code:%(lineno)s',
                'asctime:%(asctime)s',
                'module:%(module)s',
                'message:%(message)s',
            ])
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'all'
        },
    },
    'loggers': {
        'command': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
