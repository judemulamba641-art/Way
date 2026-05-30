from __future__ import annotations

import logging
import os
import time
from typing import Any

from celery import Celery
from celery.signals import (
    after_setup_logger,
    after_setup_task_logger,
    task_failure,
    task_postrun,
    task_prerun,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "way.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from way.config import configure_logging  # noqa: E402
from way.logging import set_log_context  # noqa: E402


# ---------------------------------------------------------
# Logging bootstrap
# ---------------------------------------------------------
configure_logging()
set_log_context(service="celery")

logger = logging.getLogger("way.celery")


# ---------------------------------------------------------
# Celery app
# ---------------------------------------------------------
celery_app = Celery(
    getattr(settings, "APP_NAME", "way")
    .lower()
    .replace(" ", "_")
)

celery_app.config_from_object("django.conf:settings", namespace="CELERY")


# ---------------------------------------------------------
# Core configuration (stable production baseline)
# ---------------------------------------------------------
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    enable_utc=True,
    timezone=settings.TIME_ZONE,

    task_acks_late=True,
    task_track_started=True,
    task_reject_on_worker_lost=True,

    worker_prefetch_multiplier=1,
    worker_send_task_events=True,

    broker_connection_retry_on_startup=True,

    task_default_queue=settings.CELERY_DEFAULT_QUEUE,
    task_default_exchange=settings.CELERY_DEFAULT_QUEUE,
    task_default_routing_key=settings.CELERY_DEFAULT_QUEUE,

    result_expires=settings.CELERY_RESULT_EXPIRES,

    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    worker_max_tasks_per_child=settings.CELERY_MAX_TASKS_PER_CHILD,

    task_send_sent_event=True,

    broker_transport_options={
        "visibility_timeout": settings.CELERY_VISIBILITY_TIMEOUT,
    },

    task_routes={
        "notifications.*": {"queue": "notifications"},
        "emails.*": {"queue": "emails"},
        "analytics.*": {"queue": "analytics"},
        "media.*": {"queue": "media"},
        "way.system.*": {"queue": "system"},
    },

    beat_schedule=getattr(settings, "CELERY_BEAT_SCHEDULE", {}),
)


celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)


# ---------------------------------------------------------
# Helpers (clean logging abstraction)
# ---------------------------------------------------------
def log_task(event: str, task_id: str | None, task: Any = None, extra: dict | None = None):
    logger.info(
        event,
        extra={
            "task_id": task_id,
            "task_name": getattr(task, "name", None),
            **(extra or {}),
        },
    )


# ---------------------------------------------------------
# Logger setup hooks
# ---------------------------------------------------------
@after_setup_logger.connect
def setup_celery_logger(*args, **kwargs):
    logger.info("Celery worker logger initialized")


@after_setup_task_logger.connect
def setup_task_logger(*args, **kwargs):
    logger.info("Celery task logger initialized")


# ---------------------------------------------------------
# Task lifecycle tracking
# ---------------------------------------------------------
@task_prerun.connect
def on_task_prerun(task_id=None, task=None, **kwargs):
    set_log_context(
        service="celery",
        task_id=task_id,
        task_name=getattr(task, "name", None),
    )

    task._start_time = time.time() if task else None

    log_task("task_started", task_id, task)


@task_postrun.connect
def on_task_postrun(task_id=None, task=None, state=None, **kwargs):
    duration = None

    if task and hasattr(task, "_start_time"):
        duration = round(time.time() - task._start_time, 4)

    log_task(
        "task_completed",
        task_id,
        task,
        extra={
            "state": state,
            "duration_seconds": duration,
        },
    )


@task_failure.connect
def on_task_failure(task_id=None, exception=None, sender=None, traceback=None, **kwargs):
    log_task(
        "task_failed",
        task_id,
        sender,
        extra={
            "error": str(exception),
            "exception_type": exception.__class__.__name__ if exception else None,
        },
    )


# ---------------------------------------------------------
# Health check task
# ---------------------------------------------------------
@celery_app.task(bind=True, name="way.system.heartbeat")
def heartbeat(self):
    return {
        "status": "ok",
        "worker": self.request.hostname,
    }


# ---------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------
if __name__ == "__main__":
    celery_app.start()