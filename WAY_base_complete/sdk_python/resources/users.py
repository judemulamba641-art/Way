from __future__ import annotations

from typing import Any, Mapping, Optional

from sdk_python.resources.base import BaseResource


class UsersResource(BaseResource):
    """
    User resource.

    Handles:
    - create
    - retrieve
    - list
    - update
    - delete
    - current profile
    - activate / deactivate
    """

    resource_name = "users"

    #
    # sync
    #

    def create(
        self,
        *,
        username: str,
        email: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(),
            json={
                "username": username,
                "email": email,
                "metadata": dict(metadata or {}),
            },
        )

    def me(self) -> Any:
        return self._request(
            "GET",
            self.endpoint("me"),
        )

    def get(
        self,
        user_id: str,
    ) -> Any:
        cache_key = f"user:{user_id}"

        cached = self._cache_get(cache_key)

        if cached is not None:
            return cached

        result = self._request(
            "GET",
            self.endpoint(user_id),
        )

        self._cache_set(
            cache_key,
            result,
            ttl=300,
        )

        return result

    def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        search: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Any:
        return self._request(
            "GET",
            self.endpoint(),
            params={
                "limit": limit,
                "cursor": cursor,
                "search": search,
                "active": active,
            },
        )

    def update(
        self,
        user_id: str,
        *,
        username: Optional[str] = None,
        email: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        result = self._request(
            "PATCH",
            self.endpoint(user_id),
            json={
                "username": username,
                "email": email,
                "metadata": dict(metadata or {}),
            },
        )

        self._cache_set(
            f"user:{user_id}",
            result,
            ttl=300,
        )

        return result

    def activate(
        self,
        user_id: str,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(user_id, "activate"),
        )

    def deactivate(
        self,
        user_id: str,
    ) -> Any:
        return self._request(
            "POST",
            self.endpoint(user_id, "deactivate"),
        )

    def delete(
        self,
        user_id: str,
    ) -> Any:
        return self._request(
            "DELETE",
            self.endpoint(user_id),
        )

    #
    # async
    #

    async def acreate(
        self,
        *,
        username: str,
        email: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(),
            json={
                "username": username,
                "email": email,
                "metadata": dict(metadata or {}),
            },
        )

    async def ame(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("me"),
        )

    async def aget(
        self,
        user_id: str,
    ) -> Any:
        cache_key = f"user:{user_id}"

        cached = await self._acache_get(cache_key)

        if cached is not None:
            return cached

        result = await self._arequest(
            "GET",
            self.endpoint(user_id),
        )

        await self._acache_set(
            cache_key,
            result,
            ttl=300,
        )

        return result

    async def alist(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        search: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(),
            params={
                "limit": limit,
                "cursor": cursor,
                "search": search,
                "active": active,
            },
        )

    async def aupdate(
        self,
        user_id: str,
        *,
        username: Optional[str] = None,
        email: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        result = await self._arequest(
            "PATCH",
            self.endpoint(user_id),
            json={
                "username": username,
                "email": email,
                "metadata": dict(metadata or {}),
            },
        )

        await self._acache_set(
            f"user:{user_id}",
            result,
            ttl=300,
        )

        return result

    async def aactivate(
        self,
        user_id: str,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(user_id, "activate"),
        )

    async def adeactivate(
        self,
        user_id: str,
    ) -> Any:
        return await self._arequest(
            "POST",
            self.endpoint(user_id, "deactivate"),
        )

    async def adelete(
        self,
        user_id: str,
    ) -> Any:
        return await self._arequest(
            "DELETE",
            self.endpoint(user_id),
        )