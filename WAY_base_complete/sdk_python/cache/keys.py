from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
import hashlib


#
# =========================================================
# Namespaces
# =========================================================
#


class CacheNamespace(StrEnum):
    """
    Default cache namespaces for WAY SDK.

    Extend freely depending on domain needs.
    """

    DEFAULT = "default"

    AUTH = "auth"
    SESSION = "session"
    TOKEN = "token"
    USER = "user"

    STORAGE = "storage"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    PRESIGNED = "presigned"
    MULTIPART = "multipart"

    HTTP = "http"
    TRANSPORT = "transport"

    CONFIG = "config"
    SETTINGS = "settings"

    METRICS = "metrics"
    TELEMETRY = "telemetry"


#
# =========================================================
# Helpers
# =========================================================
#


def _normalize(value: Any) -> str:
    """
    Normalize cache key components.

    Stable conversion for:
    - str
    - int
    - UUID
    - enums
    """

    if value is None:
        return "null"

    if isinstance(value, str):
        return value.strip()

    return str(value)


def _hash(value: str) -> str:
    """
    Deterministic SHA256 helper.

    Useful when key length must stay compact.
    """

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


#
# =========================================================
# CacheKey
# =========================================================
#


@dataclass(slots=True, frozen=True)
class CacheKey:
    """
    Immutable cache key.

    Examples:
        CacheKey(CacheNamespace.AUTH, "token", user_id)
        CacheKey(CacheNamespace.STORAGE, "file", file_id)
    """

    namespace: str
    parts: tuple[str, ...]

    def __init__(
        self,
        namespace: str | CacheNamespace,
        *parts: Any,
    ) -> None:
        normalized_namespace = _normalize(namespace)

        normalized_parts = tuple(
            _normalize(part)
            for part in parts
        )

        object.__setattr__(
            self,
            "namespace",
            normalized_namespace,
        )

        object.__setattr__(
            self,
            "parts",
            normalized_parts,
        )

    #
    # -----------------------------------------------------
    # render
    # -----------------------------------------------------
    #

    def full(self) -> str:
        """
        Full string representation.
        """

        if not self.parts:
            return self.namespace

        return ":".join(
            (
                self.namespace,
                *self.parts,
            )
        )

    def compact(self) -> str:
        """
        Compact hashed representation.
        """

        return _hash(self.full())

    #
    # -----------------------------------------------------
    # mutation helpers
    # -----------------------------------------------------
    #

    def child(self, *parts: Any) -> CacheKey:
        """
        Create child key.

        Example:
            parent.child("metadata")
        """

        return CacheKey(
            self.namespace,
            *self.parts,
            *parts,
        )

    def with_namespace(
        self,
        namespace: str | CacheNamespace,
    ) -> CacheKey:
        """
        Clone with another namespace.
        """

        return CacheKey(
            namespace,
            *self.parts,
        )

    #
    # -----------------------------------------------------
    # comparisons
    # -----------------------------------------------------
    #

    def startswith(
        self,
        namespace: str | CacheNamespace,
    ) -> bool:
        return self.namespace == _normalize(namespace)

    #
    # -----------------------------------------------------
    # dunder
    # -----------------------------------------------------
    #

    def __str__(self) -> str:
        return self.full()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(namespace={self.namespace!r}, parts={self.parts!r})"
        )


#
# =========================================================
# Factory helpers
# =========================================================
#


def auth_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.AUTH, *parts)


def session_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.SESSION, *parts)


def token_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.TOKEN, *parts)


def user_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.USER, *parts)


def storage_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.STORAGE, *parts)


def upload_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.UPLOAD, *parts)


def download_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.DOWNLOAD, *parts)


def presigned_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.PRESIGNED, *parts)


def multipart_key(*parts: Any) -> CacheKey:
    return CacheKey(CacheNamespace.MULTIPART, *parts)