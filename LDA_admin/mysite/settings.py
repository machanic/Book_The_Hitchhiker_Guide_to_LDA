# coding=utf-8
"""
Django settings for mysite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kd4#tk^vsm=)9=)tx-85&)wi%@b)yrfe-%pf%kl$(&seda%8p+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

TEMPLATE_DEBUG = True




# Application definition

INSTALLED_APPS = (
    #
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
)

ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'web').replace('\\','/'),
)

#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX' : 'av'
    },
    'phi': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        "KEY_PREFIX" : "phi"
    },
    'nw': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        "KEY_PREFIX" : "nw"
    },
    'nwsum': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        "KEY_PREFIX" : "nwsum"
    },
    'nd': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        "KEY_PREFIX" : "nd"
    },
    'ndsum': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        "KEY_PREFIX" : "ndsum"
    },
     'avg_word_dist': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        "KEY_PREFIX" : "avg_word_dist"
    },
    'wordmap': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        "KEY_PREFIX" : "wordmap"
    }
}


'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "topic_model_machen",
        'USER':'root',
        'PASSWORD':'',
        'HOST':'10.13.3.33',
        'PORT':'3306',
    }
}
'''
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATIC_PATH = "D:/LDA_admin/LDA_admin/static"
STATICFILES_FINDERS = ( 
    'django.contrib.staticfiles.finders.FileSystemFinder',    
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',  
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
STATIC_URL = '/res/'
MEDIA_ROOT = os.path.join(BASE_DIR, STATIC_URL)  #变成项目绝对路径,放置静态资源文件

STATICFILES_DIRS = (STATIC_PATH, "D:/LDA_admin/LDA_admin/mysite/web")  #这样可以把D盘文件也引入绝对路径
