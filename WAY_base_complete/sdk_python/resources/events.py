from __future__ import annotations

from typing import Any, Mapping, Optional

from sdk_python.resources.base import BaseResource


class EventsResource(BaseResource):
    """
    Event resource.

    Handles:
    - publish
    - retrieve
    - list
    - acknowledge
    - replay
    """

    resource_name = "events"

    #
    # sync
    #

    def publish(
        self,
        *,
        name: str,
        payload: Mapping[str, Any],
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        body = {
            "name": name,
            "payload": dict(payload),
            "metadata": dict(metadata or {}),
        }

        return self._request(
            "POST",
            self.endpoint(),
            json=body,
        )

    def get(
        self,
        event_id: str,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(event_id),
        )

    def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Any:
        params = {
            "limit": limit,
            "cursor": cursor,
            "name": name,
            "status": status,
        }

        return self._request(
            "GET",
            self.endpoint(),
            params=params,
        )

    def acknowledge(
        self,
        event_id: str,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(event_id, "ack"),
        )

    def replay(
        self,
        event_id: str,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(event_id, "replay"),
        )

    #
    # async
    #

    async def apublish(
        self,
        *,
        name: str,
        payload: Mapping[str, Any],
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        body = {
            "name": name,
            "payload": dict(payload),
            "metadata": dict(metadata or {}),
        }

        return await self._arequest(
            "POST",
            self.endpoint(),
            json=body,
        )

    async def aget(
        self,
        event_id: str,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(event_id),
        )

    async def alist(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Any:
        params = {
            "limit": limit,
            "cursor": cursor,
            "name": name,
            "status": status,
        }

        return await self._arequest(
            "GET",
            self.endpoint(),
            params=params,
        )

    async def aacknowledge(
        self,
        event_id: str,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(event_id, "ack"),
        )

    async def areplay(
        self,
        event_id: str,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(event_id, "replay"),
        )