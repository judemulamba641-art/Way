from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from sdk_python.exceptions import (
    SDKTimeoutError,
    SDKTransportError,
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


class WebSocketState(str, Enum):
    """
    Etat websocket.
    """

    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CLOSING = "closing"
    CLOSED = "closed"


class WebSocketEvent(str, Enum):
    """
    Type d’événement.
    """

    CONNECT = "connect"
    MESSAGE = "message"
    ERROR = "error"
    CLOSE = "close"
    PING = "ping"
    PONG = "pong"


@dataclass(slots=True)
class WebSocketMessage:
    """
    Message websocket standardisé.
    """

    event: WebSocketEvent
    payload: Any = None
    headers: Mapping[str, str] = field(default_factory=dict)


class WebSocketTransport:
    """
    Transport websocket sync.
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
        self._retry = retry_policy or RetryPolicy(
            RetryConfig(),
        )
        self._timeout = timeout_manager or TimeoutManager()

        self._state = WebSocketState.IDLE

    @property
    def state(self) -> WebSocketState:
        return self._state

    def connect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """
        Ouvre connexion websocket.
        """
        attempt = 0
        self._state = WebSocketState.CONNECTING

        while True:
            try:
                self._timeout.run(
                    self._client.connect,
                    url,
                    headers=headers or {},
                )

                self._state = WebSocketState.CONNECTED
                return

            except Exception as exc:
                decision = self._retry.evaluate(
                    attempt=attempt,
                    error=exc,
                    request=None,
                )

                if not decision.should_retry:
                    self._state = WebSocketState.CLOSED
                    raise SDKTransportError(
                        "WebSocket connection failed"
                    ) from exc

                attempt += 1

    def send(
        self,
        payload: Any,
    ) -> None:
        """
        Envoi message.
        """
        self._ensure_connected()

        serialized = self._serializer.dumps(payload)

        self._timeout.run(
            self._client.send,
            serialized,
        )

    def receive(self) -> WebSocketMessage:
        """
        Réception sync.
        """
        self._ensure_connected()

        raw = self._timeout.run(
            self._client.recv,
        )

        payload = self._deserializer.loads(raw)

        return WebSocketMessage(
            event=WebSocketEvent.MESSAGE,
            payload=payload,
        )

    def ping(self) -> None:
        """
        Ping serveur.
        """
        self._ensure_connected()

        ping = getattr(self._client, "ping", None)

        if callable(ping):
            self._timeout.run(ping)

    def close(self) -> None:
        """
        Fermeture connexion.
        """
        if self._state is WebSocketState.CLOSED:
            return

        self._state = WebSocketState.CLOSING

        close = getattr(self._client, "close", None)

        if callable(close):
            self._timeout.run(close)

        self._state = WebSocketState.CLOSED

    def _ensure_connected(self) -> None:
        if self._state is not WebSocketState.CONNECTED:
            raise SDKTransportError(
                "WebSocket is not connected"
            )


class AsyncWebSocketTransport:
    """
    Transport websocket async.
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
        self._retry = retry_policy or RetryPolicy(
            RetryConfig(),
        )
        self._timeout = timeout_manager or TimeoutManager()

        self._state = WebSocketState.IDLE

    @property
    def state(self) -> WebSocketState:
        return self._state

    async def connect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """
        Connexion async.
        """
        attempt = 0
        self._state = WebSocketState.CONNECTING

        while True:
            try:
                await self._timeout.run_async(
                    self._client.connect(
                        url,
                        headers=headers or {},
                    )
                )

                self._state = WebSocketState.CONNECTED
                return

            except Exception as exc:
                decision = self._retry.evaluate(
                    attempt=attempt,
                    error=exc,
                    request=None,
                )

                if not decision.should_retry:
                    self._state = WebSocketState.CLOSED
                    raise SDKTransportError(
                        "WebSocket connection failed"
                    ) from exc

                if decision.delay > 0:
                    await asyncio.sleep(
                        decision.delay
                    )

                attempt += 1

    async def send(
        self,
        payload: Any,
    ) -> None:
        """
        Envoi async.
        """
        self._ensure_connected()

        serialized = self._serializer.dumps(
            payload
        )

        await self._timeout.run_async(
            self._client.send(
                serialized
            )
        )

    async def receive(
        self,
    ) -> WebSocketMessage:
        """
        Réception async.
        """
        self._ensure_connected()

        raw = await self._timeout.run_async(
            self._client.recv()
        )

        payload = self._deserializer.loads(
            raw
        )

        return WebSocketMessage(
            event=WebSocketEvent.MESSAGE,
            payload=payload,
        )

    async def ping(self) -> None:
        """
        Ping async.
        """
        self._ensure_connected()

        ping = getattr(
            self._client,
            "ping",
            None,
        )

        if callable(ping):
            await self._timeout.run_async(
                ping()
            )

    async def close(self) -> None:
        """
        Fermeture.
        """
        if self._state is WebSocketState.CLOSED:
            return

        self._state = WebSocketState.CLOSING

        close = getattr(
            self._client,
            "close",
            None,
        )

        if callable(close):
            await self._timeout.run_async(
                close()
            )

        self._state = WebSocketState.CLOSED

    def _ensure_connected(
        self,
    ) -> None:
        if self._state is not WebSocketState.CONNECTED:
            raise SDKTransportError(
                "WebSocket is not connected"
            )