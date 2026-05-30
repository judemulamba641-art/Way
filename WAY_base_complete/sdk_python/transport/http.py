from __future__ import annotations

import asyncio
from typing import Any, Mapping

from sdk_python.exceptions import (
    SDKTimeoutError,
    SDKTransportError,
)
from sdk_python.transport.base import (
    AsyncBaseTransport,
    BaseTransport,
    BaseTransportRequest,
    BaseTransportResponse,
    HTTPMethod,
    TransportMetadata,
)
from sdk_python.transport.retry import (
    RetryConfig,
    RetryPolicy,
)
from sdk_python.transport.serializer import (
    TransportDeserializer,
    TransportSerializer,
)
from sdk_python.transport.timeout import TimeoutManager


class HTTPTransport(BaseTransport):
    """
    Transport HTTP synchrone.
    """

    def __init__(
        self,
        *,
        client: Any,
        serializer: TransportSerializer,
        deserializer: TransportDeserializer,
        retry_policy: RetryPolicy | None = None,
        timeout_manager: TimeoutManager | None = None,
    ) -> None:
        self._client = client
        self._serializer = serializer
        self._deserializer = deserializer
        self._retry_policy = retry_policy or RetryPolicy(
            RetryConfig(),
        )
        self._timeout = timeout_manager or TimeoutManager()

    def send(
        self,
        request: BaseTransportRequest,
    ) -> BaseTransportResponse:
        """
        Envoie requête sync.
        """
        attempt = 0

        while True:
            try:
                return self._dispatch(request)

            except Exception as exc:
                decision = self._retry_policy.evaluate(
                    attempt=attempt,
                    error=exc,
                    request=request,
                )

                if not decision.should_retry:
                    raise

                attempt += 1

    def close(self) -> None:
        close = getattr(self._client, "close", None)

        if callable(close):
            close()

    def _dispatch(
        self,
        request: BaseTransportRequest,
    ) -> BaseTransportResponse:
        """
        Exécution réelle HTTP.
        """
        body = self._serialize_body(request.body)

        response = self._timeout.run(
            self._client.request,
            method=self._method_value(request.method),
            url=str(request.url),
            headers=dict(request.headers or {}),
            json=body,
            timeout=self._timeout.default_timeout,
        )

        return self._build_response(response)

    def _serialize_body(
        self,
        body: Any,
    ) -> Any:
        if body is None:
            return None

        return self._serializer.dumps(body)

    def _deserialize_body(
        self,
        body: Any,
    ) -> Any:
        if body in (None, "", b""):
            return None

        return self._deserializer.loads(body)

    def _build_response(
        self,
        raw: Any,
    ) -> BaseTransportResponse:
        metadata = TransportMetadata(
            status_code=getattr(raw, "status_code", 0),
            headers=dict(getattr(raw, "headers", {})),
        )

        body = self._deserialize_body(
            getattr(raw, "text", None),
        )

        return BaseTransportResponse(
            body=body,
            metadata=metadata,
        )

    @staticmethod
    def _method_value(
        method: HTTPMethod | str,
    ) -> str:
        if isinstance(method, HTTPMethod):
            return method.value

        return str(method).upper()


class AsyncHTTPTransport(AsyncBaseTransport):
    """
    Transport HTTP async.
    """

    def __init__(
        self,
        *,
        client: Any,
        serializer: TransportSerializer,
        deserializer: TransportDeserializer,
        retry_policy: RetryPolicy | None = None,
        timeout_manager: TimeoutManager | None = None,
    ) -> None:
        self._client = client
        self._serializer = serializer
        self._deserializer = deserializer
        self._retry_policy = retry_policy or RetryPolicy(
            RetryConfig(),
        )
        self._timeout = timeout_manager or TimeoutManager()

    async def send(
        self,
        request: BaseTransportRequest,
    ) -> BaseTransportResponse:
        """
        Envoi async.
        """
        attempt = 0

        while True:
            try:
                return await self._dispatch(request)

            except Exception as exc:
                decision = self._retry_policy.evaluate(
                    attempt=attempt,
                    error=exc,
                    request=request,
                )

                if not decision.should_retry:
                    raise

                delay = decision.delay

                if delay > 0:
                    await asyncio.sleep(delay)

                attempt += 1

    async def close(self) -> None:
        close = getattr(self._client, "aclose", None)

        if callable(close):
            await close()

    async def _dispatch(
        self,
        request: BaseTransportRequest,
    ) -> BaseTransportResponse:
        body = self._serialize_body(request.body)

        response = await self._timeout.run_async(
            self._client.request(
                method=self._method_value(request.method),
                url=str(request.url),
                headers=dict(request.headers or {}),
                json=body,
                timeout=self._timeout.default_timeout,
            )
        )

        return self._build_response(response)

    def _serialize_body(
        self,
        body: Any,
    ) -> Any:
        if body is None:
            return None

        return self._serializer.dumps(body)

    def _deserialize_body(
        self,
        body: Any,
    ) -> Any:
        if body in (None, "", b""):
            return None

        return self._deserializer.loads(body)

    def _build_response(
        self,
        raw: Any,
    ) -> BaseTransportResponse:
        metadata = TransportMetadata(
            status_code=getattr(raw, "status_code", 0),
            headers=dict(getattr(raw, "headers", {})),
        )

        body = self._deserialize_body(
            getattr(raw, "text", None),
        )

        return BaseTransportResponse(
            body=body,
            metadata=metadata,
        )

    @staticmethod
    def _method_value(
        method: HTTPMethod | str,
    ) -> str:
        if isinstance(method, HTTPMethod):
            return method.value

        return str(method).upper()