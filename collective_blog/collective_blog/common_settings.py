# -*- coding: utf-8 -*-
"""
Common settings that are used in development, travis, and production builds.

These variables may be extended or overwritten in the build-specific files.

"""

from __future__ import unicode_literals

import os
from django.utils.translation import ugettext_lazy as _

SITE_NAME = 'a.k.a. Блог'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

# This list may be extended in build-specific configs
INSTALLED_APPS = [
    'collective_blog',
    'user',
    'appearance',
    'markdown',

    'registration',
    'ckeditor',
    'ckeditor_uploader',
    'captcha',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# This list may be extended in build-specific configs
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

# This list and its substructures may be extended in build-specific configs
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
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

ROOT_URLCONF = 'collective_blog.urls'

WSGI_APPLICATION = 'collective_blog.wsgi.application'

# Auth and registration setup

AUTH_USER_MODEL = 'auth.User'

LOGIN_URL = '/u/a/login/'

LOGIN_REDIRECT_URL = '/'

REGISTRATION_AUTO_LOGIN = True

ACCOUNT_ACTIVATION_DAYS = 30

REGISTRATION_FORM = 'user.forms.RegistrationFormCaptcha'

NOCAPTCHA = True

RECAPTCHA_USE_SSL = True

INCLUDE_AUTH_URLS = False

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

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Files upload settings
# https://docs.djangoproject.com/en/1.9/topics/files/

MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

CKEDITOR_UPLOAD_PATH = 'upload/'

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
