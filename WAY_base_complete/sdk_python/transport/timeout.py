from __future__ import annotations

import asyncio
import threading
import time
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    TypeVar,
)

from sdk_python.exceptions import SDKTimeoutError

T = TypeVar("T")


@dataclass(slots=True, frozen=True)
class Deadline:
    """
    Représente une deadline absolue monotonic.
    """

    expires_at: float

    @classmethod
    def after(cls, seconds: float | None) -> Deadline | None:
        """
        Crée une deadline dans X secondes.
        """
        if seconds is None:
            return None

        return cls(expires_at=time.monotonic() + max(seconds, 0.0))

    @property
    def remaining(self) -> float:
        """
        Temps restant avant expiration.
        """
        return max(self.expires_at - time.monotonic(), 0.0)

    @property
    def expired(self) -> bool:
        """
        Deadline expirée ?
        """
        return self.remaining <= 0

    def clamp(self, seconds: float | None) -> Deadline | None:
        """
        Combine deadline actuelle + timeout enfant.
        Garde la plus proche.
        """
        if seconds is None:
            return self

        candidate = Deadline.after(seconds)

        if candidate is None:
            return self

        if candidate.expires_at < self.expires_at:
            return candidate

        return self

    def raise_if_expired(self, message: str = "Operation timed out") -> None:
        """
        Raise immédiatement si expirée.
        """
        if self.expired:
            raise SDKTimeoutError(message)


class TimeoutContext(
    AbstractContextManager["TimeoutContext"],
    AbstractAsyncContextManager["TimeoutContext"],
):
    """
    Context manager sync + async pour timeout.
    """

    def __init__(
        self,
        deadline: Deadline | None,
        *,
        message: str = "Operation timed out",
    ) -> None:
        self._deadline = deadline
        self._message = message

    @property
    def deadline(self) -> Deadline | None:
        return self._deadline

    @property
    def remaining(self) -> float | None:
        if self._deadline is None:
            return None

        return self._deadline.remaining

    def ensure(self) -> None:
        if self._deadline is not None:
            self._deadline.raise_if_expired(self._message)

    def __enter__(self) -> TimeoutContext:
        self.ensure()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.ensure()
        return False

    async def __aenter__(self) -> TimeoutContext:
        self.ensure()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        self.ensure()
        return False


class TimeoutManager:
    """
    Gestionnaire central timeout.
    Thread-safe.
    """

    def __init__(
        self,
        timeout: float | None = None,
    ) -> None:
        self._default_timeout = timeout
        self._lock = threading.RLock()

    @property
    def default_timeout(self) -> float | None:
        return self._default_timeout

    def deadline(
        self,
        timeout: float | None = None,
        *,
        parent: Deadline | None = None,
    ) -> Deadline | None:
        """
        Crée deadline en tenant compte parent.
        """
        value = timeout if timeout is not None else self._default_timeout

        if parent is None:
            return Deadline.after(value)

        return parent.clamp(value)

    def context(
        self,
        timeout: float | None = None,
        *,
        parent: Deadline | None = None,
        message: str = "Operation timed out",
    ) -> TimeoutContext:
        """
        Retourne context manager timeout.
        """
        return TimeoutContext(
            self.deadline(timeout, parent=parent),
            message=message,
        )

    def run(
        self,
        func: Callable[..., T],
        *args: Any,
        timeout: float | None = None,
        parent: Deadline | None = None,
        **kwargs: Any,
    ) -> T:
        """
        Exécute sync sous timeout.
        """
        deadline = self.deadline(timeout, parent=parent)

        if deadline is not None:
            deadline.raise_if_expired()

        result = func(*args, **kwargs)

        if deadline is not None:
            deadline.raise_if_expired()

        return result

    async def run_async(
        self,
        awaitable: Awaitable[T],
        *,
        timeout: float | None = None,
        parent: Deadline | None = None,
    ) -> T:
        """
        Exécute coroutine sous timeout.
        """
        deadline = self.deadline(timeout, parent=parent)

        if deadline is None:
            return await awaitable

        remaining = deadline.remaining

        if remaining <= 0:
            raise SDKTimeoutError("Operation timed out")

        try:
            return await asyncio.wait_for(
                awaitable,
                timeout=remaining,
            )

        except asyncio.TimeoutError as exc:
            raise SDKTimeoutError(
                "Operation timed out"
            ) from exc