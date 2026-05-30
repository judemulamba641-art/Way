"""
WAY SDK async client.
"""

from __future__ import annotations

from typing import Any, Optional

from sdk_python.auth import AuthManager
from sdk_python.cache import InMemoryCache
from sdk_python.config import SDKConfig
from sdk_python.realtime import RealtimeClient
from sdk_python.settings import SDKSettings
from sdk_python.storage import AsyncStorageClient
from sdk_python.telemetry import (
    MetricsCollector,
    TracingManager,
)
from sdk_python.transport import (
    AsyncTransport,
)


class AsyncWAYClient:
    """
    High-level async WAY client.
    """

    def __init__(
        self,
        *,
        config: Optional[SDKConfig] = None,
        settings: Optional[SDKSettings] = None,
        transport: Optional[
            AsyncTransport
        ] = None,
        cache: Optional[
            InMemoryCache
        ] = None,
        auth: Optional[
            AuthManager
        ] = None,
        storage: Optional[
            AsyncStorageClient
        ] = None,
        metrics: Optional[
            MetricsCollector
        ] = None,
        tracing: Optional[
            TracingManager
        ] = None,
    ) -> None:
        self.config = config or SDKConfig()

        self.settings = (
            settings or SDKSettings()
        )

        self.transport = (
            transport
            or AsyncTransport(
                config=self.config,
            )
        )

        self.cache = (
            cache
            or InMemoryCache()
        )

        self.auth = (
            auth
            or AuthManager(
                config=self.config,
            )
        )

        self.storage = (
            storage
            or AsyncStorageClient(
                transport=self.transport,
                config=self.config,
            )
        )

        self.metrics = (
            metrics
            or MetricsCollector()
        )

        self.tracing = (
            tracing
            or TracingManager()
        )

        self.realtime = RealtimeClient(
            connect=self._rt_connect,
            disconnect=self._rt_disconnect,
            receiver=self._rt_receive,
            sender=self._rt_send,
        )

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        self.metrics.increment(
            "requests.total"
        )

        return await self.transport.request(
            method=method,
            path=path,
            **kwargs,
        )

    async def get(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return await self.request(
            "GET",
            path,
            **kwargs,
        )

    async def post(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return await self.request(
            "POST",
            path,
            **kwargs,
        )

    async def put(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return await self.request(
            "PUT",
            path,
            **kwargs,
        )

    async def patch(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return await self.request(
            "PATCH",
            path,
            **kwargs,
        )

    async def delete(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return await self.request(
            "DELETE",
            path,
            **kwargs,
        )

    async def _rt_connect(
        self,
    ) -> None:
        return None

    async def _rt_disconnect(
        self,
    ) -> None:
        return None

    async def _rt_receive(
        self,
    ) -> dict[str, Any]:
        return {}

    async def _rt_send(
        self,
        payload: dict[str, Any],
    ) -> None:
        return None