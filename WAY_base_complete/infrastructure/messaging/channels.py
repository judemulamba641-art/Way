from __future__ import annotations

import logging
from typing import Any

from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class ChannelManager:
    """
    Central Django Channels manager.

    Used by:
        - websocket consumers
        - realtime notifications
        - internal events
        - group broadcasting
        - async services
    """

    _layer = None

    @classmethod
    def layer(cls):
        """
        Return singleton channel layer.
        """
        if cls._layer is None:
            logger.info(
                "Initializing channel layer",
            )

            cls._layer = get_channel_layer()

        return cls._layer

    @classmethod
    async def send(
        cls,
        channel: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Send to one channel.
        """
        try:
            layer = cls.layer()

            if layer is None:
                return

            await layer.send(
                channel,
                payload,
            )

        except Exception:
            logger.exception(
                "Channel send failed",
                extra={
                    "channel": channel,
                },
            )

    @classmethod
    async def group_send(
        cls,
        group: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Broadcast to group.
        """
        try:
            layer = cls.layer()

            if layer is None:
                return

            await layer.group_send(
                group,
                payload,
            )

        except Exception:
            logger.exception(
                "Channel group_send failed",
                extra={
                    "group": group,
                },
            )

    @classmethod
    async def group_add(
        cls,
        group: str,
        channel: str,
    ) -> None:
        """
        Add channel to group.
        """
        try:
            layer = cls.layer()

            if layer is None:
                return

            await layer.group_add(
                group,
                channel,
            )

        except Exception:
            logger.exception(
                "Channel group_add failed",
                extra={
                    "group": group,
                    "channel": channel,
                },
            )

    @classmethod
    async def group_discard(
        cls,
        group: str,
        channel: str,
    ) -> None:
        """
        Remove channel from group.
        """
        try:
            layer = cls.layer()

            if layer is None:
                return

            await layer.group_discard(
                group,
                channel,
            )

        except Exception:
            logger.exception(
                "Channel group_discard failed",
                extra={
                    "group": group,
                    "channel": channel,
                },
            )

    @classmethod
    async def notify_user(
        cls,
        user_id: int | str,
        event: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Notify one user group.
        """
        await cls.group_send(
            group=f"user:{user_id}",
            payload={
                "type": event,
                **payload,
            },
        )

    @classmethod
    async def broadcast(
        cls,
        event: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Global broadcast.
        """
        await cls.group_send(
            group="global",
            payload={
                "type": event,
                **payload,
            },
        )

    @classmethod
    def ping(cls) -> bool:
        """
        Check layer availability.
        """
        try:
            return cls.layer() is not None

        except Exception:
            logger.exception(
                "Channel layer ping failed",
            )
            return False