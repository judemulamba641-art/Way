"""
WAY SDK sandbox environment.
"""

from __future__ import annotations

from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
)
from typing import (
    Any,
)

from sdk_python.async_client import (
    AsyncWAYClient,
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

from .fixtures import (
    create_async_transport,
    create_cache,
    create_config,
    create_metrics,
    create_settings,
    create_storage,
    create_transport,
    create_tracing,
    create_async_storage,
)


class SDKSandbox(
    AbstractContextManager
):
    """
    Sync isolated test sandbox.
    """

    def __init__(
        self,
        **config: Any,
    ) -> None:
        self.config = create_config(
            **config
        )

        self.settings = (
            create_settings()
        )

        self.transport = (
            create_transport()
        )

        self.cache = (
            create_cache()
        )

        self.metrics = (
            create_metrics()
        )

        self.tracing = (
            create_tracing()
        )

        self.storage = (
            create_storage(
                transport=self.transport,
                config=self.config,
            )
        )

        self.client = WAYClient(
            config=self.config,
            settings=self.settings,
            transport=self.transport,
            cache=self.cache,
            storage=self.storage,
            metrics=self.metrics,
            tracing=self.tracing,
        )

    def reset(self) -> None:
        """
        Reset sandbox state.
        """

        if hasattr(
            self.cache,
            "clear",
        ):
            self.cache.clear()

        if hasattr(
            self.transport,
            "reset",
        ):
            self.transport.reset()

        if hasattr(
            self.metrics,
            "reset",
        ):
            self.metrics.reset()

        if hasattr(
            self.tracing,
            "reset",
        ):
            self.tracing.reset()

    def close(self) -> None:
        """
        Close resources.
        """

        if hasattr(
            self.transport,
            "close",
        ):
            self.transport.close()

    def __enter__(
        self,
    ) -> "SDKSandbox":
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.close()


class AsyncSDKSandbox(
    AbstractAsyncContextManager
):
    """
    Async isolated test sandbox.
    """

    def __init__(
        self,
        **config: Any,
    ) -> None:
        self.config = create_config(
            **config
        )

        self.settings = (
            create_settings()
        )

        self.transport = (
            create_async_transport()
        )

        self.cache = (
            create_cache()
        )

        self.metrics = (
            create_metrics()
        )

        self.tracing = (
            create_tracing()
        )

        self.storage = (
            create_async_storage(
                transport=self.transport,
                config=self.config,
            )
        )

        self.client = (
            AsyncWAYClient(
                config=self.config,
                settings=self.settings,
                transport=self.transport,
                cache=self.cache,
                storage=self.storage,
                metrics=self.metrics,
                tracing=self.tracing,
            )
        )

    def reset(self) -> None:
        """
        Reset async sandbox.
        """

        if hasattr(
            self.cache,
            "clear",
        ):
            self.cache.clear()

        if hasattr(
            self.transport,
            "reset",
        ):
            self.transport.reset()

        if hasattr(
            self.metrics,
            "reset",
        ):
            self.metrics.reset()

        if hasattr(
            self.tracing,
            "reset",
        ):
            self.tracing.reset()

    async def close(
        self,
    ) -> None:
        """
        Close async resources.
        """

        if hasattr(
            self.transport,
            "close",
        ):
            result = (
                self.transport.close()
            )

            if hasattr(
                result,
                "__await__",
            ):
                await result

    async def __aenter__(
        self,
    ) -> "AsyncSDKSandbox":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        await self.close()


def sandbox(
    **config: Any,
) -> SDKSandbox:
    """
    Create sync sandbox.
    """
    return SDKSandbox(
        **config
    )


def async_sandbox(
    **config: Any,
) -> AsyncSDKSandbox:
    """
    Create async sandbox.
    """
    return AsyncSDKSandbox(
        **config
    )