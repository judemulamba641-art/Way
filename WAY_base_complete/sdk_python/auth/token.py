# sdk_python/auth/token.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import time

from sdk_python.auth.base import (
    BaseAuthStrategy,
    AuthType,
    AuthCredentials,
    AuthContext,
    AuthResult,
    AuthError,
)


@dataclass(frozen=True, slots=True)
class TokenData:
    """
    Internal normalized token structure.

    This abstraction allows:
    - API token
    - session token
    - bearer token
    - future opaque tokens
    """
    token: str
    token_type: str = "Bearer"
    expires_at: Optional[float] = None
    refresh_token: Optional[str] = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() >= self.expires_at


class TokenAuth(BaseAuthStrategy):
    """
    Token-based authentication strategy.

    Supports:
    - bearer tokens
    - session tokens
    - opaque tokens
    - optional refresh token linkage

    Designed for:
    - stateless API authentication
    - session-based authentication
    - external identity providers
    """

    auth_type: AuthType = AuthType.TOKEN

    def _authenticate(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        """
        Build authentication result from token credentials.
        """

        token_data = self._extract_token(credentials)

        headers = {
            "Authorization": f"{token_data.token_type} {token_data.token}"
        }

        return AuthResult(
            headers=headers,
            expires_at=token_data.expires_at,
        )

    def refresh(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        """
        Refresh token if refresh_token exists.

        In real production systems:
        - this would call identity provider
        - or token endpoint
        """

        token_data = self._extract_token(credentials)

        if not token_data.refresh_token:
            # fallback: re-auth with same token
            return self.authenticate(credentials, context)

        # Simulated refresh flow (ready for real HTTP integration later)
        new_expiry = time.time() + 3600

        new_token_data = TokenData(
            token=token_data.token,
            token_type=token_data.token_type,
            expires_at=new_expiry,
            refresh_token=token_data.refresh_token,
        )

        return AuthResult(
            headers={
                "Authorization": f"{new_token_data.token_type} {new_token_data.token}"
            },
            expires_at=new_token_data.expires_at,
        )

    def _extract_token(self, credentials: AuthCredentials) -> TokenData:
        """
        Normalize credentials into TokenData structure.
        """

        token = credentials.require("token")

        token_type = credentials.get("token_type", "Bearer")
        expires_at = credentials.get("expires_at")
        refresh_token = credentials.get("refresh_token")

        if not isinstance(token, str):
            raise AuthError("Token must be a string")

        if expires_at is not None and not isinstance(expires_at, (int, float)):
            raise AuthError("expires_at must be a timestamp (int or float)")

        return TokenData(
            token=token,
            token_type=token_type,
            expires_at=expires_at,
            refresh_token=refresh_token,
        )