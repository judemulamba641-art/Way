"""
WAY Python SDK public package interface.

Stable public API for external Python consumers.

Design goals:
- enterprise-grade imports
- predictable developer experience
- stable semantic versioning
- typed exports
- minimal import overhead
- future-safe package entrypoint

Example:
    from sdk_python import WayClient

    client = WayClient()
"""

from __future__ import annotations

from sdk_python.__about__ import (
    __author__,
    __description__,
    __email__,
    __license__,
    __title__,
)
from sdk_python.async_client import (
    AsyncWAYClient,
)
from sdk_python.cache import (
    InMemoryCache,
    RedisCache,
)
from sdk_python.client import (
    WAYClient,
)
from sdk_python.config import (
    SDKConfig,
)
from sdk_python.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    SDKError,
    SerializationError,
    TimeoutError,
    ValidationError,
    WayAPIError,
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
from sdk_python.version import (
    VERSION,
    __version__,
)

__all__: list[str] = [
    #
    # metadata
    #
    "__title__",
    "__description__",
    "__author__",
    "__email__",
    "__license__",
    "__version__",
    "VERSION",

    #
    # config
    #
    "SDKConfig",
    "SDKSettings",

    #
    # clients
    #
    "WAYClient",
    "AsyncWAYClient",

    #
    # auth / core exceptions
    #
    "SDKError",
    "WayAPIError",

    #
    # common exceptions
    #
    "AuthenticationError",
    "AuthorizationError",
    "ConfigurationError",
    "NetworkError",
    "RateLimitError",
    "ResourceNotFoundError",
    "SerializationError",
    "TimeoutError",
    "ValidationError",

    #
    # cache
    #
    "InMemoryCache",
    "RedisCache",

    #
    # storage
    #
    "StorageClient",
    "AsyncStorageClient",

    #
    # telemetry
    #
    "MetricsCollector",
    "TracingManager",
]


def get_version() -> str:
    """
    Return installed SDK version.
    """
    return __version__


def get_package_metadata() -> dict[str, str]:
    """
    Return package metadata.

    Useful for:
    - diagnostics
    - telemetry
    - debugging
    - SDK introspection
    """
    return {
        "name": __title__,
        "description": __description__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "version": __version__,
    }