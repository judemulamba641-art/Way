from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import (
    Any,
    Generic,
    Mapping,
    MutableMapping,
    Protocol,
    TypeVar,
)
from urllib.parse import urlencode, urljoin
from uuid import uuid4

from sdk_python.auth.base import AuthStrategy
from sdk_python.settings import SDKSettings


__all__ = [
    "HTTPMethod",
    "TransportProtocol",
    "PayloadEncoding",
    "TransportMetadata",
    "TransportContext",
    "BaseTransportRequest",
    "BaseTransportResponse",
    "TransportExecutor",
    "AsyncTransportExecutor",
    "BaseTransport",
    "AsyncBaseTransport",
]


T = TypeVar("T")


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class TransportProtocol(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    WS = "ws"
    WSS = "wss"


class PayloadEncoding(str, Enum):
    JSON = "json"
    FORM = "form"
    MULTIPART = "multipart"
    BYTES = "bytes"
    TEXT = "text"
    NONE = "none"


@dataclass(slots=True, frozen=True)
class TransportMetadata:
    request_id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str | None = None
    trace_id: str | None = None
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: Mapping[str, str] = field(default_factory=dict)

    def with_tags(
        self,
        **extra: str,
    ) -> "TransportMetadata":
        merged = dict(self.tags)
        merged.update(extra)

        return TransportMetadata(
            request_id=self.request_id,
            tenant_id=self.tenant_id,
            trace_id=self.trace_id,
            correlation_id=self.correlation_id,
            created_at=self.created_at,
            tags=merged,
        )


@dataclass(slots=True, frozen=True)
class TransportContext:
    settings: SDKSettings
    auth: AuthStrategy | None = None
    metadata: TransportMetadata = field(default_factory=TransportMetadata)

    @property
    def base_url(self) -> str:
        return str(self.settings.base_url).rstrip("/")

    def resolve_url(
        self,
        path: str,
    ) -> str:
        return urljoin(
            f"{self.base_url}/",
            path.lstrip("/"),
        )


@dataclass(slots=True)
class BaseTransportRequest(Generic[T]):
    method: HTTPMethod
    path: str

    query: MutableMapping[str, str] = field(default_factory=dict)
    headers: MutableMapping[str, str] = field(default_factory=dict)

    body: T | None = None
    encoding: PayloadEncoding = PayloadEncoding.JSON

    metadata: TransportMetadata = field(
        default_factory=TransportMetadata,
    )

    @property
    def request_id(self) -> str:
        return self.metadata.request_id

    @property
    def url_path(self) -> str:
        return self.path

    def add_header(
        self,
        key: str,
        value: str,
    ) -> None:
        self.headers[key] = value

    def add_query(
        self,
        key: str,
        value: str,
    ) -> None:
        self.query[key] = value

    def resolved_url(
        self,
        context: TransportContext,
    ) -> str:
        url = context.resolve_url(self.path)

        if not self.query:
            return url

        return f"{url}?{urlencode(self.query)}"

    def apply_defaults(self) -> None:
        self.headers.setdefault(
            "Accept",
            "application/json",
        )

        match self.encoding:
            case PayloadEncoding.JSON:
                self.headers.setdefault(
                    "Content-Type",
                    "application/json",
                )

            case PayloadEncoding.FORM:
                self.headers.setdefault(
                    "Content-Type",
                    "application/x-www-form-urlencoded",
                )

            case PayloadEncoding.MULTIPART:
                pass

            case PayloadEncoding.BYTES:
                self.headers.setdefault(
                    "Content-Type",
                    "application/octet-stream",
                )

            case PayloadEncoding.TEXT:
                self.headers.setdefault(
                    "Content-Type",
                    "text/plain",
                )

            case PayloadEncoding.NONE:
                return

    def apply_auth(
        self,
        auth: AuthStrategy | None,
    ) -> None:
        if auth is None:
            return

        auth_headers = auth.get_headers()

        if auth_headers:
            self.headers.update(auth_headers)

    def finalize(
        self,
        context: TransportContext,
    ) -> "BaseTransportRequest[T]":
        self.apply_defaults()
        self.apply_auth(context.auth)

        self.headers.setdefault(
            "X-Request-ID",
            self.metadata.request_id,
        )

        if self.metadata.trace_id:
            self.headers.setdefault(
                "X-Trace-ID",
                self.metadata.trace_id,
            )

        if self.metadata.correlation_id:
            self.headers.setdefault(
                "X-Correlation-ID",
                self.metadata.correlation_id,
            )

        if self.metadata.tenant_id:
            self.headers.setdefault(
                "X-Tenant-ID",
                self.metadata.tenant_id,
            )

        return self


@dataclass(slots=True, frozen=True)
class BaseTransportResponse(Generic[T]):
    status_code: int
    headers: Mapping[str, str]
    body: T | None
    metadata: TransportMetadata

    received_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return self.status_code >= 500

    def header(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        return self.headers.get(key, default)


class TransportExecutor(Protocol):
    def send(
        self,
        request: BaseTransportRequest[Any],
        *,
        context: TransportContext,
    ) -> BaseTransportResponse[Any]:
        ...


class AsyncTransportExecutor(Protocol):
    async def send(
        self,
        request: BaseTransportRequest[Any],
        *,
        context: TransportContext,
    ) -> BaseTransportResponse[Any]:
        ...


class BaseTransport(ABC):
    protocol: TransportProtocol = TransportProtocol.HTTPS

    def __init__(
        self,
        *,
        settings: SDKSettings,
        auth: AuthStrategy | None = None,
        metadata: TransportMetadata | None = None,
    ) -> None:
        self._context = TransportContext(
            settings=settings,
            auth=auth,
            metadata=metadata or TransportMetadata(),
        )

    @property
    def context(self) -> TransportContext:
        return self._context

    @property
    def settings(self) -> SDKSettings:
        return self._context.settings

    @property
    def auth(self) -> AuthStrategy | None:
        return self._context.auth

    def build_request(
        self,
        request: BaseTransportRequest[T],
    ) -> BaseTransportRequest[T]:
        return request.finalize(self._context)

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class AsyncBaseTransport(ABC):
    protocol: TransportProtocol = TransportProtocol.HTTPS

    def __init__(
        self,
        *,
        settings: SDKSettings,
        auth: AuthStrategy | None = None,
        metadata: TransportMetadata | None = None,
    ) -> None:
        self._context = TransportContext(
            settings=settings,
            auth=auth,
            metadata=metadata or TransportMetadata(),
        )

    @property
    def context(self) -> TransportContext:
        return self._context

    @property
    def settings(self) -> SDKSettings:
        return self._context.settings

    @property
    def auth(self) -> AuthStrategy | None:
        return self._context.auth

    def build_request(
        self,
        request: BaseTransportRequest[T],
    ) -> BaseTransportRequest[T]:
        return request.finalize(self._context)

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError