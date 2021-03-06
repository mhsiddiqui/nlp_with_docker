"""
Django settings for urdu_tts project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

project_home = BASE_DIR

SECRET_KEY = 'y5_%9u88a6hop@q+pq!=0rqi3!(lyrz*9iosepktg0e=79iq@^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'True'))
# DEBUG = True


ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'tts',
    'error_report'
    # 'storages',
    # 'django_ftpserver'
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'error_report.middleware.ExceptionProcessor'
    # 'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'urdu_tts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'urdu_tts.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('DATABASE', 'postgres'),
            'PORT': 5432,
        }
    }

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE', "django.contrib.staticfiles.storage.StaticFilesStorage")

FESTIVALDIR = os.environ.get('FESTIVALDIR')
if not FESTIVALDIR:
    raise Exception('environment variable FESTIVALDIR is not set. It should point Festival Directory')
FESTIVAL = os.path.join(FESTIVALDIR, "bin", "festival")

TTS_COMMAND = FESTIVALDIR + '/bin/text2wave -o {path}/tmp/output/{output_file} -eval "({voice})" {input_file}'

LOGIN_URL = '/admin/login/'

SOUND_OPTIONS = (
    ('voice_pucit_indic_ur_cg', 'Speaker 1 (Fast)'),
    ('voice_pucit_indic_urs_cg', 'Speaker 1 (Slow)'),
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'tts.utils.CustomPagination',
    'PAGE_SIZE': 8
}


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'info.ballogy@gmail.com'
EMAIL_HOST_PASSWORD = 'ballogy2k18'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ERROR_DETAIL_SETTINGS = {
    "ERROR_DETAIL_HEIGHT": 5000
}
