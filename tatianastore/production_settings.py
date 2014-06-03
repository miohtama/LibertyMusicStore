from tatianastore.settings import *
DEBUG = False
LOGGING["loggers"][""]["level"] = "WARN"
LOGGING["loggers"][""]["handlers"] = ["file"]

EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"