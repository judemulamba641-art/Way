from __future__ import annotations

import math
import statistics
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

from sdk_python.telemetrics.logging import Logger, get_logger

# =========================================================
# metric point
# =========================================================


@dataclass(slots=True)
class MetricPoint:
    name: str
    value: float
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": dict(self.tags),
        }


# =========================================================
# metric base
# =========================================================


class Metric:
    def __init__(
        self,
        name: str,
        *,
        tags: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.name = name
        self.tags = dict(tags or {})
        self._lock = threading.RLock()

    def snapshot(self) -> MetricPoint:
        raise NotImplementedError


# =========================================================
# counter
# =========================================================


class Counter(Metric):
    def __init__(
        self,
        name: str,
        *,
        value: float = 0.0,
        tags: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(name, tags=tags)
        self._value = float(value)

    def increment(self, amount: float = 1.0) -> float:
        with self._lock:
            self._value += amount
            return self._value

    def reset(self) -> None:
        with self._lock:
            self._value = 0.0

    @property
    def value(self) -> float:
        return self._value

    def snapshot(self) -> MetricPoint:
        return MetricPoint(
            name=self.name,
            value=self._value,
            tags=self.tags,
        )


# =========================================================
# gauge
# =========================================================


class Gauge(Metric):
    def __init__(
        self,
        name: str,
        *,
        value: float = 0.0,
        tags: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(name, tags=tags)
        self._value = float(value)

    def set(self, value: float) -> None:
        with self._lock:
            self._value = float(value)

    def increment(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def decrement(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    @property
    def value(self) -> float:
        return self._value

    def snapshot(self) -> MetricPoint:
        return MetricPoint(
            name=self.name,
            value=self._value,
            tags=self.tags,
        )


# =========================================================
# histogram
# =========================================================


class Histogram(Metric):
    def __init__(
        self,
        name: str,
        *,
        tags: Optional[Mapping[str, str]] = None,
    ) -> None:
        super().__init__(name, tags=tags)
        self._values: List[float] = []

    def record(self, value: float) -> None:
        with self._lock:
            self._values.append(float(value))

    @property
    def count(self) -> int:
        return len(self._values)

    @property
    def min(self) -> float:
        return min(self._values) if self._values else 0.0

    @property
    def max(self) -> float:
        return max(self._values) if self._values else 0.0

    @property
    def mean(self) -> float:
        return statistics.mean(self._values) if self._values else 0.0

    @property
    def median(self) -> float:
        return statistics.median(self._values) if self._values else 0.0

    def percentile(self, p: float) -> float:
        if not self._values:
            return 0.0

        values = sorted(self._values)

        index = math.ceil((p / 100) * len(values)) - 1
        index = max(0, min(index, len(values) - 1))

        return values[index]

    def snapshot(self) -> MetricPoint:
        return MetricPoint(
            name=self.name,
            value=self.mean,
            tags=self.tags,
        )

    def summary(self) -> Dict[str, float]:
        return {
            "count": float(self.count),
            "min": self.min,
            "max": self.max,
            "mean": self.mean,
            "median": self.median,
            "p95": self.percentile(95),
            "p99": self.percentile(99),
        }


# =========================================================
# snapshot
# =========================================================


@dataclass(slots=True)
class MetricsSnapshot:
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metrics: List[MetricPoint] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],
        }


# =========================================================
# client
# =========================================================


class MetricsClient:
    def __init__(
        self,
        *,
        logger: Optional[Logger] = None,
    ) -> None:
        self._logger = logger or get_logger()

        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}

        self._lock = threading.RLock()

    # -------------------------------------------------
    # create / get
    # -------------------------------------------------

    def counter(
        self,
        name: str,
        **tags: str,
    ) -> Counter:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(
                    name,
                    tags=tags,
                )
                self._logger.debug(
                    "metric counter created",
                    metric=name,
                )

            return self._counters[name]

    def gauge(
        self,
        name: str,
        **tags: str,
    ) -> Gauge:
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(
                    name,
                    tags=tags,
                )
                self._logger.debug(
                    "metric gauge created",
                    metric=name,
                )

            return self._gauges[name]

    def histogram(
        self,
        name: str,
        **tags: str,
    ) -> Histogram:
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(
                    name,
                    tags=tags,
                )
                self._logger.debug(
                    "metric histogram created",
                    metric=name,
                )

            return self._histograms[name]

    # -------------------------------------------------
    # helpers
    # -------------------------------------------------

    def increment(
        self,
        name: str,
        amount: float = 1.0,
        **tags: str,
    ) -> None:
        self.counter(name, **tags).increment(amount)

    def gauge_set(
        self,
        name: str,
        value: float,
        **tags: str,
    ) -> None:
        self.gauge(name, **tags).set(value)

    def record(
        self,
        name: str,
        value: float,
        **tags: str,
    ) -> None:
        self.histogram(name, **tags).record(value)

    # -------------------------------------------------
    # export
    # -------------------------------------------------

    def snapshot(self) -> MetricsSnapshot:
        metrics: List[MetricPoint] = []

        with self._lock:
            for metric in self._counters.values():
                metrics.append(metric.snapshot())

            for metric in self._gauges.values():
                metrics.append(metric.snapshot())

            for metric in self._histograms.values():
                metrics.append(metric.snapshot())

        return MetricsSnapshot(metrics=metrics)

    def export(self) -> Dict[str, Any]:
        return self.snapshot().to_dict()

    # -------------------------------------------------
    # async
    # -------------------------------------------------

    async def aincrement(
        self,
        name: str,
        amount: float = 1.0,
        **tags: str,
    ) -> None:
        self.increment(name, amount, **tags)

    async def agauge_set(
        self,
        name: str,
        value: float,
        **tags: str,
    ) -> None:
        self.gauge_set(name, value, **tags)

    async def arecord(
        self,
        name: str,
        value: float,
        **tags: str,
    ) -> None:
        self.record(name, value, **tags)