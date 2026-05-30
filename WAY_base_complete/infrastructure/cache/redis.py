from __future__ import annotations

import logging
from typing import Optional
from typing import TypeVar

from django.conf import settings
from redis.asyncio import Redis
from redis.asyncio import from_url

from .base import BaseCache

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RedisCache(BaseCache[T]):
    """
    Async Redis cache backend.

    Shared by:
        - Django services
        - Celery workers
        - Channels consumers
        - Domain cache repositories
    """

    _client: Redis | None = None

    def __init__(
        self,
        prefix: str | None = None,
        url: str | None = None,
    ) -> None:
        super().__init__(prefix=prefix)

        self.url = url or settings.REDIS_URL

    async def connect(self) -> Redis:
        """
        Lazy Redis connection.
        """
        if self.__class__._client is None:
            logger.info(
                "Initializing Redis connection",
                extra={
                    "redis_url": self.url,
                },
            )

            self.__class__._client = from_url(
                self.url,
                encoding="utf-8",
                decode_responses=False,
                health_check_interval=30,
                socket_keepalive=True,
            )

        return self.__class__._client

    async def close(self) -> None:
        """
        Graceful shutdown.
        """
        if self.__class__._client is not None:
            logger.info("Closing Redis connection")

            await self.__class__._client.close()

            self.__class__._client = None

    async def ping(self) -> bool:
        """
        Health check.
        """
        try:
            client = await self.connect()

            result = await client.ping()

            return bool(result)

        except Exception:
            logger.exception("Redis ping failed")
            return False

    async def get(
        self,
        key: str,
        default: Optional[T] = None,
    ) -> Optional[T]:
        redis_key = self.build_key(key)

        try:
            client = await self.connect()

            value = await client.get(redis_key)

            if value is None:
                return default

            return self.deserialize(value)

        except Exception:
            logger.exception(
                "Redis GET failed",
                extra={"key": redis_key},
            )
            return default

    async def set(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
    ) -> bool:
        redis_key = self.build_key(key)

        try:
            client = await self.connect()

            payload = self.serialize(value)

            await client.set(
                redis_key,
                payload,
                ex=ttl,
            )

            return True

        except Exception:
            logger.exception(
                "Redis SET failed",
                extra={"key": redis_key},
            )
            return False

    async def delete(
        self,
        key: str,
    ) -> bool:
        redis_key = self.build_key(key)

        try:
            client = await self.connect()

            deleted = await client.delete(redis_key)

            return bool(deleted)

        except Exception:
            logger.exception(
                "Redis DELETE failed",
                extra={"key": redis_key},
            )
            return False

    async def exists(
        self,
        key: str,
    ) -> bool:
        redis_key = self.build_key(key)

        try:
            client = await self.connect()

            exists = await client.exists(redis_key)

            return bool(exists)

        except Exception:
            logger.exception(
                "Redis EXISTS failed",
                extra={"key": redis_key},
            )
            return False

    async def expire(
        self,
        key: str,
        ttl: int,
    ) -> bool:
        redis_key = self.build_key(key)

        try:
            client = await self.connect()

            result = await client.expire(
                redis_key,
                ttl,
            )

            return bool(result)

        except Exception:
            logger.exception(
                "Redis EXPIRE failed",
                extra={"key": redis_key},
            )
            return False

    async def clear(self) -> bool:
        """
        Clear only namespace keys.
        """
        try:
            client = await self.connect()

            pattern = f"{self.prefix}:*"

            cursor = 0

            while True:
                cursor, keys = await client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=500,
                )

                if keys:
                    await client.delete(*keys)

                if cursor == 0:
                    break

            return True

        except Exception:
            logger.exception(
                "Redis CLEAR failed",
                extra={"prefix": self.prefix},
            )
            return False