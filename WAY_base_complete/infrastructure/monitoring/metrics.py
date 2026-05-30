from __future__ import annotations

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Central infrastructure metrics collector.

    Used by:
        - Django requests
        - Celery workers
        - Channels
        - internal services
        - admin dashboards
        - future Prometheus exporters
    """

    _counters: dict[str, int] = defaultdict(int)
    _timers: dict[str, list[float]] = defaultdict(list)
    _gauges: dict[str, Any] = {}

    @classmethod
    def increment(
        cls,
        name: str,
        value: int = 1,
    ) -> None:
        """
        Increment metric counter.
        """
        cls._counters[name] += value

    @classmethod
    def decrement(
        cls,
        name: str,
        value: int = 1,
    ) -> None:
        """
        Decrement metric counter.
        """
        cls._counters[name] -= value

    @classmethod
    def gauge(
        cls,
        name: str,
        value: Any,
    ) -> None:
        """
        Set live gauge.
        """
        cls._gauges[name] = value

    @classmethod
    def timing(
        cls,
        name: str,
        duration: float,
    ) -> None:
        """
        Record timing.
        """
        cls._timers[name].append(duration)

    @classmethod
    @contextmanager
    def track(
        cls,
        name: str,
    ):
        """
        Measure execution time.

        Example:
            with MetricsCollector.track("db.query"):
                ...
        """
        started = time.perf_counter()

        try:
            yield

        finally:
            duration = (
                time.perf_counter() - started
            )

            cls.timing(
                name,
                duration,
            )

    @classmethod
    def wrap(
        cls,
        name: str,
    ) -> Callable:
        """
        Decorator timing helper.
        """

        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                with cls.track(name):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def summary(cls) -> dict[str, Any]:
        """
        Metrics snapshot.
        """
        timings: dict[str, Any] = {}

        for key, values in cls._timers.items():
            if not values:
                continue

            timings[key] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

        return {
            "counters": dict(cls._counters),
            "gauges": dict(cls._gauges),
            "timings": timings,
        }

    @classmethod
    def reset(cls) -> None:
        """
        Reset all metrics.
        """
        cls._counters.clear()
        cls._timers.clear()
        cls._gauges.clear()

    @classmethod
    def export(cls) -> dict[str, Any]:
        """
        Export metrics.
        """
        return cls.summary()

    @classmethod
    def log(cls) -> None:
        """
        Log metrics snapshot.
        """
        logger.info(
            "Infrastructure metrics snapshot",
            extra={
                "metrics": cls.summary(),
            },
        )