from settings import *

# make tests faster
SOUTH_TESTS_MIGRATE = False

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

LOGGING["loggers"]["django.db.backends"] = {
    "level": "WARN",
    'handlers': ['rainbow'],
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'