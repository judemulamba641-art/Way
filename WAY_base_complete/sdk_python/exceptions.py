"""
WAY Python SDK exception hierarchy.

Enterprise-grade exception model for:

- transport
- authentication
- authorization
- validation
- serialization
- rate limiting
- storage
- websocket
- cache
- configuration

Goals:
- consistent errors
- structured diagnostics
- typed hierarchy
- scalable extensions
- clean exception handling
- production telemetry friendly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ErrorContext:
    """
    Structured error context.

    Useful for:
    - logging
    - telemetry
    - debugging
    - retries
    """

    code: str | None = None
    detail: str | None = None
    status_code: int | None = None
    request_id: str | None = None
    endpoint: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize context.
        """
        return {
            "code": self.code,
            "detail": self.detail,
            "status_code": self.status_code,
            "request_id": self.request_id,
            "endpoint": self.endpoint,
            "payload": dict(self.payload),
        }


class SDKError(Exception):
    """
    Base SDK exception.
    """

    default_message = "WAY SDK error."

    def __init__(
        self,
        message: str | None = None,
        *,
        context: ErrorContext | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.context = context
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """
        Structured export.
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "context": (
                self.context.to_dict()
                if self.context
                else None
            ),
        }

    def __str__(self) -> str:
        return self.message


# =========================================================
# Configuration
# =========================================================


class ConfigurationError(SDKError):
    """
    Invalid SDK configuration.
    """

    default_message = "Invalid SDK configuration."


# =========================================================
# Transport
# =========================================================


class TransportError(SDKError):
    """
    Base transport error.
    """

    default_message = "Transport error."


class NetworkError(TransportError):
    """
    Network communication failure.
    """

    default_message = "Network error."


class TimeoutError(TransportError):
    """
    Request timeout.
    """

    default_message = "Request timeout."


class SerializationError(TransportError):
    """
    Payload serialization failure.
    """

    default_message = "Serialization error."


class PaginationError(TransportError):
    """
    Pagination failure.
    """

    default_message = "Pagination error."


# =========================================================
# API
# =========================================================


class WayAPIError(SDKError):
    """
    Base API failure.
    """

    default_message = "WAY API request failed."


class BadRequestError(WayAPIError):
    """
    HTTP 400.
    """

    default_message = "Bad request."


class AuthenticationError(WayAPIError):
    """
    HTTP 401.
    """

    default_message = "Authentication failed."


class AuthorizationError(WayAPIError):
    """
    HTTP 403.
    """

    default_message = "Permission denied."


class ResourceNotFoundError(WayAPIError):
    """
    HTTP 404.
    """

    default_message = "Resource not found."


class ConflictError(WayAPIError):
    """
    HTTP 409.
    """

    default_message = "Resource conflict."


class RateLimitError(WayAPIError):
    """
    HTTP 429.
    """

    default_message = "Rate limit exceeded."


class ServerError(WayAPIError):
    """
    HTTP 5xx.
    """

    default_message = "Server error."


# =========================================================
# Validation
# =========================================================


class ValidationError(SDKError):
    """
    Validation failure.
    """

    default_message = "Validation failed."


# =========================================================
# Realtime / websocket
# =========================================================


class RealtimeError(SDKError):
    """
    Realtime transport failure.
    """

    default_message = "Realtime error."


class WebSocketConnectionError(RealtimeError):
    """
    Websocket connection issue.
    """

    default_message = "WebSocket connection failed."


class SubscriptionError(RealtimeError):
    """
    Realtime subscription failure.
    """

    default_message = "Subscription failed."


# =========================================================
# Storage
# =========================================================


class StorageError(SDKError):
    """
    Storage failure.
    """

    default_message = "Storage operation failed."


class UploadError(StorageError):
    """
    Upload failure.
    """

    default_message = "Upload failed."


class DownloadError(StorageError):
    """
    Download failure.
    """

    default_message = "Download failed."


class PresignedUrlError(StorageError):
    """
    Presigned URL failure.
    """

    default_message = "Presigned URL error."


# =========================================================
# Cache
# =========================================================


class CacheError(SDKError):
    """
    Cache failure.
    """

    default_message = "Cache error."


# =========================================================
# Security
# =========================================================


class SecurityError(SDKError):
    """
    Security failure.
    """

    default_message = "Security error."


class SignatureError(SecurityError):
    """
    Signing failure.
    """

    default_message = "Signature validation failed."


class EncryptionError(SecurityError):
    """
    Encryption failure.
    """

    default_message = "Encryption error."


# =========================================================
# Utilities
# =========================================================


def map_status_to_exception(
    status_code: int,
) -> type[SDKError]:
    """
    Map HTTP status to exception class.
    """
    mapping: dict[int, type[SDKError]] = {
        400: BadRequestError,
        401: AuthenticationError,
        403: AuthorizationError,
        404: ResourceNotFoundError,
        409: ConflictError,
        429: RateLimitError,
    }

    if status_code >= 500:
        return ServerError

    return mapping.get(status_code, WayAPIError)


def raise_for_status(
    status_code: int,
    *,
    message: str | None = None,
    context: ErrorContext | None = None,
) -> None:
    """
    Raise mapped exception.
    """
    exception_cls = map_status_to_exception(status_code)

    raise exception_cls(
        message=message,
        context=context,
    )