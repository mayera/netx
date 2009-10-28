# Django settings for hutest project.

import os

def BASE_REL(path):
    return os.path.abspath(os.path.join(os.path.dirname("__file__"), path))

BASE_DIR=BASE_REL(".")

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London GB GB-Eire'

#BASE_DIR="/home/mayera/Projects/Hongwu/human"
#BASE_DIR="c:/human"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# This directory is where the uploaded graphs should be stored.
# For production it should be changed to somewhere more practical.
GRAPH_DIR="/tmp/graphs/"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
#STATIC_PATH = 'C:/python25/lib/site-packages/django/human/maps'
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = BASE_REL('media')
NXGRAPHPATH = os.path.join(MEDIA_ROOT, "nets", "test.adjlist")
CANVIZGRAPHPATH = os.path.join(MEDIA_ROOT, "nets", "livenet.xdot")

#/path/to/media to use for static files like css; using the same path as 
#ADMIN_MEDIA_PREFIX (which defaults to /media/) will overwrite URLconf entry 
#STATIC_DOC_ROOT = '/home/mayera/Projects/Hongwu/human/nets/media' 

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-f@xsf@!smzo9b1kfrgo9dejy=1xxb&34kqco6reeqdv69-nsa'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'human.urls'

TEMPLATE_DIRS = (
    BASE_REL('templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth', #the first five of these commented out if testing the effect of this, given lack of db
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
#    'django.contrib.databrowse',
#    'human.ehmn',
#    'human.igem',
#    'human.task',
#    'human.tb',
    'human.nets',
)

try:
    from local_settings import *
except ImportError, exp:
    pass
