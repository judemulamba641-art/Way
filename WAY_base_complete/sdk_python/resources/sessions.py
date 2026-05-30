from __future__ import annotations

from typing import Any, Mapping, Optional

from sdk_python.resources.base import BaseResource


class SessionsResource(BaseResource):
    """
    Session resource.

    Handles:
    - create
    - retrieve
    - list
    - revoke
    - refresh
    - current
    """

    resource_name = "sessions"

    #
    # sync
    #

    def create(
        self,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(),
            json={
                "metadata": dict(metadata or {}),
            },
        )

    def current(self) -> Any:
        return self._request(
            "GET",
            self.endpoint("current"),
        )

    def get(
        self,
        session_id: str,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(session_id),
        )

    def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(),
            params={
                "limit": limit,
                "cursor": cursor,
                "status": status,
            },
        )

    def refresh(
        self,
        session_id: str,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(session_id, "refresh"),
        )

    def revoke(
        self,
        session_id: str,
    ) -> Any:
        return self._request(
            "DELETE",
            self.endpoint(session_id),
        )

    def revoke_all(self) -> Any:
        return self._request(
            "POST",
            self.endpoint("revoke-all"),
        )

    #
    # async
    #

    async def acreate(
        self,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(),
            json={
                "metadata": dict(metadata or {}),
            },
        )

    async def acurrent(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("current"),
        )

    async def aget(
        self,
        session_id: str,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(session_id),
        )

    async def alist(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(),
            params={
                "limit": limit,
                "cursor": cursor,
                "status": status,
            },
        )

    async def arefresh(
        self,
        session_id: str,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(session_id, "refresh"),
        )

    async def arevoke(
        self,
        session_id: str,
    ) -> Any:
        return await self._arequest(
            "DELETE",
            self.endpoint(session_id),
        )

    async def arevoke_all(self) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint("revoke-all"),
        )