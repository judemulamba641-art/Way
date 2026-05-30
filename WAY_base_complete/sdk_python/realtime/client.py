"""
WAY SDK realtime client.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from .consumer import RealtimeConsumer
from .events import RealtimeEvent
from .handler import EventHandler
from .subscriptions import SubscriptionManager

ConnectCallable = Callable[
    [],
    Awaitable[None],
]

DisconnectCallable = Callable[
    [],
    Awaitable[None],
]

ReceiveCallable = Callable[
    [],
    Awaitable[dict[str, Any]],
]

SendCallable = Callable[
    [dict[str, Any]],
    Awaitable[None],
]


class RealtimeClient:
    """
    High-level realtime client.
    """

    def __init__(
        self,
        *,
        connect: ConnectCallable,
        disconnect: DisconnectCallable,
        receiver: ReceiveCallable,
        sender: Optional[
            SendCallable
        ] = None,
    ) -> None:
        self._connect = connect
        self._disconnect = disconnect
        self._receiver = receiver
        self._sender = sender

        self._connected = False

        self.handler = EventHandler()

        self.subscriptions = (
            SubscriptionManager()
        )

        self.consumer = RealtimeConsumer(
            receiver=self._receiver,
            handler=self.handler,
            subscriptions=self.subscriptions,
        )

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        if self._connected:
            return

        await self._connect()

        self._connected = True

        await self.consumer.start()

    async def disconnect(self) -> None:
        if not self._connected:
            return

        await self.consumer.stop()

        await self._disconnect()

        self._connected = False

    async def subscribe(
        self,
        channel: str,
        **filters: str,
    ) -> None:
        await self.subscriptions.subscribe(
            channel,
            **filters,
        )

        if self._sender:
            await self._sender(
                {
                    "action": "subscribe",
                    "channel": channel,
                    "filters": filters,
                }
            )

    async def unsubscribe(
        self,
        channel: str,
    ) -> None:
        await self.subscriptions.unsubscribe(
            channel
        )

        if self._sender:
            await self._sender(
                {
                    "action": "unsubscribe",
                    "channel": channel,
                }
            )

    def on(
        self,
        event_type: str,
        callback: Callable[..., Any],
    ) -> None:
        self.handler.on(
            event_type,
            callback,
        )

    def off(
        self,
        event_type: str,
        callback: Callable[..., Any],
    ) -> None:
        self.handler.off(
            event_type,
            callback,
        )

    async def send(
        self,
        event: RealtimeEvent,
    ) -> None:
        if not self._sender:
            raise RuntimeError(
                "Realtime sender not configured."
            )

        await self._sender(
            event.to_dict()
        )

    async def emit(
        self,
        event_type: str,
        data: Optional[
            dict[str, Any]
        ] = None,
        *,
        channel: Optional[
            str
        ] = None,
    ) -> None:
        event = RealtimeEvent(
            type=event_type,
            data=data or {},
            channel=channel,
        )

        await self.send(event)

    async def consume_once(
        self,
    ) -> None:
        await self.consumer.consume_once()