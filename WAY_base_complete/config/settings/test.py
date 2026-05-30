from __future__ import annotations

from .base import *


# ---------------------------------------------------------
# TEST MODE
# ---------------------------------------------------------
DEBUG = False

ALLOWED_HOSTS = ["testserver"]


# ---------------------------------------------------------
# DATABASE (in-memory for speed)
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# ---------------------------------------------------------
# PASSWORD HASHING (fast tests)
# ---------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# ---------------------------------------------------------
# CELERY (disable broker, run synchronously)
# ---------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# ---------------------------------------------------------
# CHANNELS (in-memory layer for tests)
# ---------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


# ---------------------------------------------------------
# EMAIL (no external call)
# ---------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


# ---------------------------------------------------------
# CACHE (disable external dependencies)
# ---------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# ---------------------------------------------------------
# LOGGING (minimal noise for tests)
# ---------------------------------------------------------
LOG_LEVEL = "WARNING"


# ---------------------------------------------------------
# SECURITY RELAXED FOR TESTS
# ---------------------------------------------------------
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# ---------------------------------------------------------
# TIMEZONE (stable for reproducibility)
# ---------------------------------------------------------
TIME_ZONE = "UTC"
USE_TZ = True