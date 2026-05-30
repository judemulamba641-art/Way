from __future__ import annotations

import json
import logging
import logging.config
import socket
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from django.conf import settings as django_settings


# ---------------------------------------------------------
# Safe settings access (avoid circular imports)
# ---------------------------------------------------------
def get_setting(name: str, default=None):
    return getattr(django_settings, name, default)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
BASE_DIR = Path(get_setting("BASE_DIR", Path.cwd()))
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Runtime metadata
# ---------------------------------------------------------
HOSTNAME = socket.gethostname()
ENVIRONMENT = get_setting("APP_ENV", "development")
APP_NAME = get_setting("APP_NAME", "way")
DEBUG = get_setting("DEBUG", False)
LOG_LEVEL = get_setting("LOG_LEVEL", "INFO")


# ---------------------------------------------------------
# Context storage (request_id / task_id / etc.)
# ---------------------------------------------------------
_log_context = threading.local()


def set_log_context(**kwargs):
    """
    Used by:
    - Django middleware (request_id)
    - Celery tasks (task_id)
    - Channels events
    """
    _log_context.data = kwargs


def get_log_context() -> dict:
    return getattr(_log_context, "data", {})


# ---------------------------------------------------------
# JSON Formatter (production structured logs)
# ---------------------------------------------------------
class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "hostname": HOSTNAME,
            "environment": ENVIRONMENT,
            "app": APP_NAME,
        }

        # Exception support
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Standard extras (Celery / HTTP / Channels)
        extras = [
            "task_id",
            "task_name",
            "request_id",
            "user_id",
            "path",
            "method",
            "ip",
            "user_agent",
            "service",
        ]

        for key in extras:
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        # Thread / context propagation
        payload.update(get_log_context())

        return json.dumps(payload, default=str)


# ---------------------------------------------------------
# Dev formatter
# ---------------------------------------------------------
DEV_FORMAT = "[%(asctime)s] %(levelname)s %(name)s :: %(message)s"


def get_formatter_name() -> str:
    return "console" if DEBUG else "json"


# ---------------------------------------------------------
# Prevent double configuration
# ---------------------------------------------------------
_LOGGING_CONFIGURED = False


def configure_logging() -> None:
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    _LOGGING_CONFIGURED = True
    logging.config.dictConfig(LOGGING)


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console": {"format": DEV_FORMAT},
        "json": {"()": "way.logging.JSONFormatter"},
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": get_formatter_name(),
        },

        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "when": "midnight",
            "backupCount": 30,
            "formatter": "json",
            "encoding": "utf-8",
        },

        "errors": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "errors.log"),
            "when": "midnight",
            "backupCount": 30,
            "formatter": "json",
            "level": "ERROR",
            "encoding": "utf-8",
        },
    },

    "root": {
        "handlers": ["console", "file", "errors"],
        "level": LOG_LEVEL,
    },

    "loggers": {
        # Django core
        "django": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        "django.request": {
            "handlers": ["console", "errors"],
            "level": "ERROR",
            "propagate": False,
        },

        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "WARNING",
            "propagate": False,
        },

        # API layer
        "rest_framework": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        # Channels (WebSocket)
        "channels": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        # Celery (background tasks)
        "celery": {
            "handlers": ["console", "file", "errors"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        # ASGI servers
        "uvicorn": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        "daphne": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        # Infra
        "redis": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },

        # Project root logger
        "way": {
            "handlers": ["console", "file", "errors"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}