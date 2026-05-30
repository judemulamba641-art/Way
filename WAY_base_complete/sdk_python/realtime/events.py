"""
WAY SDK realtime events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class RealtimeEvent:
    """
    Base realtime event.
    """

    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    channel: Optional[str] = None
    event_id: Optional[str] = None
    timestamp: datetime = field(default_factory=utcnow)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RealtimeEvent":
        event_type = payload.get("type", "unknown")

        event_cls = EVENT_REGISTRY.get(
            event_type,
            RealtimeEvent,
        )

        return event_cls(
            type=event_type,
            data=payload.get("data", {}),
            channel=payload.get("channel"),
            event_id=payload.get("event_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "channel": self.channel,
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }


@dataclass(slots=True)
class MessageEvent(RealtimeEvent):
    pass


@dataclass(slots=True)
class SessionEvent(RealtimeEvent):
    pass


@dataclass(slots=True)
class PresenceEvent(RealtimeEvent):
    pass


@dataclass(slots=True)
class ConnectionEvent(RealtimeEvent):
    pass


@dataclass(slots=True)
class ErrorEvent(RealtimeEvent):
    pass


EVENT_REGISTRY: Dict[str, Type[RealtimeEvent]] = {
    "message.created": MessageEvent,
    "message.updated": MessageEvent,
    "message.deleted": MessageEvent,

    "session.created": SessionEvent,
    "session.updated": SessionEvent,
    "session.closed": SessionEvent,

    "presence.updated": PresenceEvent,

    "connection.opened": ConnectionEvent,
    "connection.closed": ConnectionEvent,
    "connection.reconnected": ConnectionEvent,

    "error": ErrorEvent,
}