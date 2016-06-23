"""Production settings

See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

"""

from __future__ import unicode_literals
import dj_database_url

print('\033[00;32mLoading production settings\033[0;00m')

DEBUG = False

from .settings import *

ADMINS = (('Zelta', 'dev.zelta@gmail.com'), )

MANAGERS = ()

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    # Use sqlite for heroku app
    'default': dj_database_url.config(),
}

# Hosts setup
# https://docs.djangoproject.com/en/1.9/ref/settings/#std:setting-ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'collective-blog-hse-project.herokuapp.com',
    'www.collective-blog-hse-project.herokuapp.com',
]

# Email

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

EMAIL_HOST = os.getenv('EMAIL_HOST', '')

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')

EMAIL_PORT = 465

SERVER_EMAIL = os.getenv('SERVER_EMAIL', '')

EMAIL_SUBJECT_PREFIX = '[heroku collective blog] '

EMAIL_USE_SSL = True

if DEFAULT_FROM_EMAIL and EMAIL_HOST and EMAIL_HOST_PASSWORD and EMAIL_HOST_USER and SERVER_EMAIL:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print('\033[01;31mWarning: mail server config is missing!\033[0;00m')
    print('\033[01;31mWarning: using console mail backend!\033[0;00m')


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


INSTALLED_APPS += [
    'gunicorn',
]


STATIC_ROOT = os.path.join(BASE_DIR, 'collective_blog', 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'collective_blog', 'static'),
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
