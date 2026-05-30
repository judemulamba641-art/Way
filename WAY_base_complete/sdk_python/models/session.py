from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from .base import BaseModel


__all__ = [
    "SessionStatus",
    "SessionScope",
    "SessionMetadata",
    "SessionDevice",
    "SessionTokens",
    "Session",
]


# =========================================================
# ENUMS
# =========================================================


class SessionStatus(StrEnum):
    """
    Current lifecycle state of a session.
    """

    ACTIVE = "active"
    REFRESHING = "refreshing"
    EXPIRED = "expired"
    REVOKED = "revoked"
    TERMINATED = "terminated"


class SessionScope(StrEnum):
    """
    Access scope.
    """

    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    SERVICE = "service"


# =========================================================
# SUPPORT MODELS
# =========================================================


@dataclass(slots=True, kw_only=True)
class SessionMetadata(BaseModel):
    """
    Arbitrary metadata.
    """

    labels: list[str] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)

    def merge(
        self,
        *,
        labels: list[str] | None = None,
        tags: dict[str, str] | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> "SessionMetadata":
        merged_labels = list(self.labels)
        merged_tags = dict(self.tags)
        merged_attrs = dict(self.attributes)

        if labels:
            merged_labels.extend(labels)

        if tags:
            merged_tags.update(tags)

        if attributes:
            merged_attrs.update(attributes)

        return SessionMetadata(
            labels=merged_labels,
            tags=merged_tags,
            attributes=merged_attrs,
        )


@dataclass(slots=True, kw_only=True)
class SessionDevice(BaseModel):
    """
    Device/client descriptor.
    """

    id: str = ""
    name: str = ""
    platform: str = ""
    version: str = ""
    ip_address: str = ""
    location: str = ""
    user_agent: str = ""

    @property
    def is_known(self) -> bool:
        return bool(self.id)


@dataclass(slots=True, kw_only=True)
class SessionTokens(BaseModel):
    """
    Auth token bundle.
    """

    access_token: str = ""
    refresh_token: str = ""
    id_token: str = ""

    access_expires_at: datetime | None = None
    refresh_expires_at: datetime | None = None

    def has_access(self) -> bool:
        return bool(self.access_token)

    def has_refresh(self) -> bool:
        return bool(self.refresh_token)

    def access_expired(self) -> bool:
        if self.access_expires_at is None:
            return False

        return datetime.now(timezone.utc) >= self.access_expires_at

    def refresh_expired(self) -> bool:
        if self.refresh_expires_at is None:
            return False

        return datetime.now(timezone.utc) >= self.refresh_expires_at

    def clear(self) -> "SessionTokens":
        return SessionTokens()


# =========================================================
# MAIN MODEL
# =========================================================


@dataclass(slots=True, kw_only=True)
class Session(BaseModel):
    """
    Authenticated runtime session.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    user_id: str = ""

    scope: SessionScope = SessionScope.USER
    status: SessionStatus = SessionStatus.ACTIVE

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    expires_at: datetime | None = None
    last_seen_at: datetime | None = None

    tokens: SessionTokens = field(default_factory=SessionTokens)
    device: SessionDevice = field(default_factory=SessionDevice)
    metadata: SessionMetadata = field(default_factory=SessionMetadata)

    # -----------------------------------------------------
    # STATE
    # -----------------------------------------------------

    @property
    def is_active(self) -> bool:
        return self.status is SessionStatus.ACTIVE

    @property
    def is_expired(self) -> bool:
        if self.status is SessionStatus.EXPIRED:
            return True

        if self.expires_at is None:
            return False

        return datetime.now(timezone.utc) >= self.expires_at

    @property
    def is_refreshable(self) -> bool:
        return (
            self.is_active
            and self.tokens.has_refresh()
            and not self.tokens.refresh_expired()
        )

    # -----------------------------------------------------
    # ACTIONS
    # -----------------------------------------------------

    def touch(self) -> "Session":
        now = datetime.now(timezone.utc)

        return Session(
            id=self.id,
            user_id=self.user_id,
            scope=self.scope,
            status=self.status,
            created_at=self.created_at,
            updated_at=now,
            expires_at=self.expires_at,
            last_seen_at=now,
            tokens=self.tokens,
            device=self.device,
            metadata=self.metadata,
        )

    def with_tokens(
        self,
        tokens: SessionTokens,
    ) -> "Session":
        return Session(
            id=self.id,
            user_id=self.user_id,
            scope=self.scope,
            status=self.status,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            expires_at=self.expires_at,
            last_seen_at=self.last_seen_at,
            tokens=tokens,
            device=self.device,
            metadata=self.metadata,
        )

    def expire(self) -> "Session":
        return Session(
            id=self.id,
            user_id=self.user_id,
            scope=self.scope,
            status=SessionStatus.EXPIRED,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            expires_at=self.expires_at,
            last_seen_at=self.last_seen_at,
            tokens=self.tokens,
            device=self.device,
            metadata=self.metadata,
        )

    def revoke(self) -> "Session":
        return Session(
            id=self.id,
            user_id=self.user_id,
            scope=self.scope,
            status=SessionStatus.REVOKED,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            expires_at=self.expires_at,
            last_seen_at=self.last_seen_at,
            tokens=self.tokens.clear(),
            device=self.device,
            metadata=self.metadata,
        )

    def terminate(self) -> "Session":
        return Session(
            id=self.id,
            user_id=self.user_id,
            scope=self.scope,
            status=SessionStatus.TERMINATED,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            expires_at=self.expires_at,
            last_seen_at=self.last_seen_at,
            tokens=self.tokens.clear(),
            device=self.device,
            metadata=self.metadata,
        )

    # -----------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------

    def to_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}

        if self.tokens.access_token:
            headers["Authorization"] = (
                f"Bearer {self.tokens.access_token}"
            )

        headers["X-Session-ID"] = self.id

        return headers

    def __bool__(self) -> bool:
        return self.is_active and not self.is_expired