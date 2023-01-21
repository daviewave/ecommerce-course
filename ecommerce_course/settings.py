from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY  = os.getenv('SECRET_KEY', 'django-insecure-6lsm7+d8@f#nsv^ax722#x(9&68iks#42@48^%sv-s@narc=wv')
DEBUG       = os.getenv('DEBUG', True)


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'ecommerce-django-dev.us-east-1.elasticbeanstalk.com',
    '*',
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "category",
    "accounts",
    "store",
    "carts",
    "orders",
    "storages",
    "django_ses"
]

AWS_STORAGE_BUCKET_NAME = 'ecommerce-course'

# if 'AWS_STORAGE_BUCKET_NAME' in os.environ:
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
AWS_S3_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_S3_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'
AWS_LOCATION = 'static'
STATICFILES_DIRS = ['ecommerce_course/static']
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django_session_timeout.middleware.SessionTimeoutMiddleware',    
]

# NOTE: the major urls.py router (root urls.py)
ROOT_URLCONF = "ecommerce_course.urls"

SESSION_EXPIRE_SECONDS = 3600  # 1 hour
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = 'accounts/login' # NOTE: need to fix this



TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                
                #NOTE: By adding this, we are allowing all the templates to use this function
                "category.context_processors.get_category_links",
                "carts.context_processors.shopping_cart_counter",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce_course.wsgi.application"

# NOTE: This specifies that we want to use a custom user model
AUTH_USER_MODEL = 'accounts.Account'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.postgresql_psycopg2",
            'NAME':     os.environ['RDS_DB_NAME'],
            'USER':     os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST':     os.environ['RDS_HOSTNAME'],
            'PORT':     os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.postgresql_psycopg2",
            'NAME':     os.getenv('DATABASE_NAME','postgres'),
            'USER':     os.getenv('DATABASE_USERNAME', 'postgres'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
            'HOST':     os.getenv('DATABASE_HOST', 'localhost'),
            'PORT':     os.getenv('DATABASE_PORT', 5432),
        }
    }



# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/



# NOTE: This defines where our static files will be stored in the project
# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR /'static'
# STATICFILES_DIRS = ['ecommerce_course/static']

# NOTE: This defines where our media files will be stored in the project
DEFAULT_FILE_STORAGE = 'ecommerce_course.media_files.MediaStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR /'media'


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

EMAIL_BACKEND           = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL      = 'davidsilveira.3.djs@gmail.com'
FROM_EMAIL              = 'davidsilveira.3.djs@gmail.com'
EMAIL_HOST              = os.getenv('EMAIL_HOST', 'email-smtp.us-east-1.amazonaws.com')
EMAIL_HOST_USER         = os.getenv('EMAIL_HOST_USER', 'AKIAYSAC2SUIDV73W2QF')
EMAIL_HOST_PASSWORD     = os.getenv('EMAIL_HOST_PASSWORD', 'BPIxCDrEEpsjdbQy4hXCclnq2Kc/pVmW+ruNltnrRHGE')
EMAIL_PORT              = os.getenv('EMAIL_PORT', 587)
EMAIL_USE_TLS           = os.getenv('EMAIL_USE_TLS', True)

from django_ses import SESBackend
AWS_SES_REGION = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'davidsilveira.3.djs@gmail.com.us-east-1.amazonaws.com'
AWS_SES_RETURN_PATH     = 'davidsilveira.3.djs@gmail.com'



