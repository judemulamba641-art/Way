from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from .base import BaseModel


__all__ = [
    "UploadStatus",
    "UploadVisibility",
    "UploadChecksum",
    "UploadProgress",
    "UploadPart",
    "UploadMetadata",
    "Upload",
]


# =========================================================
# ENUMS
# =========================================================


class UploadStatus(StrEnum):
    """
    Upload lifecycle.
    """

    PENDING = "pending"
    PREPARING = "preparing"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class UploadVisibility(StrEnum):
    """
    File visibility.
    """

    PRIVATE = "private"
    INTERNAL = "internal"
    PUBLIC = "public"


# =========================================================
# SUPPORT MODELS
# =========================================================


@dataclass(slots=True, kw_only=True)
class UploadChecksum(BaseModel):
    """
    Integrity hashes.
    """

    md5: str = ""
    sha1: str = ""
    sha256: str = ""

    @property
    def available(self) -> bool:
        return bool(self.md5 or self.sha1 or self.sha256)


@dataclass(slots=True, kw_only=True)
class UploadProgress(BaseModel):
    """
    Progress tracking.
    """

    transferred: int = 0
    total: int = 0

    @property
    def percent(self) -> float:
        if self.total <= 0:
            return 0.0

        return round(
            (self.transferred / self.total) * 100,
            2,
        )

    @property
    def completed(self) -> bool:
        return (
            self.total > 0
            and self.transferred >= self.total
        )

    def update(self, value: int) -> "UploadProgress":
        return UploadProgress(
            transferred=max(0, value),
            total=self.total,
        )


@dataclass(slots=True, kw_only=True)
class UploadPart(BaseModel):
    """
    Multipart upload chunk.
    """

    number: int
    size: int

    etag: str = ""
    uploaded: bool = False

    @property
    def ready(self) -> bool:
        return self.uploaded and bool(self.etag)


@dataclass(slots=True, kw_only=True)
class UploadMetadata(BaseModel):
    """
    Arbitrary file metadata.
    """

    tags: dict[str, str] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)

    mime_type: str = ""

    def merge(
        self,
        *,
        tags: dict[str, str] | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> "UploadMetadata":
        merged_tags = dict(self.tags)
        merged_attrs = dict(self.attributes)

        if tags:
            merged_tags.update(tags)

        if attributes:
            merged_attrs.update(attributes)

        return UploadMetadata(
            tags=merged_tags,
            attributes=merged_attrs,
            mime_type=self.mime_type,
        )


# =========================================================
# MAIN MODEL
# =========================================================


@dataclass(slots=True, kw_only=True)
class Upload(BaseModel):
    """
    Storage upload model.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    filename: str
    key: str

    size: int = 0

    visibility: UploadVisibility = (
        UploadVisibility.PRIVATE
    )

    status: UploadStatus = UploadStatus.PENDING

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    checksum: UploadChecksum = field(
        default_factory=UploadChecksum
    )

    progress: UploadProgress = field(
        default_factory=UploadProgress
    )

    metadata: UploadMetadata = field(
        default_factory=UploadMetadata
    )

    parts: list[UploadPart] = field(
        default_factory=list
    )

    upload_url: str = ""
    public_url: str = ""

    error: str = ""

    # =====================================================
    # FILE INFO
    # =====================================================

    @property
    def extension(self) -> str:
        return Path(self.filename).suffix.lower()

    @property
    def is_public(self) -> bool:
        return (
            self.visibility
            is UploadVisibility.PUBLIC
        )

    @property
    def multipart(self) -> bool:
        return bool(self.parts)

    @property
    def completed(self) -> bool:
        return (
            self.status
            is UploadStatus.COMPLETED
        )

    # =====================================================
    # MUTATIONS
    # =====================================================

    def start(self) -> "Upload":
        return self._replace(
            status=UploadStatus.UPLOADING,
            error="",
        )

    def preparing(self) -> "Upload":
        return self._replace(
            status=UploadStatus.PREPARING,
        )

    def processing(self) -> "Upload":
        return self._replace(
            status=UploadStatus.PROCESSING,
        )

    def fail(
        self,
        message: str,
    ) -> "Upload":
        return self._replace(
            status=UploadStatus.FAILED,
            error=message,
        )

    def cancel(self) -> "Upload":
        return self._replace(
            status=UploadStatus.CANCELED,
        )

    def finish(
        self,
        *,
        public_url: str = "",
    ) -> "Upload":
        return self._replace(
            status=UploadStatus.COMPLETED,
            public_url=public_url
            or self.public_url,
            progress=UploadProgress(
                transferred=self.size,
                total=self.size,
            ),
        )

    def update_progress(
        self,
        transferred: int,
    ) -> "Upload":
        return self._replace(
            progress=UploadProgress(
                transferred=transferred,
                total=self.size,
            ),
        )

    def add_part(
        self,
        part: UploadPart,
    ) -> "Upload":
        updated = list(self.parts)
        updated.append(part)

        return self._replace(
            parts=updated,
        )

    # =====================================================
    # INTERNAL
    # =====================================================

    def _replace(
        self,
        **changes: Any,
    ) -> "Upload":
        payload = self.to_dict()
        payload.update(changes)

        payload["updated_at"] = datetime.now(
            timezone.utc
        )

        return Upload(**payload)

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def as_transport_payload(
        self,
    ) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "key": self.key,
            "size": self.size,
            "visibility": self.visibility.value,
            "mime_type": self.metadata.mime_type,
            "tags": self.metadata.tags,
            "attributes": self.metadata.attributes,
        }

    def __bool__(self) -> bool:
        return self.status not in {
            UploadStatus.FAILED,
            UploadStatus.CANCELED,
        }