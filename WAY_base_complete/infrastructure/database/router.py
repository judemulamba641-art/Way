from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DatabaseRouter:
    """
    Central database router.

    Supports:
        - default database
        - read/write split
        - analytics database
        - future sharding
        - migrations routing
    """

    DEFAULT_DB = "default"

    READ_REPLICA_DB = None
    ANALYTICS_DB = "analytics"

    APP_LABEL_MAPPING: dict[str, str] = {
        # Example:
        # "analytics": "analytics",
    }

    def db_for_read(
        self,
        model,
        **hints: Any,
    ) -> str | None:
        """
        Route read operations.
        """
        app_label = model._meta.app_label

        if app_label in self.APP_LABEL_MAPPING:
            return self.APP_LABEL_MAPPING[app_label]

        if self.READ_REPLICA_DB:
            return self.READ_REPLICA_DB

        return self.DEFAULT_DB

    def db_for_write(
        self,
        model,
        **hints: Any,
    ) -> str | None:
        """
        Route write operations.
        """
        app_label = model._meta.app_label

        if app_label in self.APP_LABEL_MAPPING:
            return self.APP_LABEL_MAPPING[app_label]

        return self.DEFAULT_DB

    def allow_relation(
        self,
        obj1,
        obj2,
        **hints: Any,
    ) -> bool | None:
        """
        Allow relations across managed DBs.
        """
        db_list = {
            self.DEFAULT_DB,
            self.READ_REPLICA_DB,
            self.ANALYTICS_DB,
        }

        if (
            obj1._state.db in db_list
            and obj2._state.db in db_list
        ):
            return True

        return None

    def allow_migrate(
        self,
        db: str,
        app_label: str,
        model_name: str | None = None,
        **hints: Any,
    ) -> bool | None:
        """
        Control migrations routing.
        """

        mapped_db = self.APP_LABEL_MAPPING.get(
            app_label,
        )

        if mapped_db:
            return db == mapped_db

        if db == self.ANALYTICS_DB:
            return False

        return db == self.DEFAULT_DB