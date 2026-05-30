"""
WAY SDK Python - Pagination Models
==================================

Pagination utilities for:

- REST API
- SDK collections
- event feeds
- dashboards
- websocket streams
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from .base import BaseModel


T = TypeVar("T")


# =========================================================
# Cursor pagination
# =========================================================
@dataclass(slots=True)
class PaginationCursor(BaseModel):
    """
    Cursor-based pagination state.
    """

    current: Optional[str] = None

    next: Optional[str] = None

    previous: Optional[str] = None

    has_next: bool = False

    has_previous: bool = False

    def validate(self) -> None:
        return

    def advance(
        self,
        value: Optional[str],
    ) -> None:
        self.previous = self.current
        self.current = value
        self.touch()


# =========================================================
# Standard pagination
# =========================================================
@dataclass(slots=True)
class Pagination(BaseModel):
    """
    Offset pagination model.
    """

    page: int = 1

    page_size: int = 20

    total_items: int = 0

    total_pages: int = 0

    cursor: Optional[
        PaginationCursor
    ] = None

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------
    def validate(self) -> None:
        if self.page < 1:
            raise ValueError(
                "page must be >= 1"
            )

        if self.page_size < 1:
            raise ValueError(
                "page_size must be >= 1"
            )

        if self.total_items < 0:
            raise ValueError(
                "total_items invalid"
            )

    # -----------------------------------------------------
    # Properties
    # -----------------------------------------------------
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def offset(self) -> int:
        return (
            self.page - 1
        ) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    # -----------------------------------------------------
    # Navigation
    # -----------------------------------------------------
    def next_page(self) -> None:
        if self.has_next:
            self.page += 1
            self.touch()

    def previous_page(self) -> None:
        if self.has_previous:
            self.page -= 1
            self.touch()

    def update_total(
        self,
        count: int,
    ) -> None:
        """
        Recompute total pages.
        """
        self.total_items = count

        if count == 0:
            self.total_pages = 0

        else:
            self.total_pages = (
                count
                + self.page_size
                - 1
            ) // self.page_size

        self.touch()

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------
    def to_transport(
        self,
    ) -> Dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
            "offset": self.offset,
            "limit": self.limit,
            "cursor": (
                self.cursor.to_dict()
                if self.cursor
                else None
            ),
        }


# =========================================================
# Paginated result
# =========================================================
@dataclass(slots=True)
class PaginatedResult(
    BaseModel,
    Generic[T],
):
    """
    Typed paginated payload.
    """

    items: List[T] = field(
        default_factory=list
    )

    pagination: Pagination = field(
        default_factory=Pagination
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------
    def validate(self) -> None:
        if not isinstance(
            self.items,
            list,
        ):
            raise TypeError(
                "items must be list"
            )

        if not isinstance(
            self.pagination,
            Pagination,
        ):
            raise TypeError(
                "pagination invalid"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata invalid"
            )

    # -----------------------------------------------------
    # Collection helpers
    # -----------------------------------------------------
    def add(
        self,
        item: T,
    ) -> None:
        self.items.append(item)
        self.touch()

    def extend(
        self,
        values: List[T],
    ) -> None:
        self.items.extend(values)
        self.touch()

    def count(self) -> int:
        return len(self.items)

    def empty(self) -> bool:
        return len(self.items) == 0

    def first(self) -> Optional[T]:
        if not self.items:
            return None

        return self.items[0]

    def last(self) -> Optional[T]:
        if not self.items:
            return None

        return self.items[-1]

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------
    def set_meta(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata[key] = value
        self.touch()

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------
    def to_transport(
        self,
    ) -> Dict[str, Any]:
        serialized = []

        for item in self.items:
            if hasattr(
                item,
                "to_dict",
            ):
                serialized.append(
                    item.to_dict()
                )
            else:
                serialized.append(
                    item
                )

        return {
            "items": serialized,
            "pagination": (
                self.pagination.to_transport()
            ),
            "metadata": self.metadata,
        }