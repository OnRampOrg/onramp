"""
Django settings for ui project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

# throw some error here 
import os
import logging.config

#Fix for chrome not loading all static files
#from django.core.servers.basehttp import WSGIServer
#WSGIServer.request_queue_size = 20

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = '/home/nick/Desktop/onramp/server/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y#_d-xefmw+$-9t!(!)oe5d_e&b69a28c$4vhuwyrns%wj-$2d'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ui.admin',
    'ui.public'
    # 'ui.static'
    # 'django.contrib.contenttypes.models.ContentType'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
    # 'django.contrib.contenttypes',
]

ROOT_URLCONF = 'ui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '{}/ui/static/templates/'.format(BASE_DIR)
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ui.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django',
        'USER': 'onramp',
        'PASSWORD': 'OnRamp_16',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

AUTHENTICATION_BACKENDS = ('ui.authentication.OnRampAuthenticator',)

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = BASE_DIR + 'ui/static/'
STATICFILES_DIRS = [
    BASE_DIR + '/ui/static/',
]
STATIC_URL = '/static/'

########### Uncomment the following for DEBUG only #############
DEBUG = True


LOGGING = None
logging.config.dictConfig({
   'version': 1,
   'disable_existing_loggers': False,
   'formatters': {
       'console': {
           'format': '%(asctime)-15s %(levelname)-3s %(module)s: %(message)s',
       },
   },
   'handlers': {
       'console': {
           'class': 'logging.StreamHandler',
           'formatter': 'console',
       },
   },
   'loggers': {
       '': {
           'level': 'DEBUG',
           'handlers': ['console'],
       },
   },
})