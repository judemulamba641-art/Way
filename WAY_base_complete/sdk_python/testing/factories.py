"""
WAY SDK testing factories.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict


def _utcnow() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _id() -> str:
    return uuid.uuid4().hex


class BaseFactory:
    """
    Base test factory.
    """

    @classmethod
    def build(
        cls,
        **overrides: Any,
    ) -> Dict[str, Any]:
        payload = cls.defaults()

        payload.update(
            overrides
        )

        return payload

    @classmethod
    def defaults(
        cls,
    ) -> Dict[str, Any]:
        return {}


class UserFactory(BaseFactory):
    """
    Build user payloads.
    """

    @classmethod
    def defaults(
        cls,
    ) -> Dict[str, Any]:
        user_id = _id()

        return {
            "id": user_id,
            "username": f"user_{user_id[:8]}",
            "email": (
                f"{user_id[:8]}"
                "@way.local"
            ),
            "active": True,
            "created_at": _utcnow(),
        }


class SessionFactory(BaseFactory):
    """
    Build session payloads.
    """

    @classmethod
    def defaults(
        cls,
    ) -> Dict[str, Any]:
        return {
            "id": _id(),
            "user_id": _id(),
            "status": "active",
            "created_at": _utcnow(),
        }


class MessageFactory(BaseFactory):
    """
    Build message payloads.
    """

    @classmethod
    def defaults(
        cls,
    ) -> Dict[str, Any]:
        return {
            "id": _id(),
            "session_id": _id(),
            "content": "Hello WAY",
            "role": "user",
            "created_at": _utcnow(),
        }


class EventFactory(BaseFactory):
    """
    Build realtime event payloads.
    """

    @classmethod
    def defaults(
        cls,
    ) -> Dict[str, Any]:
        return {
            "type": "message.created",
            "channel": "messages",
            "event_id": _id(),
            "data": (
                MessageFactory.build()
            ),
        }