# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import os.path
from tempfile import mkdtemp

import django

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '66666666666666666666666666666666666666666666666666'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

tempdir = mkdtemp('test_query_counter_tests')

TEST_QUERY_COUNTER = {
    'ENABLE': True,
    'DETAIL_PATH': os.path.join(tempdir, 'query_count_detail.json'),
    'SUMMARY_PATH': os.path.join(tempdir, 'query_count.json')
}

ROOT_URLCONF = 'tests.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django',
    'test_query_counter',
]

SITE_ID = 1

if django.VERSION >= (1, 10):
    MIDDLEWARE = ()
else:
    MIDDLEWARE_CLASSES = ()
