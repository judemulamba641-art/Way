from __future__ import annotations

import json
import logging
from typing import Any

from django.conf import settings
from redis.asyncio import Redis
from redis.asyncio import from_url

logger = logging.getLogger(__name__)


class MessageBroker:
    """
    Central async message broker.

    Used by:
        - Celery
        - Channels
        - internal pub/sub
        - event broadcasting
        - background workers
    """

    _client: Redis | None = None

    def __init__(
        self,
        url: str | None = None,
        prefix: str = "way",
    ) -> None:
        self.url = url or settings.REDIS_URL
        self.prefix = prefix

    async def connect(self) -> Redis:
        """
        Lazy broker connection.
        """
        if self.__class__._client is None:
            logger.info(
                "Initializing message broker",
                extra={
                    "redis_url": self.url,
                },
            )

            self.__class__._client = from_url(
                self.url,
                encoding="utf-8",
                decode_responses=False,
                health_check_interval=30,
                socket_keepalive=True,
            )

        return self.__class__._client

    async def close(self) -> None:
        """
        Graceful shutdown.
        """
        if self.__class__._client is not None:
            logger.info(
                "Closing message broker",
            )

            await self.__class__._client.close()

            self.__class__._client = None

    def channel_name(
        self,
        name: str,
    ) -> str:
        """
        Namespaced broker channel.
        """
        return f"{self.prefix}:{name}"

    def serialize(
        self,
        payload: Any,
    ) -> str:
        """
        JSON encode.
        """
        return json.dumps(
            payload,
            default=str,
            ensure_ascii=False,
        )

    def deserialize(
        self,
        payload: bytes | str | None,
    ) -> Any:
        """
        JSON decode.
        """
        if payload is None:
            return None

        if isinstance(payload, bytes):
            payload = payload.decode()

        try:
            return json.loads(payload)

        except json.JSONDecodeError:
            return payload

    async def ping(self) -> bool:
        """
        Broker health.
        """
        try:
            client = await self.connect()

            return bool(
                await client.ping(),
            )

        except Exception:
            logger.exception(
                "Broker ping failed",
            )
            return False

    async def publish(
        self,
        channel: str,
        payload: Any,
    ) -> int:
        """
        Publish event.
        """
        redis_channel = self.channel_name(channel)

        try:
            client = await self.connect()

            subscribers = await client.publish(
                redis_channel,
                self.serialize(payload),
            )

            return int(subscribers)

        except Exception:
            logger.exception(
                "Broker publish failed",
                extra={
                    "channel": redis_channel,
                },
            )
            return 0

    async def subscribe(
        self,
        channel: str,
    ):
        """
        Subscribe to channel.
        """
        redis_channel = self.channel_name(channel)

        client = await self.connect()

        pubsub = client.pubsub()

        await pubsub.subscribe(
            redis_channel,
        )

        return pubsub

    async def unsubscribe(
        self,
        pubsub,
        channel: str,
    ) -> None:
        """
        Unsubscribe safely.
        """
        redis_channel = self.channel_name(channel)

        try:
            await pubsub.unsubscribe(
                redis_channel,
            )

        except Exception:
            logger.exception(
                "Broker unsubscribe failed",
                extra={
                    "channel": redis_channel,
                },
            )

    async def broadcast(
        self,
        event: str,
        payload: Any,
    ) -> int:
        """
        Broadcast global event.
        """
        return await self.publish(
            event,
            payload,
        )