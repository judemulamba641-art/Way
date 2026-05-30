# sdk_python/auth/base.py

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, runtime_checkable, Mapping, Generic, TypeVar
import time


from sdk_python.exceptions import SDKException
from sdk_python.utils.typing import JSONDict


T = TypeVar("T")


class AuthError(SDKException):
    """Raised when authentication fails at SDK level."""


class AuthType(str, Enum):
    """
    Supported authentication strategies.
    Designed to be extensible without breaking API.
    """
    API_KEY = "api_key"
    JWT = "jwt"
    TOKEN = "token"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class AuthCredentials:
    """
    Immutable credentials container.

    This is the single source of truth passed across auth strategies.
    """
    auth_type: AuthType
    values: JSONDict = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def require(self, key: str) -> Any:
        if key not in self.values:
            raise AuthError(f"Missing required credential field: {key}")
        return self.values[key]


@dataclass(frozen=True, slots=True)
class AuthContext:
    """
    Runtime context for authentication execution.

    Contains request-level metadata used for signing or token generation.
    """
    service: str
    endpoint: str
    method: str = "GET"
    timestamp: float = field(default_factory=lambda: time.time())
    metadata: JSONDict = field(default_factory=dict)

    def as_dict(self) -> JSONDict:
        return {
            "service": self.service,
            "endpoint": self.endpoint,
            "method": self.method,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class AuthResult:
    """
    Output of any authentication process.

    Can be used by transport layer to inject headers or query params.
    """
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    signature: Optional[str] = None
    expires_at: Optional[float] = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() >= self.expires_at


@runtime_checkable
class AuthStrategy(Protocol):
    """
    Protocol for all authentication strategies.

    Allows both class-based and duck-typed implementations.
    """

    def authenticate(self, credentials: AuthCredentials, context: AuthContext) -> AuthResult:
        ...

    def refresh(self, credentials: AuthCredentials, context: AuthContext) -> AuthResult:
        ...


class BaseAuthStrategy(ABC):
    """
    Base class for all authentication strategies.

    Enforces a consistent contract across API key, JWT, token, etc.
    """

    auth_type: AuthType = AuthType.NONE

    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def authenticate(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        """
        Entry point for authentication.
        Validates state then delegates to concrete implementation.
        """
        if not self._enabled:
            raise AuthError("Authentication strategy is disabled")

        if credentials.auth_type != self.auth_type:
            raise AuthError(
                f"Invalid auth type. Expected {self.auth_type}, got {credentials.auth_type}"
            )

        return self._authenticate(credentials, context)

    @abstractmethod
    def _authenticate(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        """
        Concrete implementation must produce authentication result.
        """
        raise NotImplementedError

    def refresh(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        """
        Optional refresh mechanism for long-lived auth systems.

        Default behavior: re-authenticate.
        """
        return self.authenticate(credentials, context)

    def build_headers(self, result: AuthResult) -> Dict[str, str]:
        """
        Hook for transport layer header injection.
        Can be overridden for custom schemes.
        """
        return dict(result.headers)

    def build_query_params(self, result: AuthResult) -> Dict[str, str]:
        """
        Hook for transport layer query param injection.
        """
        return dict(result.query_params)


class StatelessAuthStrategy(BaseAuthStrategy):
    """
    Convenience base class for stateless auth (API keys, simple tokens).

    No refresh logic required.
    """

    def refresh(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        return self.authenticate(credentials, context)