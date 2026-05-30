"""
WAY SDK testing mocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class MockResponse:
    """
    Fake HTTP response.
    """

    status_code: int = 200
    data: Any = None
    headers: Dict[str, str] = field(
        default_factory=dict
    )

    @property
    def ok(self) -> bool:
        return (
            200 <= self.status_code < 300
        )

    def json(self) -> Any:
        return self.data

    def text(self) -> str:
        if self.data is None:
            return ""

        return str(self.data)


class MockTransport:
    """
    Sync transport mock.
    """

    def __init__(self) -> None:
        self._routes: Dict[
            tuple[str, str],
            MockResponse,
        ] = {}

        self.requests: list[
            dict[str, Any]
        ] = []

    def add(
        self,
        method: str,
        path: str,
        *,
        data: Any = None,
        status_code: int = 200,
        headers: Optional[
            Dict[str, str]
        ] = None,
    ) -> None:
        self._routes[
            (
                method.upper(),
                path,
            )
        ] = MockResponse(
            status_code=status_code,
            data=data,
            headers=headers or {},
        )

    def request(
        self,
        *,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        method = method.upper()

        self.requests.append(
            {
                "method": method,
                "path": path,
                "kwargs": kwargs,
            }
        )

        response = self._routes.get(
            (
                method,
                path,
            )
        )

        if response is None:
            return MockResponse(
                status_code=404,
                data={
                    "detail": "not found",
                },
            )

        return response.json()

    def reset(self) -> None:
        self._routes.clear()
        self.requests.clear()


class MockAsyncTransport:
    """
    Async transport mock.
    """

    def __init__(self) -> None:
        self._routes: Dict[
            tuple[str, str],
            MockResponse,
        ] = {}

        self.requests: list[
            dict[str, Any]
        ] = []

    def add(
        self,
        method: str,
        path: str,
        *,
        data: Any = None,
        status_code: int = 200,
        headers: Optional[
            Dict[str, str]
        ] = None,
    ) -> None:
        self._routes[
            (
                method.upper(),
                path,
            )
        ] = MockResponse(
            status_code=status_code,
            data=data,
            headers=headers or {},
        )

    async def request(
        self,
        *,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        method = method.upper()

        self.requests.append(
            {
                "method": method,
                "path": path,
                "kwargs": kwargs,
            }
        )

        response = self._routes.get(
            (
                method,
                path,
            )
        )

        if response is None:
            return MockResponse(
                status_code=404,
                data={
                    "detail": "not found",
                },
            )

        return response.json()

    def reset(self) -> None:
        self._routes.clear()
        self.requests.clear()


class MockCache:
    """
    Simple in-memory cache mock.
    """

    def __init__(self) -> None:
        self._values: Dict[
            str,
            Any,
        ] = {}

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._values.get(
            key,
            default,
        )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._values[key] = value

    def delete(
        self,
        key: str,
    ) -> None:
        self._values.pop(
            key,
            None,
        )

    def exists(
        self,
        key: str,
    ) -> bool:
        return key in self._values

    def clear(self) -> None:
        self._values.clear()