"""
WAY SDK Python - Base Models
============================

Core abstractions used across all SDK models.

Features:
- UUID identifiers
- UTC timestamps
- strict serialization
- immutable-safe update
- validation hooks
- dict/json conversion
- extensible mixins
"""

from __future__ import annotations

import json
import uuid
from copy import deepcopy
from dataclasses import MISSING
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from dataclasses import replace
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import Mapping
from typing import Optional
from typing import Type
from typing import TypeVar


T = TypeVar("T", bound="BaseModel")


# =========================================================
# Time utilities
# =========================================================
def utc_now() -> datetime:
    """
    Return timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)


def generate_id() -> str:
    """
    Generate secure UUID4 string.
    """
    return str(uuid.uuid4())


# =========================================================
# Serialization mixin
# =========================================================
class SerializableMixin:
    """
    JSON and dict conversion helpers.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert dataclass to dictionary.
        """
        return asdict(self)

    def to_json(
        self,
        *,
        indent: Optional[int] = None,
        sort_keys: bool = False,
    ) -> str:
        """
        Serialize to JSON string.
        """
        return json.dumps(
            self.to_dict(),
            default=self._json_encoder,
            indent=indent,
            sort_keys=sort_keys,
        )

    @classmethod
    def from_dict(
        cls: Type[T],
        data: Mapping[str, Any],
    ) -> T:
        """
        Instantiate model from dictionary.
        """
        return cls(**dict(data))

    @classmethod
    def from_json(
        cls: Type[T],
        payload: str,
    ) -> T:
        """
        Deserialize JSON payload.
        """
        data = json.loads(payload)
        return cls.from_dict(data)

    @staticmethod
    def _json_encoder(value: Any) -> Any:
        """
        Custom serializer.
        """
        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, uuid.UUID):
            return str(value)

        return value


# =========================================================
# Timestamp mixin
# =========================================================
@dataclass(slots=True)
class TimestampMixin:
    """
    Automatic timestamps.
    """

    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        """
        Update modification timestamp.
        """
        self.updated_at = utc_now()


# =========================================================
# Identifiable mixin
# =========================================================
@dataclass(slots=True)
class IdentifiableMixin:
    """
    UUID identity.
    """

    id: str = field(default_factory=generate_id)


# =========================================================
# Base model
# =========================================================
@dataclass(slots=True)
class BaseModel(
    SerializableMixin,
    TimestampMixin,
    IdentifiableMixin,
):
    """
    Root model abstraction.

    Lifecycle:
    - construct
    - validate
    - serialize
    - clone/update
    """

    __frozen__: ClassVar[bool] = False

    # -----------------------------------------------------
    # Dataclass lifecycle
    # -----------------------------------------------------
    def __post_init__(self) -> None:
        self.validate()

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------
    def validate(self) -> None:
        """
        Override in subclasses.

        Example:
            if not self.email:
                raise ValueError(...)
        """
        return

    # -----------------------------------------------------
    # Cloning
    # -----------------------------------------------------
    def clone(self: T) -> T:
        """
        Deep copy model.
        """
        return deepcopy(self)

    def update(
        self: T,
        **changes: Any,
    ) -> T:
        """
        Return updated copy.

        Safe immutable pattern.
        """
        obj = replace(self, **changes)

        if isinstance(obj, TimestampMixin):
            obj.touch()

        obj.validate()

        return obj

    # -----------------------------------------------------
    # Merge helper
    # -----------------------------------------------------
    def merge(
        self: T,
        data: Mapping[str, Any],
    ) -> T:
        """
        Merge dict values.
        """
        return self.update(**dict(data))

    # -----------------------------------------------------
    # Utility
    # -----------------------------------------------------
    def is_equal(self, other: object) -> bool:
        """
        Compare by dictionary.
        """
        if not isinstance(other, BaseModel):
            return False

        return self.to_dict() == other.to_dict()

    def require(
        self,
        field_name: str,
    ) -> Any:
        """
        Require field value.
        """
        value = getattr(self, field_name)

        if value is None:
            raise ValueError(
                f"{self.__class__.__name__}.{field_name} is required"
            )

        return value

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------
    def __repr__(self) -> str:
        values = []

        for f in fields(self):
            values.append(
                f"{f.name}={getattr(self, f.name)!r}"
            )

        joined = ", ".join(values)

        return f"{self.__class__.__name__}({joined})"


# =========================================================
# Generic collection wrapper
# =========================================================
U = TypeVar("U")


@dataclass(slots=True)
class ModelCollection(Generic[U]):
    """
    Generic typed collection.
    """

    items: list[U] = field(default_factory=list)

    def add(self, item: U) -> None:
        self.items.append(item)

    def extend(self, values: list[U]) -> None:
        self.items.extend(values)

    def clear(self) -> None:
        self.items.clear()

    def first(self) -> Optional[U]:
        return self.items[0] if self.items else None

    def last(self) -> Optional[U]:
        return self.items[-1] if self.items else None

    def count(self) -> int:
        return len(self.items)

    def to_list(self) -> list[U]:
        return list(self.items)

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)