from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import Final

from sdk_python.transport.base import BaseTransportResponse


__all__ = [
    "RetryDecision",
    "RetryBackoffStrategy",
    "RetryConfig",
    "RetryPolicy",
]


DEFAULT_MAX_ATTEMPTS: Final[int] = 3
DEFAULT_BASE_DELAY: Final[float] = 0.5
DEFAULT_MAX_DELAY: Final[float] = 30.0
DEFAULT_JITTER_FACTOR: Final[float] = 0.2


class RetryDecision(str, Enum):
    RETRY = "retry"
    FAIL = "fail"
    SUCCESS = "success"


class RetryBackoffStrategy(str, Enum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass(slots=True, frozen=True)
class RetryConfig:
    """
    Transport retry policy config.
    """

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    base_delay: float = DEFAULT_BASE_DELAY
    max_delay: float = DEFAULT_MAX_DELAY
    jitter_factor: float = DEFAULT_JITTER_FACTOR

    strategy: RetryBackoffStrategy = (
        RetryBackoffStrategy.EXPONENTIAL
    )

    retry_on_status: frozenset[int] = field(
        default_factory=lambda: frozenset(
            {
                408,
                425,
                429,
                500,
                502,
                503,
                504,
            }
        )
    )

    retry_on_exceptions: frozenset[type[Exception]] = field(
        default_factory=frozenset,
    )

    def should_retry_status(
        self,
        status_code: int,
    ) -> bool:
        return status_code in self.retry_on_status

    def should_retry_exception(
        self,
        exc: Exception,
    ) -> bool:
        if not self.retry_on_exceptions:
            return False

        return isinstance(
            exc,
            tuple(self.retry_on_exceptions),
        )


@dataclass(slots=True, frozen=True)
class RetryPolicy:
    """
    Enterprise retry executor.
    """

    config: RetryConfig = field(
        default_factory=RetryConfig,
    )

    def should_retry_response(
        self,
        response: BaseTransportResponse,
        *,
        attempt: int,
    ) -> RetryDecision:
        if response.ok:
            return RetryDecision.SUCCESS

        if attempt >= self.config.max_attempts:
            return RetryDecision.FAIL

        if self.config.should_retry_status(
            response.status_code,
        ):
            return RetryDecision.RETRY

        return RetryDecision.FAIL

    def should_retry_exception(
        self,
        exc: Exception,
        *,
        attempt: int,
    ) -> RetryDecision:
        if attempt >= self.config.max_attempts:
            return RetryDecision.FAIL

        if self.config.should_retry_exception(exc):
            return RetryDecision.RETRY

        return RetryDecision.FAIL

    def compute_delay(
        self,
        attempt: int,
    ) -> float:
        strategy = self.config.strategy
        base = self.config.base_delay

        match strategy:
            case RetryBackoffStrategy.FIXED:
                delay = base

            case RetryBackoffStrategy.LINEAR:
                delay = base * attempt

            case RetryBackoffStrategy.EXPONENTIAL:
                delay = base * (2 ** (attempt - 1))

        delay = min(
            delay,
            self.config.max_delay,
        )

        return self._with_jitter(delay)

    def compute_timedelta(
        self,
        attempt: int,
    ) -> timedelta:
        return timedelta(
            seconds=self.compute_delay(attempt),
        )

    def sleep(
        self,
        attempt: int,
    ) -> None:
        time.sleep(
            self.compute_delay(attempt),
        )

    async def asleep(
        self,
        attempt: int,
    ) -> None:
        import asyncio

        await asyncio.sleep(
            self.compute_delay(attempt),
        )

    def _with_jitter(
        self,
        delay: float,
    ) -> float:
        factor = self.config.jitter_factor

        if factor <= 0:
            return delay

        spread = delay * factor

        return max(
            0.0,
            random.uniform(
                delay - spread,
                delay + spread,
            ),
        )