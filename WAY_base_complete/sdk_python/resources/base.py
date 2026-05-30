from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional

from sdk_python.exceptions import SDKError


JsonDict = MutableMapping[str, Any]


class BaseResource:
    """
    Base class for all SDK resources.

    Exposes shared access to:
    - sync / async client
    - transport
    - auth
    - cache
    - storage

    Also centralizes low-level request helpers.
    """

    __slots__ = ("_client",)

    resource_name: str = ""

    def __init__(self, client: Any) -> None:
        self._client = client

    #
    # core references
    #

    @property
    def client(self) -> Any:
        return self._client

    @property
    def transport(self) -> Any:
        return getattr(self._client, "transport", None)

    @property
    def auth(self) -> Any:
        return getattr(self._client, "auth", None)

    @property
    def cache(self) -> Any:
        return getattr(self._client, "cache", None)

    @property
    def storage(self) -> Any:
        return getattr(self._client, "storage", None)

    @property
    def config(self) -> Any:
        return getattr(self._client, "config", None)

    #
    # utilities
    #

    def _join_path(self, *parts: str) -> str:
        """
        Safely join URL fragments.
        """

        values = []

        for part in parts:
            if not part:
                continue

            cleaned = str(part).strip("/")

            if cleaned:
                values.append(cleaned)

        return "/" + "/".join(values)

    def _headers(
        self,
        extra: Optional[Mapping[str, str]] = None,
    ) -> dict[str, str]:
        """
        Merge default headers + auth headers + custom headers.
        """

        headers: dict[str, str] = {}

        default_headers = getattr(
            self._client,
            "default_headers",
            {},
        )

        if default_headers:
            headers.update(default_headers)

        auth = self.auth

        if auth and hasattr(auth, "headers"):
            headers.update(auth.headers())

        if extra:
            headers.update(dict(extra))

        return headers

    def _params(
        self,
        values: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Remove None params.
        """

        if not values:
            return {}

        return {
            key: value
            for key, value in values.items()
            if value is not None
        }

    #
    # sync requests
    #

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        data: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Sync request wrapper.
        """

        transport = self.transport

        if transport is None:
            raise SDKError("Transport is not configured.")

        if not hasattr(transport, "request"):
            raise SDKError("Transport does not support sync requests.")

        return transport.request(
            method=method,
            path=path,
            params=self._params(params),
            json=json,
            data=data,
            headers=self._headers(headers),
            timeout=timeout,
        )

    #
    # async requests
    #

    async def _arequest(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        data: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Async request wrapper.
        """

        transport = self.transport

        if transport is None:
            raise SDKError("Transport is not configured.")

        if not hasattr(transport, "request"):
            raise SDKError("Transport does not support async requests.")

        return await transport.request(
            method=method,
            path=path,
            params=self._params(params),
            json=json,
            data=data,
            headers=self._headers(headers),
            timeout=timeout,
        )

    #
    # cache helpers
    #

    def _cache_get(self, key: str) -> Any:
        cache = self.cache

        if cache and hasattr(cache, "get"):
            return cache.get(key)

        return None

    def _cache_set(
        self,
        key: str,
        value: Any,
        *,
        ttl: Optional[int] = None,
    ) -> None:
        cache = self.cache

        if cache and hasattr(cache, "set"):
            cache.set(
                key,
                value,
                ttl=ttl,
            )

    async def _acache_get(self, key: str) -> Any:
        cache = self.cache

        if cache and hasattr(cache, "get"):
            result = cache.get(key)

            if hasattr(result, "__await__"):
                return await result

            return result

        return None

    async def _acache_set(
        self,
        key: str,
        value: Any,
        *,
        ttl: Optional[int] = None,
    ) -> None:
        cache = self.cache

        if not cache or not hasattr(cache, "set"):
            return

        result = cache.set(
            key,
            value,
            ttl=ttl,
        )

        if hasattr(result, "__await__"):
            await result

    #
    # resource endpoint
    #

    def endpoint(
        self,
        *parts: str,
    ) -> str:
        """
        Build resource endpoint.

        Example:
            users.endpoint("123")
            -> /users/123
        """

        base = self.resource_name

        return self._join_path(
            base,
            *parts,
        )