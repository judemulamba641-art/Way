from __future__ import annotations

import logging
from typing import Any

from celery import Celery
from celery.result import AsyncResult
from django.conf import settings

logger = logging.getLogger(__name__)


class CeleryManager:
    """
    Central Celery manager.

    Used by:
        - async tasks
        - background jobs
        - scheduled jobs
        - workers
        - retries
    """

    _app: Celery | None = None

    @classmethod
    def app(cls) -> Celery:
        """
        Return singleton Celery app.
        """
        if cls._app is None:
            logger.info(
                "Initializing Celery manager",
            )

            app = Celery(
                settings.APP_NAME.lower(),
                broker=settings.CELERY_BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND,
            )

            app.conf.update(
                task_default_queue=settings.CELERY_DEFAULT_QUEUE,
                result_expires=settings.CELERY_RESULT_EXPIRES,
                worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
                worker_max_tasks_per_child=settings.CELERY_MAX_TASKS_PER_CHILD,
                broker_transport_options={
                    "visibility_timeout": (
                        settings.CELERY_VISIBILITY_TIMEOUT
                    ),
                },
                task_track_started=True,
                task_acks_late=True,
                task_ignore_result=False,
                timezone="UTC",
                enable_utc=True,
            )

            app.autodiscover_tasks()

            cls._app = app

        return cls._app

    @classmethod
    def delay(
        cls,
        task_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Send task immediately.
        """
        try:
            task = cls.app().send_task(
                task_name,
                args=args,
                kwargs=kwargs,
            )

            logger.info(
                "Celery task dispatched",
                extra={
                    "task": task_name,
                    "task_id": task.id,
                },
            )

            return task

        except Exception:
            logger.exception(
                "Celery dispatch failed",
                extra={
                    "task": task_name,
                },
            )
            raise

    @classmethod
    def apply_async(
        cls,
        task_name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        countdown: int | None = None,
        eta=None,
        queue: str | None = None,
    ):
        """
        Schedule task.
        """
        try:
            task = cls.app().send_task(
                task_name,
                args=args or [],
                kwargs=kwargs or {},
                countdown=countdown,
                eta=eta,
                queue=queue,
            )

            logger.info(
                "Celery task scheduled",
                extra={
                    "task": task_name,
                    "task_id": task.id,
                },
            )

            return task

        except Exception:
            logger.exception(
                "Celery scheduling failed",
                extra={
                    "task": task_name,
                },
            )
            raise

    @classmethod
    def result(
        cls,
        task_id: str,
    ) -> AsyncResult:
        """
        Fetch task result.
        """
        return AsyncResult(
            task_id,
            app=cls.app(),
        )

    @classmethod
    def revoke(
        cls,
        task_id: str,
        terminate: bool = False,
    ) -> None:
        """
        Cancel task.
        """
        try:
            cls.app().control.revoke(
                task_id,
                terminate=terminate,
            )

            logger.info(
                "Celery task revoked",
                extra={
                    "task_id": task_id,
                },
            )

        except Exception:
            logger.exception(
                "Celery revoke failed",
                extra={
                    "task_id": task_id,
                },
            )
            raise

    @classmethod
    def ping(cls) -> bool:
        """
        Worker health.
        """
        try:
            inspect = cls.app().control.inspect()

            workers = inspect.ping()

            return bool(workers)

        except Exception:
            logger.exception(
                "Celery ping failed",
            )
            return False