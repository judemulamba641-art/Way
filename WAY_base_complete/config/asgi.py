from __future__ import annotations

import logging
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from way.config import configure_logging, settings
from way.channels import websocket_urlpatterns

# ---------------------------------------------------------
# Django bootstrap
# ---------------------------------------------------------
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "way.settings",
)

# ---------------------------------------------------------
# Logging bootstrap
# ---------------------------------------------------------
configure_logging()

logger = logging.getLogger(__name__)

logger.info(
    "WAY ASGI booting",
    extra={
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
    },
)

# ---------------------------------------------------------
# Django HTTP app (DRF + admin + auth)
# ---------------------------------------------------------
django_asgi_app = get_asgi_application()

# ---------------------------------------------------------
# Root ASGI router
# ---------------------------------------------------------
application = ProtocolTypeRouter(
    {
        # ---------------------------------------------
        # DRF / Django routes
        # ---------------------------------------------
        "http": django_asgi_app,

        # ---------------------------------------------
        # WebSockets / Channels
        # ---------------------------------------------
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns,
            ),
        ),
    }
)

# ---------------------------------------------------------
# Startup log
# ---------------------------------------------------------
logger.info(
    "WAY ASGI ready",
    extra={
        "debug": settings.DEBUG,
    },
)