from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from .base import BaseModel


__all__ = [
    "UserStatus",
    "UserRole",
    "UserProfile",
    "UserPreferences",
    "UserPermissions",
    "UserMetadata",
    "User",
]


# =========================================================
# ENUMS
# =========================================================


class UserStatus(StrEnum):
    """
    Account lifecycle.
    """

    ACTIVE = "active"
    PENDING = "pending"
    DISABLED = "disabled"
    BLOCKED = "blocked"
    DELETED = "deleted"


class UserRole(StrEnum):
    """
    Authorization role.
    """

    USER = "user"
    ADMIN = "admin"
    STAFF = "staff"
    SYSTEM = "system"
    SERVICE = "service"


# =========================================================
# SUPPORT MODELS
# =========================================================


@dataclass(slots=True, kw_only=True)
class UserProfile(BaseModel):
    """
    Public profile.
    """

    username: str = ""
    email: str = ""

    first_name: str = ""
    last_name: str = ""

    display_name: str = ""
    avatar_url: str = ""

    phone: str = ""
    locale: str = "en"

    timezone: str = "UTC"

    bio: str = ""

    @property
    def full_name(self) -> str:
        value = (
            f"{self.first_name} {self.last_name}"
        ).strip()

        return value or self.display_name

    @property
    def identity(self) -> str:
        return (
            self.display_name
            or self.username
            or self.email
        )


@dataclass(slots=True, kw_only=True)
class UserPreferences(BaseModel):
    """
    Runtime preferences.
    """

    theme: str = "system"
    language: str = "en"

    notifications: bool = True
    email_notifications: bool = True

    realtime_enabled: bool = True

    values: dict[str, Any] = field(
        default_factory=dict
    )

    def merge(
        self,
        values: dict[str, Any],
    ) -> "UserPreferences":
        merged = dict(self.values)
        merged.update(values)

        return UserPreferences(
            theme=self.theme,
            language=self.language,
            notifications=self.notifications,
            email_notifications=(
                self.email_notifications
            ),
            realtime_enabled=(
                self.realtime_enabled
            ),
            values=merged,
        )


@dataclass(slots=True, kw_only=True)
class UserPermissions(BaseModel):
    """
    Access control.
    """

    scopes: set[str] = field(
        default_factory=set
    )

    roles: set[str] = field(
        default_factory=set
    )

    admin: bool = False

    def has(
        self,
        scope: str,
    ) -> bool:
        return scope in self.scopes

    def has_any(
        self,
        *scopes: str,
    ) -> bool:
        return any(
            scope in self.scopes
            for scope in scopes
        )

    def add(
        self,
        *scopes: str,
    ) -> "UserPermissions":
        merged = set(self.scopes)
        merged.update(scopes)

        return UserPermissions(
            scopes=merged,
            roles=set(self.roles),
            admin=self.admin,
        )


@dataclass(slots=True, kw_only=True)
class UserMetadata(BaseModel):
    """
    Internal metadata.
    """

    tags: dict[str, str] = field(
        default_factory=dict
    )

    attributes: dict[str, Any] = field(
        default_factory=dict
    )

    labels: list[str] = field(
        default_factory=list
    )

    def merge(
        self,
        *,
        tags: dict[str, str] | None = None,
        attributes: dict[str, Any] | None = None,
        labels: list[str] | None = None,
    ) -> "UserMetadata":
        merged_tags = dict(self.tags)
        merged_attrs = dict(self.attributes)
        merged_labels = list(self.labels)

        if tags:
            merged_tags.update(tags)

        if attributes:
            merged_attrs.update(attributes)

        if labels:
            merged_labels.extend(labels)

        return UserMetadata(
            tags=merged_tags,
            attributes=merged_attrs,
            labels=merged_labels,
        )


# =========================================================
# MAIN MODEL
# =========================================================


@dataclass(slots=True, kw_only=True)
class User(BaseModel):
    """
    WAY user model.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: UserStatus = (
        UserStatus.ACTIVE
    )

    role: UserRole = (
        UserRole.USER
    )

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

    last_seen_at: datetime | None = None

    verified: bool = False

    profile: UserProfile = field(
        default_factory=UserProfile
    )

    preferences: UserPreferences = field(
        default_factory=UserPreferences
    )

    permissions: UserPermissions = field(
        default_factory=UserPermissions
    )

    metadata: UserMetadata = field(
        default_factory=UserMetadata
    )

    # =====================================================
    # STATE
    # =====================================================

    @property
    def is_active(self) -> bool:
        return (
            self.status
            is UserStatus.ACTIVE
        )

    @property
    def is_admin(self) -> bool:
        return (
            self.role is UserRole.ADMIN
            or self.permissions.admin
        )

    @property
    def identity(self) -> str:
        return self.profile.identity

    # =====================================================
    # ACTIONS
    # =====================================================

    def verify(self) -> "User":
        return self._replace(
            verified=True,
        )

    def touch(self) -> "User":
        now = datetime.now(
            timezone.utc
        )

        return self._replace(
            last_seen_at=now,
        )

    def disable(self) -> "User":
        return self._replace(
            status=UserStatus.DISABLED,
        )

    def block(self) -> "User":
        return self._replace(
            status=UserStatus.BLOCKED,
        )

    def activate(self) -> "User":
        return self._replace(
            status=UserStatus.ACTIVE,
        )

    def set_role(
        self,
        role: UserRole,
    ) -> "User":
        return self._replace(
            role=role,
        )

    # =====================================================
    # INTERNAL
    # =====================================================

    def _replace(
        self,
        **changes: Any,
    ) -> "User":
        payload = self.to_dict()
        payload.update(changes)

        payload["updated_at"] = (
            datetime.now(
                timezone.utc
            )
        )

        return User(**payload)

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def as_transport_payload(
        self,
    ) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": (
                self.profile.username
            ),
            "email": (
                self.profile.email
            ),
            "display_name": (
                self.profile.display_name
            ),
            "role": (
                self.role.value
            ),
            "verified": (
                self.verified
            ),
        }

    def __bool__(self) -> bool:
        return self.is_active