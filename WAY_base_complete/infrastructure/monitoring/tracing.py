from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

logger = logging.getLogger(__name__)

_trace_id: ContextVar[str | None] = ContextVar(
    "trace_id",
    default=None,
)

_span_name: ContextVar[str | None] = ContextVar(
    "span_name",
    default=None,
)


class TraceContext:
    """
    Central tracing context.

    Supports:
        - Django request lifecycle
        - async views
        - Celery workers
        - Channels consumers
        - service layer
    """

    @classmethod
    def new_id(cls) -> str:
        """
        Generate trace id.
        """
        return uuid.uuid4().hex

    @classmethod
    def get_id(cls) -> str | None:
        """
        Current trace id.
        """
        return _trace_id.get()

    @classmethod
    def ensure_id(cls) -> str:
        """
        Ensure trace exists.
        """
        current = cls.get_id()

        if current:
            return current

        trace_id = cls.new_id()

        _trace_id.set(trace_id)

        return trace_id

    @classmethod
    def set_id(
        cls,
        trace_id: str | None,
    ) -> None:
        """
        Set active trace id.
        """
        _trace_id.set(trace_id)

    @classmethod
    def clear(cls) -> None:
        """
        Clear active trace.
        """
        _trace_id.set(None)
        _span_name.set(None)

    @classmethod
    def get_span(cls) -> str | None:
        """
        Current span.
        """
        return _span_name.get()

    @classmethod
    def payload(cls) -> dict[str, Any]:
        """
        Log payload.
        """
        return {
            "trace_id": cls.get_id(),
            "span": cls.get_span(),
        }

    @classmethod
    @contextmanager
    def span(
        cls,
        name: str,
    ):
        """
        Create scoped span.

        Example:
            with TraceContext.span("database.health"):
                ...
        """
        trace_id = cls.ensure_id()

        trace_token = _trace_id.set(trace_id)
        span_token = _span_name.set(name)

        logger.debug(
            "Trace span started",
            extra=cls.payload(),
        )

        try:
            yield trace_id

        finally:
            logger.debug(
                "Trace span finished",
                extra=cls.payload(),
            )

            _trace_id.reset(trace_token)
            _span_name.reset(span_token)


class TraceLogFilter(logging.Filter):
    """
    Inject trace into Django logging.
    """

    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:
        record.trace_id = (
            TraceContext.get_id()
            or "-"
        )

        record.span = (
            TraceContext.get_span()
            or "-"
        )

        return True