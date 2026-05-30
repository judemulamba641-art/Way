from __future__ import annotations

import base64
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Mapping,
    Sequence,
    TypeVar,
)
from uuid import UUID

from sdk_python.models.base import BaseModel


__all__ = [
    "TransportSerializer",
    "TransportDeserializer",
]


T = TypeVar("T")


class TransportSerializer:
    """
    Enterprise transport serializer.

    Responsibilities:
    - dataclass → dict
    - BaseModel → dict
    - enum normalization
    - datetime normalization
    - JSON serialization
    - bytes normalization
    - nested recursive conversion
    """

    @classmethod
    def normalize(
        cls,
        value: Any,
    ) -> Any:
        if value is None:
            return None

        if isinstance(value, BaseModel):
            return cls.normalize(value.to_dict())

        if is_dataclass(value):
            return cls.normalize(asdict(value))

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, Path):
            return str(value)

        if isinstance(value, bytes):
            return base64.b64encode(value).decode("utf-8")

        if isinstance(value, Mapping):
            return {
                str(key): cls.normalize(item)
                for key, item in value.items()
            }

        if isinstance(value, Sequence) and not isinstance(
            value,
            (str, bytes, bytearray),
        ):
            return [
                cls.normalize(item)
                for item in value
            ]

        return value

    @classmethod
    def to_dict(
        cls,
        value: Any,
    ) -> dict[str, Any]:
        normalized = cls.normalize(value)

        if normalized is None:
            return {}

        if not isinstance(normalized, dict):
            raise TypeError(
                "Serialized value must resolve to dict.",
            )

        return normalized

    @classmethod
    def dumps(
        cls,
        value: Any,
        *,
        indent: int | None = None,
        ensure_ascii: bool = False,
        sort_keys: bool = False,
    ) -> str:
        normalized = cls.normalize(value)

        return json.dumps(
            normalized,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            separators=(",", ":"),
        )

    @classmethod
    def to_bytes(
        cls,
        value: Any,
    ) -> bytes:
        return cls.dumps(value).encode("utf-8")


class TransportDeserializer:
    """
    Enterprise transport deserializer.

    Responsibilities:
    - json string → dict
    - bytes → json
    - dataclass hydration helper
    - model hydration helper
    """

    @classmethod
    def loads(
        cls,
        value: str,
    ) -> Any:
        if not value:
            return None

        return json.loads(value)

    @classmethod
    def from_bytes(
        cls,
        value: bytes | bytearray,
    ) -> Any:
        if not value:
            return None

        return cls.loads(
            bytes(value).decode("utf-8"),
        )

    @classmethod
    def to_model(
        cls,
        model_type: type[T],
        payload: Mapping[str, Any] | None,
    ) -> T | None:
        if payload is None:
            return None

        if hasattr(model_type, "from_dict"):
            return model_type.from_dict(payload)  # type: ignore[return-value]

        return model_type(**payload)

    @classmethod
    def to_models(
        cls,
        model_type: type[T],
        payload: Sequence[Mapping[str, Any]],
    ) -> list[T]:
        return [
            cls.to_model(model_type, item)
            for item in payload
            if item is not None
        ]