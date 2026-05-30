"""
WAY SDK realtime consumer.
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Optional

from .events import RealtimeEvent
from .handler import EventHandler
from .subscriptions import SubscriptionManager

ReceiveCallable = Callable[
    [],
    Awaitable[dict[str, Any]],
]


class RealtimeConsumer:
    """
    Consumes realtime websocket payloads.
    """

    def __init__(
        self,
        *,
        receiver: ReceiveCallable,
        handler: EventHandler,
        subscriptions: SubscriptionManager,
    ) -> None:
        self._receiver = receiver
        self._handler = handler
        self._subscriptions = subscriptions

        self._running = False
        self._task: Optional[
            asyncio.Task[Any]
        ] = None

    @property
    def running(self) -> bool:
        return self._running

    async def start(self) -> None:
        if self._running:
            return

        self._running = True

        self._task = asyncio.create_task(
            self._consume_loop()
        )

    async def stop(self) -> None:
        self._running = False

        if self._task:
            self._task.cancel()

            try:
                await self._task
            except asyncio.CancelledError:
                pass

            self._task = None

    async def _consume_loop(self) -> None:
        while self._running:
            payload = await self._receiver()

            event = RealtimeEvent.from_dict(
                payload
            )

            if not self._subscriptions.matches(
                event
            ):
                continue

            await self._handler.dispatch(
                event
            )

    async def consume_once(self) -> None:
        payload = await self._receiver()

        event = RealtimeEvent.from_dict(
            payload
        )

        if self._subscriptions.matches(
            event
        ):
            await self._handler.dispatch(
                event
            )