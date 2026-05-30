from __future__ import annotations

import logging
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from way.config import configure_logging
from way.logging import set_log_context


# ---------------------------------------------------------
# Bootstrap logging
# ---------------------------------------------------------
configure_logging()
set_log_context(service="channels")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Channel layer
# ---------------------------------------------------------
channel_layer = get_channel_layer()


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _group_name(channel: str) -> str:
    return channel.replace(":", "_")


def publish_event(channel: str, event: str, data: dict[str, Any] | None = None) -> None:
    payload = {
        "type": "broadcast.message",
        "event": event,
        "data": data or {},
    }

    group = _group_name(channel)

    logger.info(
        "Publishing websocket event",
        extra={"channel": group, "event": event},
    )

    async_to_sync(channel_layer.group_send)(group, payload)


def publish_user_event(user_id: str | int, event: str, data: dict[str, Any] | None = None) -> None:
    publish_event(f"user:{user_id}", event, data)


def publish_system_event(event: str, data: dict[str, Any] | None = None) -> None:
    publish_event("system", event, data)


def publish_room_event(room_id: str, event: str, data: dict[str, Any] | None = None) -> None:
    publish_event(f"room:{room_id}", event, data)