from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json

from sdk_python.cache.keys import CacheKey


#
# =========================================================
# Optional imports
# =========================================================
#


try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


try:
    import redis.asyncio as redis_async
except ImportError:  # pragma: no cover
    redis_async = None


#
# =========================================================
# Exceptions
# =========================================================
#


class RedisCacheError(RuntimeError):
    """
    Redis cache failure.
    """


#
# =========================================================
# Stats
# =========================================================
#


@dataclass(slots=True)
class RedisCacheStats:
    hits: int = 0
    misses: int = 0
    writes: int = 0
    deletes: int = 0

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
# Serialization
# =========================================================
#


def _serialize(value: Any) -> str:
    return json.dumps(
        value,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _deserialize(value: bytes | str | None) -> Any:
    if value is None:
        return None

    if isinstance(value, bytes):
        value = value.decode("utf-8")

    return json.loads(value)


#
# =========================================================
# Sync Redis
# =========================================================
#


class RedisCache:
    """
    Production-ready sync Redis cache backend.
    """

    def __init__(
        self,
        client: Any | None = None,
        *,
        url: str | None = None,
        prefix: str = "way",
    ) -> None:
        if redis is None and client is None:
            raise RedisCacheError(
                "redis package not installed."
            )

        self._client = (
            client
            if client is not None
            else redis.from_url(
                url or "redis://localhost:6379/0",
                decode_responses=False,
            )
        )

        self._prefix = prefix
        self.stats = RedisCacheStats()

    #
    # -----------------------------------------------------
    # internals
    # -----------------------------------------------------
    #

    def _full(
        self,
        key: CacheKey,
    ) -> str:
        return f"{self._prefix}:{key.full()}"

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
        value = self._client.get(
            self._full(key),
        )

        if value is None:
            self.stats.misses += 1
            return default

        self.stats.hits += 1

        return _deserialize(value)

    def set(
        self,
        key: CacheKey,
        value: Any,
        *,
        ttl: int | float | None = None,
    ) -> None:
        payload = _serialize(value)

        redis_key = self._full(key)

        if ttl is None:
            self._client.set(
                redis_key,
                payload,
            )
        else:
            self._client.set(
                redis_key,
                payload,
                ex=int(ttl),
            )

        self.stats.writes += 1

    def delete(
        self,
        key: CacheKey,
    ) -> bool:
        deleted = self._client.delete(
            self._full(key),
        )

        if deleted:
            self.stats.deletes += 1

        return bool(deleted)

    def exists(
        self,
        key: CacheKey,
    ) -> bool:
        return bool(
            self._client.exists(
                self._full(key),
            )
        )

    def clear(self) -> None:
        pattern = f"{self._prefix}:*"

        for key in self._client.scan_iter(pattern):
            self._client.delete(key)

    def keys(self) -> list[str]:
        pattern = f"{self._prefix}:*"

        result: list[str] = []

        for key in self._client.scan_iter(pattern):
            if isinstance(key, bytes):
                result.append(
                    key.decode("utf-8")
                )
            else:
                result.append(key)

        return result

    def size(self) -> int:
        return len(self.keys())


#
# =========================================================
# Async Redis
# =========================================================
#


class AsyncRedisCache:
    """
    Production-ready async Redis backend.
    """

    def __init__(
        self,
        client: Any | None = None,
        *,
        url: str | None = None,
        prefix: str = "way",
    ) -> None:
        if redis_async is None and client is None:
            raise RedisCacheError(
                "redis package not installed."
            )

        self._client = (
            client
            if client is not None
            else redis_async.from_url(
                url or "redis://localhost:6379/0",
                decode_responses=False,
            )
        )

        self._prefix = prefix
        self.stats = RedisCacheStats()

    #
    # -----------------------------------------------------
    # internals
    # -----------------------------------------------------
    #

    def _full(
        self,
        key: CacheKey,
    ) -> str:
        return f"{self._prefix}:{key.full()}"

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
        value = await self._client.get(
            self._full(key),
        )

        if value is None:
            self.stats.misses += 1
            return default

        self.stats.hits += 1

        return _deserialize(value)

    async def set(
        self,
        key: CacheKey,
        value: Any,
        *,
        ttl: int | float | None = None,
    ) -> None:
        payload = _serialize(value)

        redis_key = self._full(key)

        if ttl is None:
            await self._client.set(
                redis_key,
                payload,
            )
        else:
            await self._client.set(
                redis_key,
                payload,
                ex=int(ttl),
            )

        self.stats.writes += 1

    async def delete(
        self,
        key: CacheKey,
    ) -> bool:
        deleted = await self._client.delete(
            self._full(key),
        )

        if deleted:
            self.stats.deletes += 1

        return bool(deleted)

    async def exists(
        self,
        key: CacheKey,
    ) -> bool:
        return bool(
            await self._client.exists(
                self._full(key),
            )
        )

    async def clear(self) -> None:
        pattern = f"{self._prefix}:*"

        async for key in self._client.scan_iter(pattern):
            await self._client.delete(key)

    async def keys(self) -> list[str]:
        pattern = f"{self._prefix}:*"

        result: list[str] = []

        async for key in self._client.scan_iter(pattern):
            if isinstance(key, bytes):
                result.append(
                    key.decode("utf-8")
                )
            else:
                result.append(key)

        return result

    async def size(self) -> int:
        keys = await self.keys()
        return len(keys)