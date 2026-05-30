from __future__ import annotations

import logging
import os

from django.core.wsgi import get_wsgi_application

from way.config import configure_logging, settings
from way.logging import set_log_context


# ---------------------------------------------------------
# Django settings module
# ---------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "way.settings")


# ---------------------------------------------------------
# Logging bootstrap (same strategy as ASGI / Celery)
# ---------------------------------------------------------
configure_logging()

set_log_context(
    service="wsgi",
    app=getattr(settings, "APP_NAME", "way"),
    environment=getattr(settings, "APP_ENV", "development"),
)

logger = logging.getLogger("way.wsgi")


# ---------------------------------------------------------
# WSGI application
# ---------------------------------------------------------
application = get_wsgi_application()


# ---------------------------------------------------------
# Startup log (useful in Gunicorn / uWSGI logs)
# ---------------------------------------------------------
logger.info(
    "WAY WSGI initialized",
    extra={
        "debug": getattr(settings, "DEBUG", False),
        "version": getattr(settings, "APP_VERSION", None),
    },
)