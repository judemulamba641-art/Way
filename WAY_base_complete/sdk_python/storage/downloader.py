from __future__ import annotations

from dataclasses import dataclass
from typing import Any, BinaryIO, Callable, Protocol, runtime_checkable

from sdk_python.exceptions import SDKError
from sdk_python.transport.retries import RetryPolicy
from sdk_python.transport.timeout import TimeoutConfig


#
# =========================================================
# Exceptions
# =========================================================
#


class DownloadError(SDKError):
    """Base download error."""


class DownloadFailedError(DownloadError):
    """Raised when download fails."""


#
# =========================================================
# Models
# =========================================================
#


@dataclass(slots=True, frozen=True)
class DownloadResult:
    """
    Standard download result.
    """

    key: str
    data: bytes

    content_type: str | None = None
    etag: str | None = None
    size: int | None = None

    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class DownloadProgress:
    """
    Streaming download progress tracker.
    """

    key: str
    total_bytes: int | None = None
    downloaded_bytes: int = 0

    def percent(self) -> float:
        if not self.total_bytes:
            return 0.0
        return (self.downloaded_bytes / self.total_bytes) * 100


#
# =========================================================
# Transport Protocol
# =========================================================
#


@runtime_checkable
class BaseDownloaderTransport(Protocol):
    """
    Sync transport abstraction.
    """

    def get(
        self,
        url: str,
        *,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        ...


@runtime_checkable
class BaseAsyncDownloaderTransport(Protocol):
    """
    Async transport abstraction.
    """

    async def get(
        self,
        url: str,
        *,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        ...


#
# =========================================================
# Sync Downloader
# =========================================================
#


class Downloader:
    """
    Production-grade sync downloader.

    Supports:
    - presigned URLs
    - backend key-based download
    - retry + timeout injection
    - streaming-ready design (future)
    """

    def __init__(
        self,
        transport: BaseDownloaderTransport,
        *,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._transport = transport
        self._timeout = timeout
        self._retry_policy = retry_policy

    def download(
        self,
        *,
        url: str,
        key: str,
        stream: bool = False,
        progress_callback: Callable[[DownloadProgress], None] | None = None,
    ) -> DownloadResult:
        try:
            response = self._transport.get(
                url=url,
                timeout=self._timeout,
                retry_policy=self._retry_policy,
                stream=stream,
            )

            data = response["content"]

            return DownloadResult(
                key=key,
                data=data,
                content_type=response.get("headers", {}).get("content-type"),
                etag=response.get("headers", {}).get("etag"),
                size=response.get("size"),
                metadata=response.get("metadata"),
            )

        except Exception as exc:
            raise DownloadFailedError(f"Download failed for key={key}") from exc


#
# =========================================================
# Async Downloader
# =========================================================
#


class AsyncDownloader:
    """
    Async scalable downloader (production-ready).
    """

    def __init__(
        self,
        transport: BaseAsyncDownloaderTransport,
        *,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._transport = transport
        self._timeout = timeout
        self._retry_policy = retry_policy

    async def download(
        self,
        *,
        url: str,
        key: str,
        stream: bool = False,
        progress_callback: Callable[[DownloadProgress], None] | None = None,
    ) -> DownloadResult:
        try:
            response = await self._transport.get(
                url=url,
                timeout=self._timeout,
                retry_policy=self._retry_policy,
                stream=stream,
            )

            data = response["content"]

            return DownloadResult(
                key=key,
                data=data,
                content_type=response.get("headers", {}).get("content-type"),
                etag=response.get("headers", {}).get("etag"),
                size=response.get("size"),
                metadata=response.get("metadata"),
            )

        except Exception as exc:
            raise DownloadFailedError(f"Async download failed for key={key}") from exc