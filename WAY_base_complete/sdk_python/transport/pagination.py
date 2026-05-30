from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import (
    Generic,
    Iterable,
    Iterator,
    Sequence,
    TypeVar,
)

from sdk_python.models.pagination import (
    CursorPagination,
    CursorPaginationMetadata,
    PagePagination,
    PagePaginationMetadata,
)


__all__ = [
    "PagePaginationState",
    "CursorPaginationState",
    "PaginationResult",
]


T = TypeVar("T")


@dataclass(slots=True, frozen=True)
class PagePaginationState:
    """
    Stateful page pagination helper.
    """

    page: int = 1
    page_size: int = 20
    total_items: int | None = None

    @property
    def offset(self) -> int:
        return max(self.page - 1, 0) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def total_pages(self) -> int | None:
        if self.total_items is None:
            return None

        if self.total_items == 0:
            return 0

        return ceil(
            self.total_items / self.page_size,
        )

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        total_pages = self.total_pages

        if total_pages is None:
            return False

        return self.page < total_pages

    def next(self) -> "PagePaginationState":
        return PagePaginationState(
            page=self.page + 1,
            page_size=self.page_size,
            total_items=self.total_items,
        )

    def previous(self) -> "PagePaginationState":
        return PagePaginationState(
            page=max(1, self.page - 1),
            page_size=self.page_size,
            total_items=self.total_items,
        )

    def with_total(
        self,
        total_items: int,
    ) -> "PagePaginationState":
        return PagePaginationState(
            page=self.page,
            page_size=self.page_size,
            total_items=total_items,
        )

    def as_query(self) -> dict[str, str]:
        return {
            "page": str(self.page),
            "page_size": str(self.page_size),
        }

    def to_model(self) -> PagePagination:
        return PagePagination(
            metadata=PagePaginationMetadata(
                page=self.page,
                page_size=self.page_size,
                total_items=self.total_items or 0,
                total_pages=self.total_pages or 0,
            ),
        )


@dataclass(slots=True, frozen=True)
class CursorPaginationState:
    """
    Stateful cursor pagination helper.
    """

    cursor: str | None = None
    page_size: int = 20
    next_cursor: str | None = None
    previous_cursor: str | None = None
    has_more: bool = False

    def advance(
        self,
        *,
        next_cursor: str | None,
        has_more: bool,
    ) -> "CursorPaginationState":
        return CursorPaginationState(
            cursor=next_cursor,
            page_size=self.page_size,
            next_cursor=next_cursor,
            previous_cursor=self.cursor,
            has_more=has_more,
        )

    def back(self) -> "CursorPaginationState":
        return CursorPaginationState(
            cursor=self.previous_cursor,
            page_size=self.page_size,
            next_cursor=None,
            previous_cursor=None,
            has_more=self.has_more,
        )

    def as_query(self) -> dict[str, str]:
        payload = {
            "page_size": str(self.page_size),
        }

        if self.cursor:
            payload["cursor"] = self.cursor

        return payload

    def to_model(self) -> CursorPagination:
        return CursorPagination(
            metadata=CursorPaginationMetadata(
                cursor=self.cursor,
                next_cursor=self.next_cursor,
                previous_cursor=self.previous_cursor,
                has_more=self.has_more,
                page_size=self.page_size,
            ),
        )


@dataclass(slots=True, frozen=True)
class PaginationResult(Generic[T]):
    """
    Generic paginated transport result.
    """

    items: Sequence[T] = field(default_factory=tuple)

    page: PagePaginationState | None = None
    cursor: CursorPaginationState | None = None

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def empty(self) -> bool:
        return len(self.items) == 0

    @property
    def has_next(self) -> bool:
        if self.page:
            return self.page.has_next

        if self.cursor:
            return self.cursor.has_more

        return False

    @property
    def has_previous(self) -> bool:
        if self.page:
            return self.page.has_previous

        if self.cursor:
            return self.cursor.previous_cursor is not None

        return False

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def first(self) -> T | None:
        if not self.items:
            return None

        return self.items[0]

    def last(self) -> T | None:
        if not self.items:
            return None

        return self.items[-1]

    def map(
        self,
        fn,
    ) -> "PaginationResult":
        return PaginationResult(
            items=tuple(
                fn(item)
                for item in self.items
            ),
            page=self.page,
            cursor=self.cursor,
        )

    @classmethod
    def from_iterable(
        cls,
        items: Iterable[T],
        *,
        page: PagePaginationState | None = None,
        cursor: CursorPaginationState | None = None,
    ) -> "PaginationResult[T]":
        return cls(
            items=tuple(items),
            page=page,
            cursor=cursor,
        )