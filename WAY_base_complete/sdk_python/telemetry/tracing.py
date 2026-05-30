from __future__ import annotations

import asyncio
import threading
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Mapping, Optional

from sdk_python.telemetrics.logging import Logger, get_logger
from sdk_python.telemetrics.metrics import MetricsClient


# =========================================================
# enums
# =========================================================


class SpanKind(str, Enum):
    INTERNAL = "internal"
    CLIENT = "client"
    SERVER = "server"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    CANCELLED = "cancelled"


# =========================================================
# trace context
# =========================================================


@dataclass(slots=True)
class TraceContext:
    trace_id: str = field(
        default_factory=lambda: uuid.uuid4().hex
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
        }


@dataclass(slots=True)
class SpanContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None

    @classmethod
    def create(
        cls,
        *,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ) -> "SpanContext":
        return cls(
            trace_id=trace_id or uuid.uuid4().hex,
            span_id=uuid.uuid4().hex,
            parent_span_id=parent_span_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }

        if self.parent_span_id:
            payload["parent_span_id"] = self.parent_span_id

        return payload


# =========================================================
# event
# =========================================================


@dataclass(slots=True)
class SpanEvent:
    name: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    attributes: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "attributes": dict(self.attributes),
        }


# =========================================================
# span
# =========================================================


@dataclass(slots=True)
class Span:
    name: str
    context: SpanContext
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.OK

    attributes: Dict[str, Any] = field(
        default_factory=dict
    )

    events: List[SpanEvent] = field(
        default_factory=list
    )

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    ended_at: Optional[datetime] = None

    _started_perf: float = field(
        default_factory=time.perf_counter
    )

    _duration_ms: Optional[float] = None

    @property
    def duration_ms(self) -> float:
        if self._duration_ms is None:
            return 0.0

        return self._duration_ms

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.attributes[key] = value

    def add_event(
        self,
        name: str,
        **attributes: Any,
    ) -> None:
        self.events.append(
            SpanEvent(
                name=name,
                attributes=attributes,
            )
        )

    def finish(
        self,
        *,
        status: SpanStatus = SpanStatus.OK,
    ) -> None:
        self.status = status
        self.ended_at = datetime.now(
            timezone.utc
        )

        self._duration_ms = (
            time.perf_counter()
            - self._started_perf
        ) * 1000

    def fail(
        self,
        exc: BaseException,
    ) -> None:
        self.status = SpanStatus.ERROR

        self.add_event(
            "exception",
            type=exc.__class__.__name__,
            message=str(exc),
        )

        self.finish(
            status=SpanStatus.ERROR
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "name": self.name,
            "kind": self.kind.value,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "started_at": self.started_at.isoformat(),
            "attributes": dict(
                self.attributes
            ),
            "events": [
                e.to_dict()
                for e in self.events
            ],
        }

        payload.update(
            self.context.to_dict()
        )

        if self.ended_at:
            payload[
                "ended_at"
            ] = self.ended_at.isoformat()

        return payload


# =========================================================
# tracer
# =========================================================


class Tracer:
    def __init__(
        self,
        *,
        logger: Optional[
            Logger
        ] = None,
        metrics: Optional[
            MetricsClient
        ] = None,
    ) -> None:
        self._logger = (
            logger
            or get_logger()
        )

        self._metrics = (
            metrics
            or MetricsClient()
        )

        self._lock = threading.RLock()

    # -----------------------------------------
    # create span
    # -----------------------------------------

    def start_span(
        self,
        name: str,
        *,
        trace_id: Optional[
            str
        ] = None,
        parent: Optional[
            Span
        ] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> Span:
        context = SpanContext.create(
            trace_id=(
                parent.context.trace_id
                if parent
                else trace_id
            ),
            parent_span_id=(
                parent.context.span_id
                if parent
                else None
            ),
        )

        span = Span(
            name=name,
            context=context,
            kind=kind,
            attributes=dict(
                attributes or {}
            ),
        )

        self._logger.debug(
            "span started",
            **span.context.to_dict(),
            name=name,
        )

        self._metrics.increment(
            "trace.started"
        )

        return span

    # -----------------------------------------
    # end
    # -----------------------------------------

    def end_span(
        self,
        span: Span,
    ) -> None:
        span.finish()

        self._logger.debug(
            "span finished",
            **span.to_dict(),
        )

        self._metrics.increment(
            "trace.finished"
        )

        self._metrics.record(
            "trace.duration_ms",
            span.duration_ms,
        )

    # -----------------------------------------
    # fail
    # -----------------------------------------

    def fail_span(
        self,
        span: Span,
        exc: BaseException,
    ) -> None:
        span.fail(exc)

        self._logger.error(
            "span failed",
            exception=exc,
            **span.to_dict(),
        )

        self._metrics.increment(
            "trace.failed"
        )

    # -----------------------------------------
    # context manager
    # -----------------------------------------

    @asynccontextmanager
    async def span(
        self,
        name: str,
        *,
        parent: Optional[
            Span
        ] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        **attributes: Any,
    ) -> AsyncIterator[Span]:
        span = self.start_span(
            name,
            parent=parent,
            kind=kind,
            attributes=attributes,
        )

        try:
            yield span
            self.end_span(span)

        except Exception as exc:
            self.fail_span(
                span,
                exc,
            )
            raise

    # -----------------------------------------
    # helpers
    # -----------------------------------------

    async def trace(
        self,
        name: str,
        *,
        parent: Optional[
            Span
        ] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        **attributes: Any,
    ) -> AsyncIterator[Span]:
        async with self.span(
            name,
            parent=parent,
            kind=kind,
            **attributes,
        ) as span:
            yield span


# =========================================================
# async tracer
# =========================================================


class AsyncTracer(Tracer):
    async def start_span_async(
        self,
        name: str,
        **kwargs: Any,
    ) -> Span:
        return self.start_span(
            name,
            **kwargs,
        )

    async def end_span_async(
        self,
        span: Span,
    ) -> None:
        self.end_span(span)

    async def fail_span_async(
        self,
        span: Span,
        exc: BaseException,
    ) -> None:
        self.fail_span(
            span,
            exc,
        )