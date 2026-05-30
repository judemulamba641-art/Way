from __future__ import annotations

import json
from typing import Any, Dict, Union, Optional


# =========================================================
# CORE SERIALIZATION
# =========================================================

def dumps(
    data: Any,
    *,
    indent: Optional[int] = None,
    sort_keys: bool = False,
    ensure_ascii: bool = False,
) -> str:
    """
    Safe JSON serialization for SDK usage.

    Designed for:
    - API payloads
    - logs
    - telemetry events
    - caching layer
    """

    return json.dumps(
        data,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=ensure_ascii,
        separators=(",", ":"),
    )


def loads(data: Union[str, bytes]) -> Any:
    """
    Strict JSON deserialization.

    Raises:
        json.JSONDecodeError if invalid JSON
    """
    if isinstance(data, bytes):
        data = data.decode("utf-8")

    return json.loads(data)


# =========================================================
# SAFE OPERATIONS
# =========================================================

def try_dumps(
    data: Any,
    *,
    default: str = "{}",
    **kwargs: Any,
) -> str:
    """
    Safe JSON serialization with fallback.
    Prevents crashes in logging/telemetry.
    """
    try:
        return dumps(data, **kwargs)
    except Exception:
        return default


def try_loads(
    data: Union[str, bytes],
    *,
    default: Any = None,
) -> Any:
    """
    Safe JSON parsing with fallback.
    """
    try:
        return loads(data)
    except Exception:
        return default


# =========================================================
# NORMALIZATION HELPERS
# =========================================================

def normalize_json(data: Any) -> Any:
    """
    Normalize SDK data into JSON-safe structure.

    Converts:
    - datetime → iso string (future hook via utils.datetime)
    - sets → list
    - tuples → list
    """

    if data is None:
        return None

    if isinstance(data, (str, int, float, bool)):
        return data

    if isinstance(data, dict):
        return {k: normalize_json(v) for k, v in data.items()}

    if isinstance(data, (list, tuple)):
        return [normalize_json(v) for v in data]

    if isinstance(data, set):
        return [normalize_json(v) for v in data]

    # fallback: convert unknown objects safely
    return str(data)


# =========================================================
# DIFF / DEBUG HELPERS
# =========================================================

def pretty(data: Any) -> str:
    """
    Pretty-print JSON for debugging purposes.
    """
    return dumps(data, indent=2, sort_keys=True)


def compact(data: Any) -> str:
    """
    Compact JSON representation (minified).
    """
    return dumps(data, indent=None)


# =========================================================
# JSON MERGING (SDK USEFUL)
# =========================================================

def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two JSON-compatible dictionaries.

    Values in b override values in a.
    """

    result = dict(a)

    for key, value in b.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


# =========================================================
# VALIDATION
# =========================================================

def is_json_serializable(data: Any) -> bool:
    """
    Check if data can be JSON serialized.
    """
    try:
        json.dumps(data)
        return True
    except Exception:
        return False