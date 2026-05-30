"""
WAY SDK Python - Event Models
=============================

Typed event system shared across:

- API lifecycle
- WebSocket transport
- async workers
- internal pub/sub
- tracing
- audit logs
- retries
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional

from .base import BaseModel
from .base import utc_now


# =========================================================
# Event types
# =========================================================
class EventType(str, Enum):
    """
    Canonical SDK event names.
    """

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    REQUEST = "request"
    RESPONSE = "response"

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

    MESSAGE_SENT = "message.sent"
    MESSAGE_RECEIVED = "message.received"

    SESSION_STARTED = "session.started"
    SESSION_ENDED = "session.ended"

    UPLOAD_STARTED = "upload.started"
    UPLOAD_COMPLETED = "upload.completed"
    UPLOAD_FAILED = "upload.failed"

    TOKEN_CREATED = "token.created"
    TOKEN_REFRESHED = "token.refreshed"

    ERROR = "error"

    CUSTOM = "custom"


# =========================================================
# Event payload
# =========================================================
@dataclass(slots=True)
class EventPayload(BaseModel):
    """
    Generic structured payload.
    """

    data: Dict[str, Any] = field(default_factory=dict)

    source: Optional[str] = None
    target: Optional[str] = None

    trace_id: Optional[str] = None
    request_id: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not isinstance(self.data, dict):
            raise TypeError("data must be dict")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be dict")

    def add(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add payload field.
        """
        self.data[key] = value
        self.touch()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read payload field.
        """
        return self.data.get(key, default)

    def set_meta(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add metadata.
        """
        self.metadata[key] = value
        self.touch()


# =========================================================
# Main event
# =========================================================
@dataclass(slots=True)
class Event(BaseModel):
    """
    Core event model.

    Example:
        Event(
            type=EventType.MESSAGE_SENT,
            name="chat.message",
        )
    """

    type: EventType = EventType.CUSTOM

    name: str = ""

    payload: EventPayload = field(
        default_factory=EventPayload
    )

    timestamp = field(
        default_factory=utc_now
    )

    version: str = "1.0"

    correlation_id: Optional[str] = None
    parent_id: Optional[str] = None

    actor_id: Optional[str] = None
    session_id: Optional[str] = None

    retryable: bool = False

    successful: bool = True

    tags: list[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------
    def validate(self) -> None:
        if not self.name:
            raise ValueError(
                "Event name is required"
            )

        if not isinstance(self.payload, EventPayload):
            raise TypeError(
                "payload must be EventPayload"
            )

        if not isinstance(self.metadata, dict):
            raise TypeError(
                "metadata must be dict"
            )

    # -----------------------------------------------------
    # Tag helpers
    # -----------------------------------------------------
    def add_tag(
        self,
        tag: str,
    ) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def has_tag(
        self,
        tag: str,
    ) -> bool:
        return tag in self.tags

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------
    def set_meta(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata[key] = value
        self.touch()

    def get_meta(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.metadata.get(
            key,
            default,
        )

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------
    def mark_failed(
        self,
        reason: Optional[str] = None,
    ) -> None:
        """
        Mark event failed.
        """
        self.successful = False

        if reason:
            self.set_meta(
                "failure_reason",
                reason,
            )

        self.touch()

    def mark_success(self) -> None:
        """
        Mark successful.
        """
        self.successful = True
        self.touch()

    # -----------------------------------------------------
    # Payload helpers
    # -----------------------------------------------------
    def emit(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add payload field.
        """
        self.payload.add(
            key,
            value,
        )
        self.touch()

    def read(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read payload value.
        """
        return self.payload.get(
            key,
            default,
        )

    # -----------------------------------------------------
    # Tracing
    # -----------------------------------------------------
    def bind_trace(
        self,
        trace_id: str,
    ) -> None:
        self.payload.trace_id = trace_id
        self.touch()

    def bind_request(
        self,
        request_id: str,
    ) -> None:
        self.payload.request_id = request_id
        self.touch()

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------
    def to_transport(self) -> Dict[str, Any]:
        """
        Transport-safe payload.

        Used for:
        - websocket
        - queues
        - external API
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "correlation_id": self.correlation_id,
            "parent_id": self.parent_id,
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "retryable": self.retryable,
            "successful": self.successful,
            "tags": self.tags,
            "metadata": self.metadata,
            "payload": self.payload.to_dict(),
        }