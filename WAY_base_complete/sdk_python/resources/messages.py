from __future__ import annotations

from typing import Any, Mapping, Optional

from sdk_python.resources.base import BaseResource


class MessagesResource(BaseResource):
    """
    Messaging resource.

    Handles:
    - send
    - retrieve
    - list
    - update
    - delete
    - acknowledge
    """

    resource_name = "messages"

    #
    # sync
    #

    def send(
        self,
        *,
        content: str,
        recipient: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(),
            json={
                "content": content,
                "recipient": recipient,
                "metadata": dict(metadata or {}),
            },
        )

    def get(
        self,
        message_id: str,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(message_id),
        )

    def list(
        self,
        *,
        recipient: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(),
            params={
                "recipient": recipient,
                "limit": limit,
                "cursor": cursor,
            },
        )

    def update(
        self,
        message_id: str,
        *,
        content: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return self._request(
            "PATCH",
            self.endpoint(message_id),
            json={
                "content": content,
                "metadata": dict(metadata or {}),
            },
        )

    def acknowledge(
        self,
        message_id: str,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(message_id, "ack"),
        )

    def delete(
        self,
        message_id: str,
    ) -> Any:
        return self._request(
            "DELETE",
            self.endpoint(message_id),
        )

    #
    # async
    #

    async def asend(
        self,
        *,
        content: str,
        recipient: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(),
            json={
                "content": content,
                "recipient": recipient,
                "metadata": dict(metadata or {}),
            },
        )

    async def aget(
        self,
        message_id: str,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(message_id),
        )

    async def alist(
        self,
        *,
        recipient: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(),
            params={
                "recipient": recipient,
                "limit": limit,
                "cursor": cursor,
            },
        )

    async def aupdate(
        self,
        message_id: str,
        *,
        content: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return await self._arequest(
            "PATCH",
            self.endpoint(message_id),
            json={
                "content": content,
                "metadata": dict(metadata or {}),
            },
        )

    async def aacknowledge(
        self,
        message_id: str,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(message_id, "ack"),
        )

    async def adelete(
        self,
        message_id: str,
    ) -> Any:
        return await self._arequest(
            "DELETE",
            self.endpoint(message_id),
        )