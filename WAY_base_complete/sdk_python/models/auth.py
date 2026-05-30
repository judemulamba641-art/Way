from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class AccessToken:
    """
    Access token payload.
    """

    token: str
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    issued_at: datetime = field(default_factory=_utc_now)
    scopes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False

        return _utc_now() >= self.expires_at

    def as_header(self) -> dict[str, str]:
        return {
            "Authorization": f"{self.token_type} {self.token}",
        }


@dataclass(slots=True)
class RefreshToken:
    """
    Refresh token payload.
    """

    token: str
    expires_at: Optional[datetime] = None

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False

        return _utc_now() >= self.expires_at


@dataclass(slots=True)
class SessionIdentity:
    """
    Authenticated identity/session.
    """

    id: str
    subject: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(
        cls,
        payload: Optional[Mapping[str, Any]],
    ) -> Optional["SessionIdentity"]:
        if not payload:
            return None

        return cls(
            id=str(payload.get("id", "")),
            subject=payload.get("subject"),
            email=payload.get("email"),
            username=payload.get("username"),
            metadata=dict(payload.get("metadata") or {}),
        )


@dataclass(slots=True)
class AuthToken:
    """
    Combined auth token state.
    """

    access: AccessToken
    refresh: Optional[RefreshToken] = None

    @property
    def expired(self) -> bool:
        return self.access.expired

    @property
    def authorization(self) -> dict[str, str]:
        return self.access.as_header()


@dataclass(slots=True)
class AuthState:
    """
    Full authentication state.
    """

    authenticated: bool = False
    token: Optional[AuthToken] = None
    identity: Optional[SessionIdentity] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=_utc_now)

    @property
    def access_token(self) -> Optional[str]:
        if not self.token:
            return None

        return self.token.access.token

    @property
    def refresh_token(self) -> Optional[str]:
        if not self.token or not self.token.refresh:
            return None

        return self.token.refresh.token

    @property
    def expired(self) -> bool:
        if not self.token:
            return True

        return self.token.expired

    def headers(self) -> dict[str, str]:
        if not self.token:
            return {}

        return self.token.authorization

    def touch(self) -> None:
        self.updated_at = _utc_now()

    def clear(self) -> None:
        self.authenticated = False
        self.token = None
        self.identity = None
        self.metadata.clear()
        self.touch()