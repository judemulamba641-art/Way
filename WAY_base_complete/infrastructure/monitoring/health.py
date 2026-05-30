from __future__ import annotations

import logging
from typing import Any

from way.infrastructure.cache import RedisCache
from way.infrastructure.database import DatabaseConnections
from way.infrastructure.messaging import CeleryManager
from way.infrastructure.messaging import ChannelManager
from way.infrastructure.messaging import MessageBroker

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Global infrastructure health monitor.

    Used by:
        - readiness endpoint
        - liveness endpoint
        - deployment checks
        - startup validation
        - admin dashboards
    """

    @classmethod
    async def cache(cls) -> dict[str, Any]:
        """
        Redis cache health.
        """
        healthy = await RedisCache().ping()

        return {
            "service": "cache",
            "healthy": healthy,
        }

    @classmethod
    def database(cls) -> dict[str, Any]:
        """
        Database health.
        """
        databases = DatabaseConnections.health_all()

        healthy = all(
            item.get("healthy", False)
            for item in databases.values()
        )

        return {
            "service": "database",
            "healthy": healthy,
            "details": databases,
        }

    @classmethod
    async def broker(cls) -> dict[str, Any]:
        """
        Message broker health.
        """
        healthy = await MessageBroker().ping()

        return {
            "service": "broker",
            "healthy": healthy,
        }

    @classmethod
    def channels(cls) -> dict[str, Any]:
        """
        Channel layer health.
        """
        healthy = ChannelManager.ping()

        return {
            "service": "channels",
            "healthy": healthy,
        }

    @classmethod
    def celery(cls) -> dict[str, Any]:
        """
        Celery workers health.
        """
        healthy = CeleryManager.ping()

        return {
            "service": "celery",
            "healthy": healthy,
        }

    @classmethod
    async def readiness(cls) -> dict[str, Any]:
        """
        Full readiness check.
        """
        report = {
            "database": cls.database(),
            "cache": await cls.cache(),
            "broker": await cls.broker(),
            "channels": cls.channels(),
            "celery": cls.celery(),
        }

        healthy = all(
            item.get("healthy", False)
            for item in report.values()
        )

        return {
            "service": "way",
            "ready": healthy,
            "checks": report,
        }

    @classmethod
    def liveness(cls) -> dict[str, Any]:
        """
        Lightweight liveness.
        """
        return {
            "service": "way",
            "alive": True,
        }

    @classmethod
    async def startup(cls) -> bool:
        """
        Startup validation.
        """
        report = await cls.readiness()

        if report["ready"]:
            logger.info(
                "Infrastructure startup validation passed",
            )
            return True

        logger.error(
            "Infrastructure startup validation failed",
            extra={
                "checks": report["checks"],
            },
        )

        return False