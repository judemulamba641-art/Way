"""
WAY SDK synchronous client.
"""

from __future__ import annotations

from typing import Any, Optional

from sdk_python.auth import AuthManager
from sdk_python.cache import InMemoryCache
from sdk_python.config import SDKConfig
from sdk_python.realtime import RealtimeClient
from sdk_python.settings import SDKSettings
from sdk_python.storage import StorageClient
from sdk_python.telemetry import (
    MetricsCollector,
    TracingManager,
)
from sdk_python.transport import Transport


class WAYClient:
    """
    High-level synchronous WAY client.
    """

    def __init__(
        self,
        *,
        config: Optional[SDKConfig] = None,
        settings: Optional[SDKSettings] = None,
        transport: Optional[Transport] = None,
        cache: Optional[InMemoryCache] = None,
        auth: Optional[AuthManager] = None,
        storage: Optional[StorageClient] = None,
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
            or Transport(
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
            or StorageClient(
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

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        self.metrics.increment(
            "requests.total"
        )

        return self.transport.request(
            method=method,
            path=path,
            **kwargs,
        )

    def get(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return self.request(
            "GET",
            path,
            **kwargs,
        )

    def post(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return self.request(
            "POST",
            path,
            **kwargs,
        )

    def put(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return self.request(
            "PUT",
            path,
            **kwargs,
        )

    def patch(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return self.request(
            "PATCH",
            path,
            **kwargs,
        )

    def delete(
        self,
        path: str,
        **kwargs: Any,
    ) -> Any:
        return self.request(
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