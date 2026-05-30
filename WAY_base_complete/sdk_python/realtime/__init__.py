"""
WAY SDK realtime package.

Realtime messaging, subscriptions, event handling,
and websocket-based consumers.
"""

from .client import RealtimeClient
from .consumer import RealtimeConsumer
from .events import (
    RealtimeEvent,
    MessageEvent,
    SessionEvent,
    ConnectionEvent,
    PresenceEvent,
    ErrorEvent,
)
from .handler import (
    EventHandler,
    MessageHandler,
    SessionHandler,
    PresenceHandler,
)
from .subscriptions import (
    Subscription,
    SubscriptionManager,
)

__all__ = [
    # client
    "RealtimeClient",

    # consumer
    "RealtimeConsumer",

    # events
    "RealtimeEvent",
    "MessageEvent",
    "SessionEvent",
    "ConnectionEvent",
    "PresenceEvent",
    "ErrorEvent",

    # handlers
    "EventHandler",
    "MessageHandler",
    "SessionHandler",
    "PresenceHandler",

    # subscriptions
    "Subscription",
    "SubscriptionManager",
]