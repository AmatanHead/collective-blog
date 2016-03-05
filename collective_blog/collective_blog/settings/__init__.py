# -*- coding: utf-8 -*-
"""Django settings for collective_blog project

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/

"""

import os

if 'TRAVIS' in os.environ:
    from .travis_settings import *
else:
    from .dev_settings import *
