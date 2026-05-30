from __future__ import annotations

from typing import Any

from sdk_python.resources.base import BaseResource


class HealthResource(BaseResource):
    """
    Health / diagnostics resource.

    Handles:
    - global health check
    - readiness
    - liveness
    - status
    - version
    """

    resource_name = "health"

    #
    # sync
    #

    def check(self) -> Any:
        """
        Global health check.
        """
        return self._request(
            "GET",
            self.endpoint(),
        )

    def ready(self) -> Any:
        """
        Service readiness.
        """
        return self._request(
            "GET",
            self.endpoint("ready"),
        )

    def live(self) -> Any:
        """
        Service liveness.
        """
        return self._request(
            "GET",
            self.endpoint("live"),
        )

    def status(self) -> Any:
        """
        Runtime status.
        """
        return self._request(
            "GET",
            self.endpoint("status"),
        )

    def version(self) -> Any:
        """
        Service / API version.
        """
        return self._request(
            "GET",
            self.endpoint("version"),
        )

    def ping(self) -> bool:
        """
        Fast boolean health probe.
        """

        try:
            self.check()
            return True
        except Exception:
            return False

    #
    # async
    #

    async def acheck(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint(),
        )

    async def aready(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("ready"),
        )

    async def alive(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("live"),
        )

    async def astatus(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("status"),
        )

    async def aversion(self) -> Any:
        return await self._arequest(
            "GET",
            self.endpoint("version"),
        )

    async def aping(self) -> bool:
        try:
            await self.acheck()
            return True
        except Exception:
            return False