"""
Development settings - unsuitable for production.

See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

"""

from __future__ import unicode_literals

from .common_settings import *

print('\033[00;32mLoading travis settings\033[0;00m')


DEBUG = False

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'django.template.context_processors.debug'
]

ALLOWED_HOSTS = ['localhost']

ADMINS = []

MANAGERS = []

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travis_ci_db',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
    }
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
