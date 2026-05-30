"""
WAY SDK Python - Message Models
===============================

Core messaging models shared across:

- REST API
- WebSocket transport
- sessions
- events
- async pipelines
- realtime streams
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
# Message roles
# =========================================================
class MessageRole(str, Enum):
    """
    Canonical sender roles.
    """

    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    SERVER = "server"
    CLIENT = "client"
    BOT = "bot"
    CUSTOM = "custom"


# =========================================================
# Message types
# =========================================================
class MessageType(str, Enum):
    """
    Message categories.
    """

    TEXT = "text"
    JSON = "json"
    EVENT = "event"
    COMMAND = "command"
    STREAM = "stream"
    FILE = "file"
    ERROR = "error"
    STATUS = "status"
    CUSTOM = "custom"


# =========================================================
# Message metadata
# =========================================================
@dataclass(slots=True)
class MessageMetadata(BaseModel):
    """
    Flexible message metadata.
    """

    headers: Dict[str, Any] = field(default_factory=dict)

    trace_id: Optional[str] = None
    request_id: Optional[str] = None

    priority: int = 0

    extras: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not isinstance(self.headers, dict):
            raise TypeError("headers must be dict")

        if not isinstance(self.extras, dict):
            raise TypeError("extras must be dict")

    def set_header(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.headers[key] = value
        self.touch()

    def get_header(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.headers.get(
            key,
            default,
        )

    def set_extra(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.extras[key] = value
        self.touch()

    def get_extra(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.extras.get(
            key,
            default,
        )


# =========================================================
# Main message
# =========================================================
@dataclass(slots=True)
class Message(BaseModel):
    """
    Core transport message.
    """

    role: MessageRole = MessageRole.USER

    type: MessageType = MessageType.TEXT

    content: Any = None

    name: Optional[str] = None

    session_id: Optional[str] = None
    user_id: Optional[str] = None

    created = field(
        default_factory=utc_now
    )

    metadata: MessageMetadata = field(
        default_factory=MessageMetadata
    )

    tags: list[str] = field(default_factory=list)

    delivered: bool = False
    streamed: bool = False

    sequence: Optional[int] = None

    reply_to: Optional[str] = None

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------
    def validate(self) -> None:
        if not isinstance(
            self.role,
            MessageRole,
        ):
            raise TypeError(
                "role must be MessageRole"
            )

        if not isinstance(
            self.type,
            MessageType,
        ):
            raise TypeError(
                "type must be MessageType"
            )

        if not isinstance(
            self.metadata,
            MessageMetadata,
        ):
            raise TypeError(
                "metadata must be MessageMetadata"
            )

    # -----------------------------------------------------
    # Tags
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
    def set_header(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata.set_header(
            key,
            value,
        )
        self.touch()

    def set_extra(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata.set_extra(
            key,
            value,
        )
        self.touch()

    # -----------------------------------------------------
    # Delivery
    # -----------------------------------------------------
    def mark_delivered(self) -> None:
        self.delivered = True
        self.touch()

    def mark_streamed(self) -> None:
        self.streamed = True
        self.touch()

    # -----------------------------------------------------
    # Content
    # -----------------------------------------------------
    def append(
        self,
        value: str,
    ) -> None:
        """
        Append to text stream.
        """
        if self.content is None:
            self.content = value

        elif isinstance(
            self.content,
            str,
        ):
            self.content += value

        else:
            raise TypeError(
                "append only supported on text content"
            )

        self.touch()

    def clear(self) -> None:
        """
        Clear content.
        """
        self.content = None
        self.touch()

    # -----------------------------------------------------
    # Reply chaining
    # -----------------------------------------------------
    def reply(
        self,
        content: Any,
        *,
        role: MessageRole = MessageRole.ASSISTANT,
        type: MessageType = MessageType.TEXT,
    ) -> "Message":
        """
        Create reply message.
        """
        return Message(
            role=role,
            type=type,
            content=content,
            session_id=self.session_id,
            user_id=self.user_id,
            reply_to=self.id,
        )

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------
    def to_transport(self) -> Dict[str, Any]:
        """
        Transport payload.
        """
        return {
            "id": self.id,
            "role": self.role.value,
            "type": self.type.value,
            "content": self.content,
            "name": self.name,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created": self.created.isoformat(),
            "tags": self.tags,
            "delivered": self.delivered,
            "streamed": self.streamed,
            "sequence": self.sequence,
            "reply_to": self.reply_to,
            "metadata": self.metadata.to_dict(),
        }