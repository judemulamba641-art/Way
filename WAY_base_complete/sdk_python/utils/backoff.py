from __future__ import annotations

import time
import random
import asyncio
from dataclasses import dataclass
from typing import Callable, TypeVar, Optional, Type, Tuple, Union


T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


# =========================================================
# STRATEGY CONFIGURATION
# =========================================================

@dataclass(slots=True)
class BackoffStrategy:
    """
    Configuration for retry/backoff behavior.

    This is used by both sync and async SDK layers.
    """

    retries: int = 3
    base_delay: float = 0.5
    max_delay: float = 10.0
    exponential_base: float = 2.0
    jitter: bool = True

    def compute_delay(self, attempt: int) -> float:
        """
        Compute delay for a given retry attempt.
        """

        delay = self.base_delay * (self.exponential_base ** attempt)

        if self.jitter:
            delay = delay * (0.5 + random.random())

        return min(delay, self.max_delay)


# =========================================================
# SYNC RETRY CORE
# =========================================================

def retry(
    fn: Callable[[], T],
    *,
    strategy: Optional[BackoffStrategy] = None,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
) -> T:
    """
    Execute a function with retry + exponential backoff.

    Designed for:
    - HTTP transport
    - auth refresh
    - transient failures
    """

    strategy = strategy or BackoffStrategy()
    last_error: Optional[BaseException] = None

    for attempt in range(strategy.retries + 1):
        try:
            return fn()

        except retry_on as e:
            last_error = e

            if attempt >= strategy.retries:
                break

            delay = strategy.compute_delay(attempt)
            time.sleep(delay)

    raise last_error  # type: ignore


# =========================================================
# ASYNC RETRY CORE
# =========================================================

async def retry_async(
    fn: Callable[[], T],
    *,
    strategy: Optional[BackoffStrategy] = None,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
) -> T:
    """
    Async version of retry with exponential backoff.

    Used for:
    - Async HTTP client
    - WebSocket reconnect
    - Async storage operations
    """

    strategy = strategy or BackoffStrategy()
    last_error: Optional[BaseException] = None

    for attempt in range(strategy.retries + 1):
        try:
            result = fn()

            # If coroutine returned, await it
            if asyncio.iscoroutine(result):
                return await result  # type: ignore

            return result  # type: ignore

        except retry_on as e:
            last_error = e

            if attempt >= strategy.retries:
                break

            delay = strategy.compute_delay(attempt)
            await asyncio.sleep(delay)

    raise last_error  # type: ignore


# =========================================================
# DECORATOR HELPERS
# =========================================================

def with_retry(
    strategy: Optional[BackoffStrategy] = None,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
):
    """
    Decorator version of retry (sync).
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            return retry(lambda: fn(*args, **kwargs), strategy=strategy, retry_on=retry_on)

        return wrapper

    return decorator


def with_retry_async(
    strategy: Optional[BackoffStrategy] = None,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
):
    """
    Decorator version of retry (async).
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(lambda: fn(*args, **kwargs), strategy=strategy, retry_on=retry_on)

        return wrapper

    return decorator