"""
Development settings - unsuitable for production.

See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

"""

from __future__ import unicode_literals

print('\033[00;32mLoading development settings\033[0;00m')

DEBUG = True

from .settings import *

# Log all sql queries
MIDDLEWARE_CLASSES.append('collective_blog.middleware.TerminalLogging')

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

print('\033[01;33mWarning: recaptcha is running in the debug mode!\033[0;00m')
os.environ['RECAPTCHA_TESTING'] = 'True'
