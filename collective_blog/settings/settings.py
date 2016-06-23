# -*- coding: utf-8 -*-
"""Common settings that are used in development, travis, and production builds

These variables may be extended or overwritten in the build-specific files.

"""

from __future__ import unicode_literals

import os
from django.utils.translation import ugettext_lazy as _

SITE_NAME = 'a.k.a. Блог'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'TEST_SECRET_KEY')
if SECRET_KEY == 'TEST_SECRET_KEY':
    print('\033[01;31mWarning: no secret key set!\033[0;00m')

# Application definition

# This list may be extended in build-specific configs
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'registration',
    'captcha',
    'messages_extends',
    'mptt',

    'collective_blog',
    'user',
    's_appearance',
    's_markdown',
    's_voting',
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

    'collective_blog.middleware.ActiveUserMiddleware',
]

# This list and its substructures may be extended in build-specific configs
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

ROOT_URLCONF = 'collective_blog.urls'

WSGI_APPLICATION = 'collective_blog.wsgi.application'

# Auth and registration setup

AUTH_USER_MODEL = 'auth.User'

AUTHENTICATION_BACKENDS = (
    'collective_blog.backend.auth.CaseInsensitiveModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/u/a/login/'

LOGIN_REDIRECT_URL = '/'

REGISTRATION_AUTO_LOGIN = True

ACCOUNT_ACTIVATION_DAYS = 30

REGISTRATION_FORM = 'user.forms.RegistrationFormCaptcha'

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '')
if RECAPTCHA_PUBLIC_KEY == '':
    print('\033[01;31mWarning: no recaptcha public key set!\033[0;00m')

RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '')
if RECAPTCHA_PRIVATE_KEY == '':
    print('\033[01;31mWarning: no recaptcha key set!\033[0;00m')

NOCAPTCHA = True

RECAPTCHA_USE_SSL = True

INCLUDE_AUTH_URLS = False

# Messages
# https://docs.djangoproject.com/en/1.9/ref/contrib/messages/

MESSAGE_STORAGE = 'messages_extends.storages.FallbackStorage'

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
    # ('en', _('English')),
]

LANGUAGE_CODE = 'ru_RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Files upload settings
# https://docs.djangoproject.com/en/1.9/topics/files/

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Email settings
# https://docs.djangoproject.com/en/1.9/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
