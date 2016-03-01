"""
Development settings - unsuitable for production.

See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

"""

from __future__ import unicode_literals

print('\033[00;32mLoading travis settings\033[0;00m')

DEBUG = False

from .settings import *

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'django.template.context_processors.debug'
]

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
