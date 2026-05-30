from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from sdk_python.exceptions import SDKError
from sdk_python.transport.serializer import Serializer


#
# =========================================================
# Exceptions
# =========================================================
#


class PresignedError(SDKError):
    """Base presigned storage exception."""


class PresignedExpiredError(PresignedError):
    """Raised when a presigned URL is expired."""


#
# =========================================================
# Models
# =========================================================
#


@dataclass(slots=True, frozen=True)
class PresignedUpload:
    """
    Presigned upload URL + metadata.

    Returned by backend before uploading directly
    to object storage.
    """

    url: str
    method: str = "PUT"

    headers: Mapping[str, str] = field(default_factory=dict)
    fields: Mapping[str, str] = field(default_factory=dict)

    file_key: str | None = None
    bucket: str | None = None

    expires_at: datetime | None = None
    content_type: str | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False

        return datetime.now(timezone.utc) >= self.expires_at

    def ensure_valid(self) -> None:
        if self.is_expired():
            raise PresignedExpiredError(
                f"Presigned upload expired for key={self.file_key!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "method": self.method,
            "headers": dict(self.headers),
            "fields": dict(self.fields),
            "file_key": self.file_key,
            "bucket": self.bucket,
            "expires_at": self.expires_at.isoformat()
            if self.expires_at
            else None,
            "content_type": self.content_type,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True, frozen=True)
class PresignedDownload:
    """
    Presigned download URL.
    """

    url: str
    method: str = "GET"

    headers: Mapping[str, str] = field(default_factory=dict)

    file_key: str | None = None
    bucket: str | None = None

    expires_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False

        return datetime.now(timezone.utc) >= self.expires_at

    def ensure_valid(self) -> None:
        if self.is_expired():
            raise PresignedExpiredError(
                f"Presigned download expired for key={self.file_key!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "method": self.method,
            "headers": dict(self.headers),
            "file_key": self.file_key,
            "bucket": self.bucket,
            "expires_at": self.expires_at.isoformat()
            if self.expires_at
            else None,
            "metadata": dict(self.metadata),
        }


#
# =========================================================
# Service
# =========================================================
#


class PresignedService:
    """
    Sync helper for presigned storage endpoints.

    Example:
        sdk.storage.presigned.upload(...)
        sdk.storage.presigned.download(...)
    """

    def __init__(
        self,
        *,
        client: Any,
        serializer: Serializer | None = None,
    ) -> None:
        self._client = client
        self._serializer = serializer or Serializer()

    #
    # ---------------------------------------------
    # Upload
    # ---------------------------------------------
    #

    def upload(
        self,
        *,
        file_name: str,
        content_type: str | None = None,
        size: int | None = None,
        bucket: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        expires_in: int | None = None,
    ) -> PresignedUpload:
        payload = {
            "file_name": file_name,
            "content_type": content_type,
            "size": size,
            "bucket": bucket,
            "metadata": dict(metadata or {}),
            "expires_in": expires_in,
        }

        data = self._client.post(
            "/storage/presigned/upload",
            json=payload,
        )

        return self._build_upload(data)

    #
    # ---------------------------------------------
    # Download
    # ---------------------------------------------
    #

    def download(
        self,
        *,
        file_key: str,
        bucket: str | None = None,
        expires_in: int | None = None,
    ) -> PresignedDownload:
        payload = {
            "file_key": file_key,
            "bucket": bucket,
            "expires_in": expires_in,
        }

        data = self._client.post(
            "/storage/presigned/download",
            json=payload,
        )

        return self._build_download(data)

    #
    # ---------------------------------------------
    # Builders
    # ---------------------------------------------
    #

    def _build_upload(
        self,
        data: Mapping[str, Any],
    ) -> PresignedUpload:
        expires_at = self._parse_expiry(data)

        return PresignedUpload(
            url=data["url"],
            method=data.get("method", "PUT"),
            headers=data.get("headers", {}),
            fields=data.get("fields", {}),
            file_key=data.get("file_key"),
            bucket=data.get("bucket"),
            expires_at=expires_at,
            content_type=data.get("content_type"),
            metadata=data.get("metadata", {}),
        )

    def _build_download(
        self,
        data: Mapping[str, Any],
    ) -> PresignedDownload:
        expires_at = self._parse_expiry(data)

        return PresignedDownload(
            url=data["url"],
            method=data.get("method", "GET"),
            headers=data.get("headers", {}),
            file_key=data.get("file_key"),
            bucket=data.get("bucket"),
            expires_at=expires_at,
            metadata=data.get("metadata", {}),
        )

    def _parse_expiry(
        self,
        data: Mapping[str, Any],
    ) -> datetime | None:
        value = data.get("expires_at")

        if value:
            return datetime.fromisoformat(value)

        seconds = data.get("expires_in")

        if seconds:
            return datetime.now(timezone.utc) + timedelta(
                seconds=int(seconds)
            )

        return None


#
# =========================================================
# Async Service
# =========================================================
#


class AsyncPresignedService:
    """
    Async variant.
    """

    def __init__(
        self,
        *,
        client: Any,
        serializer: Serializer | None = None,
    ) -> None:
        self._client = client
        self._serializer = serializer or Serializer()

    async def upload(
        self,
        *,
        file_name: str,
        content_type: str | None = None,
        size: int | None = None,
        bucket: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        expires_in: int | None = None,
    ) -> PresignedUpload:
        payload = {
            "file_name": file_name,
            "content_type": content_type,
            "size": size,
            "bucket": bucket,
            "metadata": dict(metadata or {}),
            "expires_in": expires_in,
        }

        data = await self._client.post(
            "/storage/presigned/upload",
            json=payload,
        )

        return PresignedService(
            client=self._client,
            serializer=self._serializer,
        )._build_upload(data)

    async def download(
        self,
        *,
        file_key: str,
        bucket: str | None = None,
        expires_in: int | None = None,
    ) -> PresignedDownload:
        payload = {
            "file_key": file_key,
            "bucket": bucket,
            "expires_in": expires_in,
        }

        data = await self._client.post(
            "/storage/presigned/download",
            json=payload,
        )

        return PresignedService(
            client=self._client,
            serializer=self._serializer,
        )._build_download(data)