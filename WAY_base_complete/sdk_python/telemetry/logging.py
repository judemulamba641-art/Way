from __future__ import annotations

import asyncio
import json
import logging
import sys
import threading
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
)

# =========================================================
# levels
# =========================================================


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @property
    def numeric(self) -> int:
        return {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }[self]


# =========================================================
# context
# =========================================================


@dataclass(slots=True)
class LogContext:
    service: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}

        if self.service:
            payload["service"] = self.service

        if self.request_id:
            payload["request_id"] = self.request_id

        if self.trace_id:
            payload["trace_id"] = self.trace_id

        if self.span_id:
            payload["span_id"] = self.span_id

        if self.user_id:
            payload["user_id"] = self.user_id

        payload.update(self.metadata)

        return payload

    def merge(
        self,
        other: Optional["LogContext"] = None,
        **extra: Any,
    ) -> "LogContext":
        data = self.to_dict()

        if other:
            data.update(other.to_dict())

        data.update(extra)

        return LogContext(
            service=data.pop("service", None),
            request_id=data.pop("request_id", None),
            trace_id=data.pop("trace_id", None),
            span_id=data.pop("span_id", None),
            user_id=data.pop("user_id", None),
            metadata=data,
        )


# =========================================================
# entry
# =========================================================


@dataclass(slots=True)
class LogEntry:
    level: LogLevel
    message: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    context: LogContext = field(default_factory=LogContext)
    exception: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
        }

        payload.update(self.context.to_dict())

        if self.exception:
            payload["exception"] = self.exception

        return payload

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
        )


# =========================================================
# handler protocol
# =========================================================


class AsyncLogHandler(Protocol):
    async def emit(self, entry: LogEntry) -> None:
        ...


# =========================================================
# console handler
# =========================================================


class _ConsoleHandler:
    def emit_sync(self, entry: LogEntry) -> None:
        print(entry.to_json(), file=sys.stdout)


# =========================================================
# logger
# =========================================================


class Logger:
    def __init__(
        self,
        *,
        name: str = "sdk_python",
        level: LogLevel = LogLevel.INFO,
        context: Optional[LogContext] = None,
        handlers: Optional[Iterable[AsyncLogHandler]] = None,
    ) -> None:
        self._name = name
        self._level = level
        self._context = context or LogContext(service=name)

        self._handlers = list(handlers or [])
        self._console = _ConsoleHandler()

        self._lock = threading.RLock()

    # -------------------------------------------------
    # child logger
    # -------------------------------------------------

    def child(
        self,
        **context: Any,
    ) -> "Logger":
        return Logger(
            name=self._name,
            level=self._level,
            context=self._context.merge(**context),
            handlers=self._handlers,
        )

    # -------------------------------------------------
    # internal
    # -------------------------------------------------

    def _enabled(self, level: LogLevel) -> bool:
        return level.numeric >= self._level.numeric

    def _build_entry(
        self,
        level: LogLevel,
        message: str,
        *,
        context: Optional[Mapping[str, Any]] = None,
        exception: Optional[BaseException] = None,
    ) -> LogEntry:
        merged = self._context.merge(**dict(context or {}))

        return LogEntry(
            level=level,
            message=message,
            context=merged,
            exception=str(exception) if exception else None,
        )

    async def _emit_async(self, entry: LogEntry) -> None:
        for handler in self._handlers:
            await handler.emit(entry)

    def _emit_sync(self, entry: LogEntry) -> None:
        self._console.emit_sync(entry)

        if self._handlers:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._emit_async(entry))
            except RuntimeError:
                pass

    def _log(
        self,
        level: LogLevel,
        message: str,
        *,
        context: Optional[Mapping[str, Any]] = None,
        exception: Optional[BaseException] = None,
    ) -> None:
        if not self._enabled(level):
            return

        entry = self._build_entry(
            level,
            message,
            context=context,
            exception=exception,
        )

        with self._lock:
            self._emit_sync(entry)

    # -------------------------------------------------
    # public
    # -------------------------------------------------

    def debug(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._log(LogLevel.DEBUG, message, context=context)

    def info(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._log(LogLevel.INFO, message, context=context)

    def warning(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._log(LogLevel.WARNING, message, context=context)

    def error(
        self,
        message: str,
        *,
        exception: Optional[BaseException] = None,
        **context: Any,
    ) -> None:
        self._log(
            LogLevel.ERROR,
            message,
            context=context,
            exception=exception,
        )

    def critical(
        self,
        message: str,
        *,
        exception: Optional[BaseException] = None,
        **context: Any,
    ) -> None:
        self._log(
            LogLevel.CRITICAL,
            message,
            context=context,
            exception=exception,
        )

    # -------------------------------------------------
    # async
    # -------------------------------------------------

    async def adebug(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self.debug(message, **context)

    async def ainfo(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self.info(message, **context)

    async def awarning(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self.warning(message, **context)

    async def aerror(
        self,
        message: str,
        *,
        exception: Optional[BaseException] = None,
        **context: Any,
    ) -> None:
        self.error(
            message,
            exception=exception,
            **context,
        )

    # -------------------------------------------------
    # context manager
    # -------------------------------------------------

    @asynccontextmanager
    async def span(
        self,
        message: str,
        **context: Any,
    ) -> AsyncIterator[None]:
        await self.adebug(f"{message}:start", **context)

        try:
            yield
            await self.adebug(f"{message}:end", **context)
        except Exception as exc:
            await self.aerror(
                f"{message}:failed",
                exception=exc,
                **context,
            )
            raise


# =========================================================
# default singleton
# =========================================================

_default_logger = Logger()


def get_logger() -> Logger:
    return _default_logger