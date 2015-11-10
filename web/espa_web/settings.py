"""
Django settings for espa_web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ConfigParser

#this is the location of the main project directory
#NOT the directory this file lives in!!!
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

#load up the site specific config file.
#If one is not specified default to the user home directory, looking for .cfgno
ESPA_CONFIG_FILE = os.environ.get('ESPA_CONFIG_FILE',
                                  os.path.join(os.path.expanduser('~'),
                                               '.cfgnfo'))

#stop everything if we don't have the config file
if not os.path.exists(ESPA_CONFIG_FILE):
    raise Exception("Espa config file not found at %s... exiting"
                    % ESPA_CONFIG_FILE)

config = ConfigParser.RawConfigParser()

with open(ESPA_CONFIG_FILE) as file_handle:
    config.readfp(file_handle)


# set the ESPA_ENV variable correctly
ESPA_ENV = 'dev'

# ************t*************
# NEVER CHANGE THIS TO ops IN dev OR tst UNLESS THE dev AND tst CRONS ARE OFF
# *************************
if "ESPA_ENV" in os.environ:
    if os.environ['ESPA_ENV'].lower() == 'ops':
        ESPA_ENV = 'ops'
    elif os.environ['ESPA_ENV'].lower() == 'tst':
        ESPA_ENV = 'tst'
    elif os.environ['ESPA_ENV'].lower() == 'dev':
        ESPA_ENV = 'dev'
    else:
        raise Exception("ESPA_ENV set to unknown value:%s... \
            must be one of 'dev', 'tst' or 'ops'... \
            cannot continue" % os.environ['ESPA_ENV'])


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('config', 'key')

# SECURITY WARNING: don't run with debug turned on in production!
#allow us to override this with env var
DEBUG = False
TEMPLATE_DEBUG = False

#make sure its set to a proper value
if os.environ.get('ESPA_DEBUG', '').lower() == 'true':
    DEBUG = True
    TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ordering',
    'console',
    'reports',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

#where do we find the initial set of urls?
ROOT_URLCONF = 'espa_web.urls'

WSGI_APPLICATION = 'espa_web.wsgi.application'

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config.get('config', 'post-db'),
        'USER': config.get('config', 'post-user'),
        'PASSWORD': config.get('config', 'post-pass'),
        'HOST': config.get('config', 'post-host'),
        'PORT': config.get('config', 'post-port'),
        'CONN_MAX_AGE': 30,
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_ROOT = os.path.join(BASE_DIR, 'espa_web', 'static/')
STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'espa_web/templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'espa_web.context_processors.include_external_urls',
                'espa_web.context_processors.scene_stats',
            ],
        },
    },
]

# add the EE Authentication Backend in addition to the ModelBackend
# authentication stops at the first success... so this order does matter
#leave the standard ModelBackend in first so the builtin admin account
#never hits EE
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'espa_web.auth_backends.EEAuthBackend',)

# sets the login_url to the named url action ('login') contained in urls.py
LOGIN_URL = 'login'

# if the user didn't select a ?next parameter (will happen if they are trying
# to access /) then send them to the homepage
LOGIN_REDIRECT_URL = 'index'

# Set up caching for Django.  Everything is pointed to our single memcache
# cluster but each environment is going to separated out with the environment
# value as a key prefix.
if ESPA_ENV is 'dev':
    CACHES = {
    'default': {
        'KEY_PREFIX' : ESPA_ENV,
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'l8srlscp20.cr.usgs.gov:11211',
        ]
    }
}
else:
    CACHES = {
        'default': {
            'KEY_PREFIX' : ESPA_ENV,
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': [
                'l8srlscp20.cr.usgs.gov:11211',
                'l8srlscp21.cr.usgs.gov:11211',
                'l8srlscp22.cr.usgs.gov:11211',
            ]
        }
    }

LOGDIR = os.environ.get('ESPA_LOG_DIR', '/var/log/uwsgi')

try:
    os.makedirs(LOGDIR)
except:
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'espa.standard': {
            'format': ('%(asctime)s.%(msecs)03d %(process)d'
                       ' %(levelname)-8s'
                       ' %(filename)s:%(lineno)d:%(funcName)s'
                       ' -- %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'standard': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'mode': 'a',
            'formatter': 'espa.standard',
            'filename': os.path.join(LOGDIR, 'espa-application.log'),
        },
        'requests': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'mode': 'a',
            'formatter': 'espa.standard',
            'filename': os.path.join(LOGDIR, 'espa-requests.log'),
        },
    },
    'loggers': {
       'django.request': {
            # To be used by django
            'level': 'ERROR',
            'propagate': False,
            'handlers': ['requests'],
        },
        'ordering.auth_backends': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.core': {
            # To be used by the web system
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.emails': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.errors': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.lpdaac': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.lta': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.models.user': {
            # To be used by the web system
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.models.configuration': {
            # To be used by the web system
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.models.order': {
            # To be used by the web system
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.nlaps': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.rpc': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.sensor': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.sshcmd': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.validation': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.validators': {
            'level': 'INFO',
            'propagate':False,
            'handlers': ['standard']
        },
        'ordering.views': {
            # To be used by the web system
            'level': 'INFO',
            'propagate': False,
            'handlers': ['standard']
        },
        'ordering.utilities': {
            'level': 'INFO',
            'propagate':False,
            'handlers': ['standard']
        },
    }
}
