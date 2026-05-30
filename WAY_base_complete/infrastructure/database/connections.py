from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.db import connection
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class DatabaseConnections:
    """
    Central database connection manager.

    Used by:
        - health checks
        - startup checks
        - services
        - Celery workers
        - admin monitoring
    """

    @staticmethod
    def aliases() -> list[str]:
        """
        Return configured database aliases.
        """
        return list(connections.databases.keys())

    @staticmethod
    def default_alias() -> str:
        """
        Return default database alias.
        """
        return "default"

    @classmethod
    def get(
        cls,
        alias: str | None = None,
    ):
        """
        Return a Django database connection.
        """
        db_alias = alias or cls.default_alias()

        return connections[db_alias]

    @classmethod
    def cursor(
        cls,
        alias: str | None = None,
    ):
        """
        Return DB cursor.
        """
        db = cls.get(alias)

        return db.cursor()

    @classmethod
    def ensure(
        cls,
        alias: str | None = None,
    ) -> bool:
        """
        Ensure DB connection is alive.
        """
        db_alias = alias or cls.default_alias()

        try:
            db = cls.get(db_alias)

            db.ensure_connection()

            return True

        except OperationalError:
            logger.exception(
                "Database ensure_connection failed",
                extra={
                    "database": db_alias,
                },
            )
            return False

    @classmethod
    def health(
        cls,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform health check.
        """
        db_alias = alias or cls.default_alias()

        try:
            db = cls.get(db_alias)

            with db.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()

            return {
                "alias": db_alias,
                "healthy": True,
                "vendor": db.vendor,
            }

        except Exception:
            logger.exception(
                "Database health check failed",
                extra={
                    "database": db_alias,
                },
            )

            return {
                "alias": db_alias,
                "healthy": False,
            }

    @classmethod
    def health_all(cls) -> dict[str, Any]:
        """
        Health check for all databases.
        """
        results: dict[str, Any] = {}

        for alias in cls.aliases():
            results[alias] = cls.health(alias)

        return results

    @classmethod
    def close(
        cls,
        alias: str | None = None,
    ) -> None:
        """
        Close a specific DB connection.
        """
        db_alias = alias or cls.default_alias()

        try:
            cls.get(db_alias).close()

        except Exception:
            logger.exception(
                "Database close failed",
                extra={
                    "database": db_alias,
                },
            )

    @classmethod
    def close_all(cls) -> None:
        """
        Close every DB connection.
        """
        try:
            connections.close_all()

        except Exception:
            logger.exception(
                "Database close_all failed",
            )

    @classmethod
    def info(
        cls,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """
        Return database metadata.
        """
        db_alias = alias or cls.default_alias()

        config = settings.DATABASES.get(
            db_alias,
            {},
        )

        return {
            "alias": db_alias,
            "engine": config.get("ENGINE"),
            "name": config.get("NAME"),
            "host": config.get("HOST"),
            "port": config.get("PORT"),
        }