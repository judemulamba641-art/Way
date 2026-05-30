# sdk_python/auth/refresh.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol
import time

from sdk_python.auth.base import (
    AuthCredentials,
    AuthContext,
    AuthResult,
    AuthType,
    AuthError,
)


# ----------------------------
# REFRESH STRATEGY CONTRACT
# ----------------------------

class RefreshStrategy(Protocol):
    """
    Contract for all refresh implementations.

    Allows:
    - JWT refresh
    - Token refresh
    - OAuth refresh
    - future session rotation systems
    """

    def refresh(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        ...


# ----------------------------
# REFRESH STATE MODEL
# ----------------------------

@dataclass(frozen=True, slots=True)
class RefreshState:
    """
    Internal refresh lifecycle state.

    This is used for:
    - token rotation tracking
    - expiry coordination
    - refresh eligibility checks
    """

    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[float]
    rotated_at: float

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() >= self.expires_at

    def needs_refresh(self, buffer_seconds: int = 60) -> bool:
        """
        Determines if token should be refreshed proactively.
        """
        if self.expires_at is None:
            return False
        return time.time() >= (self.expires_at - buffer_seconds)


# ----------------------------
# REFRESH MANAGER CORE
# ----------------------------

class RefreshManager:
    """
    Central refresh orchestration layer.

    Responsibilities:
    - token lifecycle management
    - refresh decision logic
    - delegation to auth strategies
    """

    def __init__(self) -> None:
        self._state_store: Dict[str, RefreshState] = {}

    # ----------------------------
    # STATE REGISTRATION
    # ----------------------------

    def register_state(
        self,
        key: str,
        state: RefreshState
    ) -> None:
        """
        Register or update token state.
        """
        self._state_store[key] = state

    def get_state(self, key: str) -> Optional[RefreshState]:
        """
        Retrieve stored refresh state.
        """
        return self._state_store.get(key)

    def invalidate(self, key: str) -> None:
        """
        Force invalidate a token state.
        """
        self._state_store.pop(key, None)

    # ----------------------------
    # REFRESH DECISION ENGINE
    # ----------------------------

    def should_refresh(self, key: str, buffer_seconds: int = 60) -> bool:
        state = self.get_state(key)
        if not state:
            return False
        return state.needs_refresh(buffer_seconds)

    # ----------------------------
    # REFRESH EXECUTION
    # ----------------------------

    def refresh(
        self,
        key: str,
        credentials: AuthCredentials,
        context: AuthContext,
        strategy: RefreshStrategy
    ) -> AuthResult:
        """
        Execute refresh flow using injected auth strategy.
        """

        state = self.get_state(key)

        if not state:
            raise AuthError(f"No refresh state found for key: {key}")

        if not state.refresh_token:
            raise AuthError("No refresh token available for this session")

        # enrich credentials with refresh context
        enriched_values = dict(credentials.values)
        enriched_values["refresh_token"] = state.refresh_token

        enriched_credentials = AuthCredentials(
            auth_type=credentials.auth_type,
            values=enriched_values
        )

        result = strategy.refresh(enriched_credentials, context)

        # update internal state if possible
        self._update_state(key, result, state)

        return result

    # ----------------------------
    # INTERNAL STATE UPDATE
    # ----------------------------

    def _update_state(
        self,
        key: str,
        result: AuthResult,
        old_state: RefreshState
    ) -> None:

        new_expiry = result.expires_at or old_state.expires_at

        new_state = RefreshState(
            access_token=result.signature or old_state.access_token,
            refresh_token=old_state.refresh_token,
            expires_at=new_expiry,
            rotated_at=time.time(),
        )

        self._state_store[key] = new_state