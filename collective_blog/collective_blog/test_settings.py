# Development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

from __future__ import unicode_literals

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# Log all sql queries
DB_DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'SECRET_KEY'

ALLOWED_HOSTS = ['localhost']

ADMINS = []

MANAGERS = []

# ReCaptcha
# These are the test keys

RECAPTCHA_PUBLIC_KEY = '6Lcd5hYTAAAAABq47ye0uJEeKh_b3BKVwZOcVwS-'

RECAPTCHA_PRIVATE_KEY = '6Lcd5hYTAAAAAB8q6JLA1-ZYVGXx3eIyekeQ-i0a'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

# Files upload settings
# https://docs.djangoproject.com/en/1.9/topics/files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Email settings
# https://docs.djangoproject.com/en/1.9/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
