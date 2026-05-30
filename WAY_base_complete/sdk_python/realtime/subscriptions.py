"""
WAY SDK realtime subscriptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from .events import RealtimeEvent


@dataclass(slots=True)
class Subscription:
    """
    Represents a realtime subscription.
    """

    channel: str
    filters: Dict[str, str] = field(default_factory=dict)

    def matches(
        self,
        event: RealtimeEvent,
    ) -> bool:
        if self.channel != "*" and event.channel != self.channel:
            return False

        for key, value in self.filters.items():
            current = event.data.get(key)

            if current != value:
                return False

        return True


class SubscriptionManager:
    """
    Dynamic realtime subscription registry.
    """

    def __init__(self) -> None:
        self._subscriptions: Dict[
            str,
            Subscription,
        ] = {}

    async def subscribe(
        self,
        channel: str,
        **filters: str,
    ) -> Subscription:
        subscription = Subscription(
            channel=channel,
            filters=filters,
        )

        self._subscriptions[channel] = subscription

        return subscription

    async def unsubscribe(
        self,
        channel: str,
    ) -> None:
        self._subscriptions.pop(
            channel,
            None,
        )

    def get(
        self,
        channel: str,
    ) -> Optional[Subscription]:
        return self._subscriptions.get(channel)

    def channels(self) -> Set[str]:
        return set(
            self._subscriptions.keys()
        )

    def is_subscribed(
        self,
        channel: str,
    ) -> bool:
        return channel in self._subscriptions

    def matches(
        self,
        event: RealtimeEvent,
    ) -> bool:
        if not self._subscriptions:
            return True

        for subscription in self._subscriptions.values():
            if subscription.matches(event):
                return True

        return False

    def clear(self) -> None:
        self._subscriptions.clear()