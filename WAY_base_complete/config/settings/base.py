from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------
BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent.parent
)


# ---------------------------------------------------------
# APP METADATA
# ---------------------------------------------------------
APP_NAME = "WAY"

APP_ENV = "development"

APP_VERSION = "0.1.0"


# ---------------------------------------------------------
# SECURITY CORE
# ---------------------------------------------------------
SECRET_KEY = "CHANGE_ME_IN_ENV"

DEBUG = False

ALLOWED_HOSTS = []

CSRF_TRUSTED_ORIGINS = []

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

USE_X_FORWARDED_HOST = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"


# ---------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "channels",
]

LOCAL_APPS = [
    "way",
]

INSTALLED_APPS = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
)


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "infrastructure.security.middleware.FirewallMiddleware",

    "infrastructure.security.middleware.RateLimitMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "infrastructure.security.middleware.SecurityHeadersMiddleware",
]


# ---------------------------------------------------------
# URL / WSGI / ASGI
# ---------------------------------------------------------
ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = (
    "config.wsgi.application"
)

ASGI_APPLICATION = (
    "config.asgi.application"
)


# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends."
            "django.DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template."
                    "context_processors.request"
                ),
                (
                    "django.contrib.auth."
                    "context_processors.auth"
                ),
                (
                    "django.contrib.messages."
                    "context_processors.messages"
                ),
            ],
        },
    },
]


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.sqlite3"
        ),
        "NAME": (
            BASE_DIR
            / "db.sqlite3"
        ),
    }
}


# ---------------------------------------------------------
# CACHE / REDIS
# ---------------------------------------------------------
REDIS_HOST = "127.0.0.1"

REDIS_PORT = 6379

REDIS_URL = (
    f"redis://"
    f"{REDIS_HOST}:"
    f"{REDIS_PORT}"
)

CACHES = {
    "default": {
        "BACKEND": (
            "django.core.cache."
            "backends.redis.RedisCache"
        ),
        "LOCATION": (
            f"{REDIS_URL}/2"
        ),
        "TIMEOUT": 300,
        "OPTIONS": {
            "CLIENT_CLASS": (
                "django_redis.client."
                "DefaultClient"
            ),
        },
    }
}


# ---------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "NumericPasswordValidator"
        )
    },
]


# ---------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------
TIME_ZONE = "Africa/Kinshasa"

USE_TZ = True

USE_I18N = True

USE_L10N = True


# ---------------------------------------------------------
# LANGUAGE
# ---------------------------------------------------------
LANGUAGE_CODE = "en-us"

LANGUAGES = [
    ("en", "English"),
    ("fr", "French"),
]


# ---------------------------------------------------------
# STATIC
# ---------------------------------------------------------
STATIC_URL = "/static/"


# ---------------------------------------------------------
# DEFAULT AUTO FIELD
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# ---------------------------------------------------------
# CELERY
# ---------------------------------------------------------
CELERY_BROKER_URL = (
    f"{REDIS_URL}/0"
)

CELERY_RESULT_BACKEND = (
    f"{REDIS_URL}/1"
)

CELERY_DEFAULT_QUEUE = (
    "default"
)

CELERY_RESULT_EXPIRES = 3600

CELERY_WORKER_CONCURRENCY = 4

CELERY_MAX_TASKS_PER_CHILD = 1000

CELERY_VISIBILITY_TIMEOUT = 3600


# ---------------------------------------------------------
# CHANNELS
# ---------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": (
            "channels_redis.core."
            "RedisChannelLayer"
        ),
        "CONFIG": {
            "hosts": [
                (
                    REDIS_HOST,
                    REDIS_PORT,
                ),
            ],
        },
    }
}


# ---------------------------------------------------------
# FIREWALL
# ---------------------------------------------------------
WAY_FIREWALL = {
    "ALLOWED_IPS": [],

    "BLOCKED_IPS": [],

    "BLOCKED_AGENTS": [
        "masscan",
        "nmap",
        "sqlmap",
    ],
}


# ---------------------------------------------------------
# RATE LIMIT
# ---------------------------------------------------------
WAY_RATE_LIMIT = {
    "WINDOW_SECONDS": 60,

    "MAX_REQUESTS": 120,

    "BLOCK_SECONDS": 300,

    "WHITELIST_IPS": [
        "127.0.0.1",
    ],

    "PATH_RULES": {
        "/health/": {
            "WINDOW_SECONDS": 60,
            "MAX_REQUESTS": 1000,
            "BLOCK_SECONDS": 0,
        },

        "/admin/": {
            "WINDOW_SECONDS": 60,
            "MAX_REQUESTS": 20,
            "BLOCK_SECONDS": 600,
        },

        "/api/auth/": {
            "WINDOW_SECONDS": 60,
            "MAX_REQUESTS": 10,
            "BLOCK_SECONDS": 900,
        },

        "/ws/": {
            "WINDOW_SECONDS": 60,
            "MAX_REQUESTS": 300,
            "BLOCK_SECONDS": 120,
        },
    },
}


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------
LOG_LEVEL = "INFO"

LOGGING = {
    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s "
                "[%(levelname)s] "
                "%(name)s :: "
                "%(message)s"
            ),
        },
    },

    "handlers": {
        "console": {
            "class": (
                "logging.StreamHandler"
            ),
            "formatter": (
                "standard"
            ),
        },
    },

    "loggers": {
        "infrastructure": {
            "handlers": [
                "console"
            ],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        "way": {
            "handlers": [
                "console"
            ],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}