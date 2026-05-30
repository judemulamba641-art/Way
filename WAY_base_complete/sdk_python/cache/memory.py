from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
import asyncio
from typing import Any, Generic, TypeVar

from sdk_python.cache.keys import CacheKey


T = TypeVar("T")


#
# =========================================================
# Models
# =========================================================
#


@dataclass(slots=True)
class CacheEntry(Generic[T]):
    """
    Internal cache value container.
    """

    value: T
    expires_at: datetime | None = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False

        return datetime.now(timezone.utc) >= self.expires_at


@dataclass(slots=True)
class CacheStats:
    """
    Runtime cache stats.
    """

    hits: int = 0
    misses: int = 0
    writes: int = 0
    deletes: int = 0
    evictions: int = 0

    @property
    def requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        total = self.requests

        if total == 0:
            return 0.0

        return (self.hits / total) * 100


#
# =========================================================
# Helpers
# =========================================================
#


def _expires_at(
    ttl: int | float | None,
) -> datetime | None:
    if ttl is None:
        return None

    return (
        datetime.now(timezone.utc)
        + timedelta(seconds=float(ttl))
    )


#
# =========================================================
# Sync Memory Cache
# =========================================================
#


class InMemoryCache:
    """
    Thread-safe sync in-memory cache.
    """

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry[Any]] = {}
        self._lock = RLock()
        self.stats = CacheStats()

    #
    # -----------------------------------------------------
    # internals
    # -----------------------------------------------------
    #

    def _purge_expired(
        self,
        key: str,
    ) -> None:
        entry = self._store.get(key)

        if entry is None:
            return

        if entry.is_expired():
            self._store.pop(key, None)
            self.stats.evictions += 1

    #
    # -----------------------------------------------------
    # public
    # -----------------------------------------------------
    #

    def get(
        self,
        key: CacheKey,
        default: Any = None,
    ) -> Any:
        full = key.full()

        with self._lock:
            self._purge_expired(full)

            entry = self._store.get(full)

            if entry is None:
                self.stats.misses += 1
                return default

            self.stats.hits += 1
            return entry.value

    def set(
        self,
        key: CacheKey,
        value: Any,
        *,
        ttl: int | float | None = None,
    ) -> None:
        full = key.full()

        with self._lock:
            self._store[full] = CacheEntry(
                value=value,
                expires_at=_expires_at(ttl),
            )

            self.stats.writes += 1

    def delete(
        self,
        key: CacheKey,
    ) -> bool:
        full = key.full()

        with self._lock:
            existed = full in self._store

            self._store.pop(full, None)

            if existed:
                self.stats.deletes += 1

            return existed

    def exists(
        self,
        key: CacheKey,
    ) -> bool:
        return self.get(key) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def keys(self) -> list[str]:
        with self._lock:
            expired = []

            for key, value in self._store.items():
                if value.is_expired():
                    expired.append(key)

            for key in expired:
                self._store.pop(key, None)

            return list(self._store.keys())

    def size(self) -> int:
        return len(self.keys())


#
# =========================================================
# Async Memory Cache
# =========================================================
#


class AsyncInMemoryCache:
    """
    Async-safe in-memory cache.
    """

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry[Any]] = {}
        self._lock = asyncio.Lock()
        self.stats = CacheStats()

    #
    # -----------------------------------------------------
    # internals
    # -----------------------------------------------------
    #

    def _purge_expired(
        self,
        key: str,
    ) -> None:
        entry = self._store.get(key)

        if entry is None:
            return

        if entry.is_expired():
            self._store.pop(key, None)
            self.stats.evictions += 1

    #
    # -----------------------------------------------------
    # public
    # -----------------------------------------------------
    #

    async def get(
        self,
        key: CacheKey,
        default: Any = None,
    ) -> Any:
        full = key.full()

        async with self._lock:
            self._purge_expired(full)

            entry = self._store.get(full)

            if entry is None:
                self.stats.misses += 1
                return default

            self.stats.hits += 1
            return entry.value

    async def set(
        self,
        key: CacheKey,
        value: Any,
        *,
        ttl: int | float | None = None,
    ) -> None:
        full = key.full()

        async with self._lock:
            self._store[full] = CacheEntry(
                value=value,
                expires_at=_expires_at(ttl),
            )

            self.stats.writes += 1

    async def delete(
        self,
        key: CacheKey,
    ) -> bool:
        full = key.full()

        async with self._lock:
            existed = full in self._store

            self._store.pop(full, None)

            if existed:
                self.stats.deletes += 1

            return existed

    async def exists(
        self,
        key: CacheKey,
    ) -> bool:
        return await self.get(key) is not None

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    async def keys(self) -> list[str]:
        async with self._lock:
            expired = []

            for key, value in self._store.items():
                if value.is_expired():
                    expired.append(key)

            for key in expired:
                self._store.pop(key, None)

            return list(self._store.keys())

    async def size(self) -> int:
        keys = await self.keys()
        return len(keys)