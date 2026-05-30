from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any
from typing import Generic
from typing import Optional
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheBackend(ABC, Generic[T]):
    """
    Base contract for cache backends.

    All cache implementations must respect this API.
    """

    @abstractmethod
    async def get(
        self,
        key: str,
        default: Optional[T] = None,
    ) -> Optional[T]:
        ...

    @abstractmethod
    async def set(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
    ) -> bool:
        ...

    @abstractmethod
    async def delete(
        self,
        key: str,
    ) -> bool:
        ...

    @abstractmethod
    async def exists(
        self,
        key: str,
    ) -> bool:
        ...

    @abstractmethod
    async def expire(
        self,
        key: str,
        ttl: int,
    ) -> bool:
        ...

    @abstractmethod
    async def clear(self) -> bool:
        ...


class BaseCache(CacheBackend[T]):
    """
    Shared helpers for all cache providers.

    Example:
        redis cache
        memory cache
        custom distributed cache
    """

    namespace = "way"

    def __init__(
        self,
        prefix: str | None = None,
    ) -> None:
        self.prefix = prefix or self.namespace

    def build_key(
        self,
        key: str,
    ) -> str:
        """
        Create namespaced cache key.
        """
        return f"{self.prefix}:{key}"

    def serialize(
        self,
        value: Any,
    ) -> str:
        """
        Serialize python object to JSON.
        """
        try:
            return json.dumps(
                value,
                default=str,
                ensure_ascii=False,
            )
        except Exception:
            logger.exception(
                "Cache serialization failed",
                extra={"value_type": type(value).__name__},
            )
            raise

    def deserialize(
        self,
        value: str | bytes | None,
    ) -> Any:
        """
        Deserialize cache payload.
        """
        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode()

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(
                "Cache deserialize fallback",
                extra={"payload": str(value)[:200]},
            )
            return value

    async def get(
        self,
        key: str,
        default: Optional[T] = None,
    ) -> Optional[T]:
        raise NotImplementedError

    async def set(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
    ) -> bool:
        raise NotImplementedError

    async def delete(
        self,
        key: str,
    ) -> bool:
        raise NotImplementedError

    async def exists(
        self,
        key: str,
    ) -> bool:
        raise NotImplementedError

    async def expire(
        self,
        key: str,
        ttl: int,
    ) -> bool:
        raise NotImplementedError

    async def clear(self) -> bool:
        raise NotImplementedError