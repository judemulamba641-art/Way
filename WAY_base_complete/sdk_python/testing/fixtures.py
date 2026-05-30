"""
WAY SDK testing fixtures.
"""

from __future__ import annotations

from typing import Any

from sdk_python.async_client import (
    AsyncWAYClient,
)
from sdk_python.cache import (
    InMemoryCache,
)
from sdk_python.client import (
    WAYClient,
)
from sdk_python.config import (
    SDKConfig,
)
from sdk_python.settings import (
    SDKSettings,
)
from sdk_python.storage import (
    AsyncStorageClient,
    StorageClient,
)
from sdk_python.telemetry import (
    MetricsCollector,
    TracingManager,
)

from .mocks import (
    MockAsyncTransport,
    MockCache,
    MockTransport,
)


def create_config(
    **overrides: Any,
) -> SDKConfig:
    """
    Create test config.
    """
    return SDKConfig(
        **overrides
    )


def create_settings(
    **overrides: Any,
) -> SDKSettings:
    """
    Create test settings.
    """
    return SDKSettings(
        **overrides
    )


def create_cache() -> MockCache:
    """
    Create test cache.
    """
    return MockCache()


def create_metrics() -> MetricsCollector:
    """
    Create metrics collector.
    """
    return MetricsCollector()


def create_tracing() -> TracingManager:
    """
    Create tracing manager.
    """
    return TracingManager()


def create_transport() -> MockTransport:
    """
    Create sync transport.
    """
    return MockTransport()


def create_async_transport(
) -> MockAsyncTransport:
    """
    Create async transport.
    """
    return MockAsyncTransport()


def create_storage(
    *,
    transport: MockTransport,
    config: SDKConfig,
) -> StorageClient:
    """
    Create sync storage.
    """
    return StorageClient(
        transport=transport,
        config=config,
    )


def create_async_storage(
    *,
    transport: MockAsyncTransport,
    config: SDKConfig,
) -> AsyncStorageClient:
    """
    Create async storage.
    """
    return AsyncStorageClient(
        transport=transport,
        config=config,
    )


def create_client(
    **overrides: Any,
) -> WAYClient:
    """
    Create ready-to-test sync client.
    """

    config = create_config(
        **overrides
    )

    transport = create_transport()

    cache = create_cache()

    metrics = create_metrics()

    tracing = create_tracing()

    storage = create_storage(
        transport=transport,
        config=config,
    )

    return WAYClient(
        config=config,
        settings=create_settings(),
        transport=transport,
        cache=cache,
        storage=storage,
        metrics=metrics,
        tracing=tracing,
    )


def create_async_client(
    **overrides: Any,
) -> AsyncWAYClient:
    """
    Create ready async client.
    """

    config = create_config(
        **overrides
    )

    transport = (
        create_async_transport()
    )

    cache = create_cache()

    metrics = create_metrics()

    tracing = create_tracing()

    storage = (
        create_async_storage(
            transport=transport,
            config=config,
        )
    )

    return AsyncWAYClient(
        config=config,
        settings=create_settings(),
        transport=transport,
        cache=cache,
        storage=storage,
        metrics=metrics,
        tracing=tracing,
    )