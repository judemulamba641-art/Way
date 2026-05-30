from .base import *

DEBUG = False

APP_ENV = "production"

ALLOWED_HOSTS = [
    "your-domain.com",
]


# ---------------------------------------------------------
# DATABASE PROD
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "way_db",
        "USER": "way_user",
        "PASSWORD": "CHANGE_ME",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


# ---------------------------------------------------------
# SECURITY HARDENING
# ---------------------------------------------------------
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# ---------------------------------------------------------
# LOGGING PROD
# ---------------------------------------------------------
LOG_LEVEL = "INFO"


# ---------------------------------------------------------
# CHANNELS REDIS (prod-ready)
# ---------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    }
}