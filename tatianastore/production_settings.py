import logging

from tatianastore.settings import *

ALLOWED_HOSTS = ["libertymusicstore.net", "upload.libertymusicstore.net"]

DEBUG = False
LOGGING["loggers"][""]["level"] = "WARN"
LOGGING["loggers"][""]["handlers"] = ["file"]

EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

# List of callables that know how to import templates from various sources.
#TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
#        'django.template.loaders.filesystem.Loader',
#        'django.template.loaders.app_directories.Loader',
#    )),
#)

LOGGING["loggers"][""]["handlers"] = ["file"]
LOGGING["loggers"][""]["level"] = "INFO"
