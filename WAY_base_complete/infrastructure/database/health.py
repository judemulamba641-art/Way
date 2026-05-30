from __future__ import annotations

import logging
from typing import Any

from .connections import DatabaseConnections

logger = logging.getLogger(__name__)


class DatabaseHealth:
    """
    Database health service.

    Used by:
        - readiness checks
        - liveness checks
        - startup validation
        - monitoring
        - admin dashboards
    """

    @classmethod
    def check(
        cls,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """
        Health check for one database.
        """
        result = DatabaseConnections.health(alias)

        if not result.get("healthy"):
            logger.warning(
                "Database unhealthy",
                extra={
                    "database": result.get("alias"),
                },
            )

        return result

    @classmethod
    def check_all(cls) -> dict[str, Any]:
        """
        Health check for every configured database.
        """
        results = DatabaseConnections.health_all()

        healthy = all(
            item.get("healthy", False)
            for item in results.values()
        )

        return {
            "healthy": healthy,
            "databases": results,
        }

    @classmethod
    def readiness(cls) -> dict[str, Any]:
        """
        Kubernetes / deployment readiness.
        """
        report = cls.check_all()

        return {
            "service": "database",
            "ready": report["healthy"],
            "details": report["databases"],
        }

    @classmethod
    def liveness(cls) -> dict[str, Any]:
        """
        Lightweight process liveness.
        """
        return {
            "service": "database",
            "alive": True,
        }

    @classmethod
    def startup(cls) -> bool:
        """
        Startup validation.
        """
        report = cls.check_all()

        if report["healthy"]:
            logger.info(
                "Database startup validation passed",
            )
            return True

        logger.error(
            "Database startup validation failed",
            extra={
                "databases": report["databases"],
            },
        )

        return False