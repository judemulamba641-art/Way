from __future__ import annotations

from typing import Final, Dict, Set


"""
WAY SDK Constants Module.

This module centralizes all immutable values used across the SDK.

Design goals:
- Avoid magic strings/numbers across codebase
- Ensure consistency across client, transport, auth, and resources
- Provide a single source of truth for protocol-level values
- Be fully stable for long-term backward compatibility
"""


# =========================================================
# SDK IDENTIFICATION
# =========================================================

SDK_NAME: Final[str] = "way-python-sdk"
SDK_PLATFORM: Final[str] = "WAY"

# =========================================================
# PROTOCOL DEFAULTS
# =========================================================

DEFAULT_BASE_URL: Final[str] = "https://api.way.local"

DEFAULT_TIMEOUT: Final[int] = 30
DEFAULT_RETRIES: Final[int] = 3

DEFAULT_MAX_CONNECTIONS: Final[int] = 100
DEFAULT_BACKOFF_FACTOR: Final[float] = 0.5

DEFAULT_CONTENT_TYPE: Final[str] = "application/json"

# =========================================================
# HTTP METHODS
# =========================================================

HTTP_METHODS: Final[Set[str]] = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
}

# =========================================================
# HEADER KEYS
# =========================================================

HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
HEADER_AUTHORIZATION: Final[str] = "Authorization"
HEADER_USER_AGENT: Final[str] = "User-Agent"
HEADER_ACCEPT: Final[str] = "Accept"

# =========================================================
# AUTH SCHEMES
# =========================================================

AUTH_SCHEME_BEARER: Final[str] = "Bearer"
AUTH_SCHEME_API_KEY: Final[str] = "ApiKey"
AUTH_SCHEME_JWT: Final[str] = "JWT"

# =========================================================
# ENVIRONMENT TYPES
# =========================================================

ENV_PRODUCTION: Final[str] = "production"
ENV_STAGING: Final[str] = "staging"
ENV_DEVELOPMENT: Final[str] = "development"
ENV_TEST: Final[str] = "test"

ENVIRONMENTS: Final[Set[str]] = {
    ENV_PRODUCTION,
    ENV_STAGING,
    ENV_DEVELOPMENT,
    ENV_TEST,
}

# =========================================================
# TRANSPORT / RETRY CODES
# =========================================================

RETRYABLE_STATUS_CODES: Final[Set[int]] = {
    408,  # Request Timeout
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}

NON_RETRYABLE_STATUS_CODES: Final[Set[int]] = {
    400,  # Bad Request
    401,  # Unauthorized
    403,  # Forbidden
    404,  # Not Found
}

# =========================================================
# WEBSOCKET EVENTS (future realtime layer)
# =========================================================

WS_EVENT_CONNECT: Final[str] = "connect"
WS_EVENT_DISCONNECT: Final[str] = "disconnect"
WS_EVENT_MESSAGE: Final[str] = "message"
WS_EVENT_ERROR: Final[str] = "error"
WS_EVENT_HEARTBEAT: Final[str] = "heartbeat"

# =========================================================
# PAGINATION DEFAULTS
# =========================================================

DEFAULT_PAGE_SIZE: Final[int] = 50
MAX_PAGE_SIZE: Final[int] = 200

# =========================================================
# SDK ERROR CODES (internal mapping layer)
# =========================================================

ERROR_CODE_AUTH_FAILED: Final[str] = "auth_failed"
ERROR_CODE_TIMEOUT: Final[str] = "timeout"
ERROR_CODE_VALIDATION: Final[str] = "validation_error"
ERROR_CODE_TRANSPORT: Final[str] = "transport_error"
ERROR_CODE_UNKNOWN: Final[str] = "unknown_error"

# =========================================================
# FEATURE FLAGS KEYS (standardized)
# =========================================================

FEATURE_REALTIME: Final[str] = "realtime"
FEATURE_STREAMING: Final[str] = "streaming"
FEATURE_BATCHING: Final[str] = "batching"
FEATURE_EXPERIMENTAL: Final[str] = "experimental"

# =========================================================
# SDK VERSION COMPATIBILITY
# =========================================================

MIN_SUPPORTED_VERSION: Final[str] = "1.0.0"

# =========================================================
# EXPORT SAFE LIST
# =========================================================

__all__ = [
    "SDK_NAME",
    "SDK_PLATFORM",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRIES",
    "DEFAULT_MAX_CONNECTIONS",
    "DEFAULT_BACKOFF_FACTOR",
    "DEFAULT_CONTENT_TYPE",
    "HTTP_METHODS",
    "HEADER_CONTENT_TYPE",
    "HEADER_AUTHORIZATION",
    "HEADER_USER_AGENT",
    "HEADER_ACCEPT",
    "AUTH_SCHEME_BEARER",
    "AUTH_SCHEME_API_KEY",
    "AUTH_SCHEME_JWT",
    "ENV_PRODUCTION",
    "ENV_STAGING",
    "ENV_DEVELOPMENT",
    "ENV_TEST",
    "ENVIRONMENTS",
    "RETRYABLE_STATUS_CODES",
    "NON_RETRYABLE_STATUS_CODES",
    "WS_EVENT_CONNECT",
    "WS_EVENT_DISCONNECT",
    "WS_EVENT_MESSAGE",
    "WS_EVENT_ERROR",
    "WS_EVENT_HEARTBEAT",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "ERROR_CODE_AUTH_FAILED",
    "ERROR_CODE_TIMEOUT",
    "ERROR_CODE_VALIDATION",
    "ERROR_CODE_TRANSPORT",
    "ERROR_CODE_UNKNOWN",
    "FEATURE_REALTIME",
    "FEATURE_STREAMING",
    "FEATURE_BATCHING",
    "FEATURE_EXPERIMENTAL",
    "MIN_SUPPORTED_VERSION",
]