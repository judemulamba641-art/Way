"""
WAY Python SDK public package interface.
"""

from __future__ import annotations

from sdk_python.__about__ import (
    __author__,
    __description__,
    __email__,
    __license__,
    __title__,
)

from sdk_python.version import (
    VERSION,
    __version__,
)

__all__: list[str] = [
    "__title__",
    "__description__",
    "__author__",
    "__email__",
    "__license__",
    "__version__",
    "VERSION",

    "SDKConfig",
    "SDKSettings",

    "WAYClient",
    "AsyncWAYClient",

    "SDKError",
    "WayAPIError",

    "AuthenticationError",
    "AuthorizationError",
    "ConfigurationError",
    "NetworkError",
    "RateLimitError",
    "ResourceNotFoundError",
    "SerializationError",
    "TimeoutError",
    "ValidationError",

    "InMemoryCache",
    "RedisCache",

    "StorageClient",
    "AsyncStorageClient",

    "MetricsCollector",
    "TracingManager",
]


def __getattr__(name: str):
    if name == "WAYClient":
        from sdk_python.client import WAYClient
        return WAYClient

    if name == "AsyncWAYClient":
        from sdk_python.async_client import (
            AsyncWAYClient,
        )
        return AsyncWAYClient

    if name in {
        "InMemoryCache",
        "RedisCache",
    }:
        from sdk_python.cache import (
            InMemoryCache,
            RedisCache,
        )
        return locals()[name]

    if name == "SDKConfig":
        from sdk_python.config import SDKConfig
        return SDKConfig

    if name == "SDKSettings":
        from sdk_python.settings import (
            SDKSettings,
        )
        return SDKSettings

    if name in {
        "StorageClient",
        "AsyncStorageClient",
    }:
        from sdk_python.storage import (
            StorageClient,
            AsyncStorageClient,
        )
        return locals()[name]

    if name in {
        "MetricsCollector",
        "TracingManager",
    }:
        from sdk_python.telemetry import (
            MetricsCollector,
            TracingManager,
        )
        return locals()[name]

    if name in {
        "SDKError",
        "WayAPIError",
        "AuthenticationError",
        "AuthorizationError",
        "ConfigurationError",
        "NetworkError",
        "RateLimitError",
        "ResourceNotFoundError",
        "SerializationError",
        "TimeoutError",
        "ValidationError",
    }:
        from sdk_python.exceptions import (
            SDKError,
            WayAPIError,
            AuthenticationError,
            AuthorizationError,
            ConfigurationError,
            NetworkError,
            RateLimitError,
            ResourceNotFoundError,
            SerializationError,
            TimeoutError,
            ValidationError,
        )
        return locals()[name]

    raise AttributeError(
        f"module 'sdk_python' has no attribute '{name}'"
    )


def get_version() -> str:
    return __version__


def get_package_metadata() -> dict[str, str]:
    return {
        "name": __title__,
        "description": __description__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "version": __version__,
    }
