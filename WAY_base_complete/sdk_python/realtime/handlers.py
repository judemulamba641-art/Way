"""
WAY SDK realtime handlers.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import (
    Any,
    Awaitable,
    Callable,
    DefaultDict,
    List,
)

from .events import (
    MessageEvent,
    PresenceEvent,
    RealtimeEvent,
    SessionEvent,
)

EventCallback = Callable[[RealtimeEvent], Any]
AsyncEventCallback = Callable[[RealtimeEvent], Awaitable[Any]]


class EventHandler:
    """
    Dynamic realtime event dispatcher.
    """

    def __init__(self) -> None:
        self._handlers: DefaultDict[
            str,
            List[EventCallback],
        ] = defaultdict(list)

    def on(
        self,
        event_type: str,
        callback: EventCallback,
    ) -> None:
        if callback not in self._handlers[event_type]:
            self._handlers[event_type].append(callback)

    def off(
        self,
        event_type: str,
        callback: EventCallback,
    ) -> None:
        if callback in self._handlers[event_type]:
            self._handlers[event_type].remove(callback)

    async def dispatch(
        self,
        event: RealtimeEvent,
    ) -> None:
        callbacks = list(
            self._handlers.get(event.type, [])
        )

        wildcard = list(
            self._handlers.get("*", [])
        )

        callbacks.extend(wildcard)

        for callback in callbacks:
            result = callback(event)

            if asyncio.iscoroutine(result):
                await result

    def clear(self) -> None:
        self._handlers.clear()


class MessageHandler(EventHandler):
    async def dispatch(
        self,
        event: RealtimeEvent,
    ) -> None:
        if isinstance(event, MessageEvent):
            await super().dispatch(event)


class SessionHandler(EventHandler):
    async def dispatch(
        self,
        event: RealtimeEvent,
    ) -> None:
        if isinstance(event, SessionEvent):
            await super().dispatch(event)


class PresenceHandler(EventHandler):
    async def dispatch(
        self,
        event: RealtimeEvent,
    ) -> None:
        if isinstance(event, PresenceEvent):
            await super().dispatch(event)