"""
WAY SDK - Authentication Module

This module provides a unified authentication layer for all SDK operations.

Supported authentication strategies:
- API Key authentication
- JWT authentication
- Token-based authentication
- Refresh-capable authentication flows

Architecture principle:
All strategies implement a shared BaseAuthStrategy contract,
ensuring full interchangeability at transport level.
"""

from __future__ import annotations

from sdk_python.auth.base import (
    AuthType,
    AuthCredentials,
    AuthContext,
    AuthResult,
    AuthStrategy,
    BaseAuthStrategy,
    StatelessAuthStrategy,
    AuthError,
)

from sdk_python.auth.api_key import APIKeyAuth
from sdk_python.auth.jwt import JWTAuth
from sdk_python.auth.token import TokenAuth
from sdk_python.auth.refresh import RefreshTokenAuth


__all__ = [
    # Core types
    "AuthType",
    "AuthCredentials",
    "AuthContext",
    "AuthResult",
    "AuthStrategy",
    "BaseAuthStrategy",
    "StatelessAuthStrategy",
    "AuthError",

    # Implementations
    "APIKeyAuth",
    "JWTAuth",
    "TokenAuth",
    "RefreshTokenAuth",
]


class AuthManager:
    """
    Central registry and factory for authentication strategies.

    This class acts as the single entry point for SDK authentication selection.
    """

    _strategies: dict[AuthType, type[BaseAuthStrategy]] = {}

    @classmethod
    def register(cls, auth_type: AuthType, strategy: type[BaseAuthStrategy]) -> None:
        """
        Register a new authentication strategy dynamically.
        """
        cls._strategies[auth_type] = strategy

    @classmethod
    def create(cls, auth_type: AuthType, **kwargs) -> BaseAuthStrategy:
        """
        Create an authentication strategy instance.

        Raises:
            AuthError: If strategy is not registered.
        """
        if auth_type not in cls._strategies:
            raise AuthError(f"No auth strategy registered for type: {auth_type}")

        return cls._strategies[auth_type](**kwargs)

    @classmethod
    def available_strategies(cls) -> list[AuthType]:
        """
        Return list of available authentication types.
        """
        return list(cls._strategies.keys())


# Auto-register default strategies (safe import-time registration)
AuthManager.register(AuthType.API_KEY, APIKeyAuth)
AuthManager.register(AuthType.JWT, JWTAuth)
AuthManager.register(AuthType.TOKEN, TokenAuth)
AuthManager.register(AuthType.NONE, StatelessAuthStrategy)