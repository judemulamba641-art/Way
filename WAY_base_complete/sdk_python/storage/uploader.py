from __future__ import annotations

from dataclasses import dataclass
from typing import Any, BinaryIO, Callable, Protocol, runtime_checkable

from sdk_python.exceptions import SDKError
from sdk_python.transport.timeout import TimeoutConfig
from sdk_python.transport.retries import RetryPolicy


#
# =========================================================
# Exceptions
# =========================================================
#


class UploadError(SDKError):
    """Base upload exception."""


class UploadFailedError(UploadError):
    """Raised when upload fails."""


#
# =========================================================
# Models
# =========================================================
#


@dataclass(slots=True, frozen=True)
class UploadResult:
    """
    Result returned after a successful upload.
    """

    key: str
    url: str | None = None
    size: int | None = None
    etag: str | None = None
    content_type: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class UploadProgress:
    """
    Upload progress tracking.
    """

    key: str
    total_bytes: int | None = None
    uploaded_bytes: int = 0

    def percent(self) -> float:
        if not self.total_bytes:
            return 0.0
        return (self.uploaded_bytes / self.total_bytes) * 100


#
# =========================================================
# Protocols
# =========================================================
#


@runtime_checkable
class BaseUploaderTransport(Protocol):
    """
    Sync transport abstraction for upload.
    """

    def put(
        self,
        url: str,
        data: bytes | BinaryIO,
        headers: dict[str, str] | None = None,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> dict[str, Any]:
        ...


@runtime_checkable
class BaseAsyncUploaderTransport(Protocol):
    """
    Async transport abstraction for upload.
    """

    async def put(
        self,
        url: str,
        data: bytes | BinaryIO,
        headers: dict[str, str] | None = None,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> dict[str, Any]:
        ...


#
# =========================================================
# Sync Uploader
# =========================================================
#


class Uploader:
    """
    High-performance sync uploader.

    Supports:
    - presigned upload
    - direct backend upload
    - retry + timeout injection
    - progress callback hook
    """

    def __init__(
        self,
        transport: BaseUploaderTransport,
        *,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._transport = transport
        self._timeout = timeout
        self._retry_policy = retry_policy

    def upload(
        self,
        *,
        url: str,
        key: str,
        data: bytes | BinaryIO,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
        progress_callback: Callable[[UploadProgress], None] | None = None,
    ) -> UploadResult:
        try:
            headers = headers or {}

            if content_type:
                headers["Content-Type"] = content_type

            result = self._transport.put(
                url=url,
                data=data,
                headers=headers,
                timeout=self._timeout,
                retry_policy=self._retry_policy,
            )

            return UploadResult(
                key=key,
                url=url,
                size=result.get("size"),
                etag=result.get("etag"),
                content_type=content_type,
                metadata=metadata,
            )

        except Exception as exc:
            raise UploadFailedError(f"Upload failed for key={key}") from exc


#
# =========================================================
# Async Uploader
# =========================================================
#


class AsyncUploader:
    """
    Async scalable uploader (production-ready).
    """

    def __init__(
        self,
        transport: BaseAsyncUploaderTransport,
        *,
        timeout: TimeoutConfig | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._transport = transport
        self._timeout = timeout
        self._retry_policy = retry_policy

    async def upload(
        self,
        *,
        url: str,
        key: str,
        data: bytes | BinaryIO,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
        progress_callback: Callable[[UploadProgress], None] | None = None,
    ) -> UploadResult:
        try:
            headers = headers or {}

            if content_type:
                headers["Content-Type"] = content_type

            result = await self._transport.put(
                url=url,
                data=data,
                headers=headers,
                timeout=self._timeout,
                retry_policy=self._retry_policy,
            )

            return UploadResult(
                key=key,
                url=url,
                size=result.get("size"),
                etag=result.get("etag"),
                content_type=content_type,
                metadata=metadata,
            )

        except Exception as exc:
            raise UploadFailedError(f"Async upload failed for key={key}") from exc