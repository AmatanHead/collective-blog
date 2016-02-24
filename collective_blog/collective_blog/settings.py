"""
Django settings for collective_blog project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _


SITE_NAME = 'a.k.a. Блог'


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/
# TODO: checklist before deploying

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Log all sql queries
DB_DEBUG = DEBUG

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'SECRET_KEY'

ALLOWED_HOSTS = ['localhost']

ADMINS = []

MANAGERS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'registration',
    'ckeditor',
    'ckeditor_uploader',
    'captcha',

    'collective_blog',
    'user',
    'appearance',
    'markdown',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

if DB_DEBUG:
    MIDDLEWARE_CLASSES.append('collective_blog.middleware.TerminalLogging')

ROOT_URLCONF = 'collective_blog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'collective_blog/templates'),
            os.path.join(BASE_DIR, 'user/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'collective_blog.context_processors.sitename.sitename',
            ],
        },
    },
]

WSGI_APPLICATION = 'collective_blog.wsgi.application'


# Auth and registration setup

AUTH_USER_MODEL = 'auth.User'

LOGIN_URL = '/u/a/login/'

LOGIN_REDIRECT_URL = '/'

REGISTRATION_AUTO_LOGIN = True

ACCOUNT_ACTIVATION_DAYS = 30

REGISTRATION_FORM = 'user.forms.RegistrationFormCaptcha'

# RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PUBLIC_KEY = '6Lcd5hYTAAAAABq47ye0uJEeKh_b3BKVwZOcVwS-'

# RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_PRIVATE_KEY = '6Lcd5hYTAAAAAB8q6JLA1-ZYVGXx3eIyekeQ-i0a'

NOCAPTCHA = True

RECAPTCHA_USE_SSL = True

INCLUDE_AUTH_URLS = False


# Localization
#

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Files upload settings
# https://docs.djangoproject.com/en/1.9/topics/files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

CKEDITOR_UPLOAD_PATH = 'upload/'

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)


# Email settings
# https://docs.djangoproject.com/en/1.9/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
