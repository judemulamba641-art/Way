from __future__ import annotations

from typing import Any, Mapping, Optional

from sdk_python.resources.base import BaseResource


class AuthResource(BaseResource):
    """
    Authentication resource.

    Handles:
    - login
    - logout
    - refresh
    - token inspection
    - session validation
    """

    resource_name = "auth"

    #
    # sync
    #

    def login(
        self,
        *,
        identifier: str,
        password: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        payload = {
            "identifier": identifier,
            "password": password,
            "metadata": metadata or {},
        }

        response = self._request(
            "POST",
            self.endpoint("login"),
            json=payload,
        )

        auth = self.auth

        if auth and hasattr(auth, "update_from_response"):
            auth.update_from_response(response)

        return response

    def logout(self) -> Any:
        response = self._request(
            "POST",
            self.endpoint("logout"),
        )

        auth = self.auth

        if auth and hasattr(auth, "clear"):
            auth.clear()

        return response

    def refresh(self) -> Any:
        response = self._request(
            "POST",
            self.endpoint("refresh"),
        )

        auth = self.auth

        if auth and hasattr(auth, "update_from_response"):
            auth.update_from_response(response)

        return response

    def validate(self) -> Any:
        return self._request(
            "GET",
            self.endpoint("validate"),
        )

    def me(self) -> Any:
        return self._request(
            "GET",
            self.endpoint("me"),
        )

    #
    # async
    #

    async def alogin(
        self,
        *,
        identifier: str,
        password: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        payload = {
            "identifier": identifier,
            "password": password,
            "metadata": metadata or {},
        }

        response = await self._arequest(
            "POST",
            self.endpoint("login"),
            json=payload,
        )

        auth = self.auth

        if auth and hasattr(auth, "update_from_response"):
            result = auth.update_from_response(response)

            if hasattr(result, "__await__"):
                await result

        return response

    async def alogout(self) -> Any:
        response = await self._arequest(
            "POST",
            self.endpoint("logout"),
        )

        auth = self.auth

        if auth and hasattr(auth, "clear"):
            result = auth.clear()

            if hasattr(result, "__await__"):
                await result

        return response

    async def arefresh(self) -> Any:
        response = await self._arequest(
            "POST",
            self.endpoint("refresh"),
        )

        auth = self.auth

        if auth and hasattr(auth, "update_from_response"):
            result = auth.update_from_response(response)

            if hasattr(result, "__await__"):
                await result

        return response

    async def avalidate(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("validate"),
        )

    async def ame(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("me"),
        )