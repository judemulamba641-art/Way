"""
WAY SDK Python - Response Models
================================

Unified response models used across:

- REST API
- SDK transport
- WebSocket
- async workers
- events
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import Optional

from .base import BaseModel
from .message import Message
from .event import Event


# =========================================================
# Response metadata
# =========================================================
@dataclass(slots=True)
class ResponseMetadata(BaseModel):
    """
    Extra response metadata.
    """

    request_id: Optional[str] = None
    trace_id: Optional[str] = None

    duration_ms: Optional[float] = None

    headers: Dict[str, Any] = field(
        default_factory=dict
    )

    extras: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        if not isinstance(
            self.headers,
            dict,
        ):
            raise TypeError(
                "headers must be dict"
            )

        if not isinstance(
            self.extras,
            dict,
        ):
            raise TypeError(
                "extras must be dict"
            )

    def set_header(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.headers[key] = value
        self.touch()

    def set_extra(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.extras[key] = value
        self.touch()


# =========================================================
# Main response
# =========================================================
@dataclass(slots=True)
class ApiResponse(BaseModel):
    """
    Universal response container.
    """

    ok: bool = True

    status_code: int = 200

    message: Optional[Message] = None

    event: Optional[Event] = None

    data: Any = None

    error: Optional[str] = None

    metadata: ResponseMetadata = field(
        default_factory=ResponseMetadata
    )

    version: str = "1.0"

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------
    def validate(self) -> None:
        if not isinstance(
            self.metadata,
            ResponseMetadata,
        ):
            raise TypeError(
                "metadata must be ResponseMetadata"
            )

        if self.ok is False and not self.error:
            raise ValueError(
                "error required when ok=False"
            )

    # -----------------------------------------------------
    # State helpers
    # -----------------------------------------------------
    def set_data(
        self,
        value: Any,
    ) -> None:
        self.data = value
        self.touch()

    def set_message(
        self,
        value: Message,
    ) -> None:
        self.message = value
        self.touch()

    def set_event(
        self,
        value: Event,
    ) -> None:
        self.event = value
        self.touch()

    def fail(
        self,
        error: str,
        *,
        status_code: int = 400,
    ) -> None:
        self.ok = False
        self.error = error
        self.status_code = status_code
        self.touch()

    def success(
        self,
        value: Any = None,
    ) -> None:
        self.ok = True
        self.error = None
        self.data = value
        self.touch()

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------
    def to_transport(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "ok": self.ok,
            "status_code": self.status_code,
            "version": self.version,
            "error": self.error,
            "data": self.data,
            "message": (
                self.message.to_transport()
                if self.message
                else None
            ),
            "event": (
                self.event.to_transport()
                if self.event
                else None
            ),
            "metadata": (
                self.metadata.to_dict()
            ),
        }


# =========================================================
# Success response
# =========================================================
@dataclass(slots=True)
class SuccessResponse(ApiResponse):
    """
    Success response.
    """

    ok: bool = True
    status_code: int = 200

    def validate(self) -> None:
        super().validate()

        if self.ok is False:
            raise ValueError(
                "SuccessResponse cannot be false"
            )


# =========================================================
# Error response
# =========================================================
@dataclass(slots=True)
class ErrorResponse(ApiResponse):
    """
    Error response.
    """

    ok: bool = False
    status_code: int = 400

    def validate(self) -> None:
        super().validate()

        if not self.error:
            raise ValueError(
                "error message required"
            )