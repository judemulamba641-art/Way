from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, TypeVar, Dict, List


T = TypeVar("T")


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def ensure_not_none(value: Any, message: str = "Value cannot be None") -> Any:
    """
    Ensure value is not None.

    Raises:
        ValueError: if value is None
    """
    if value is None:
        raise ValueError(message)
    return value


def first_non_none(*values: Any) -> Any:
    """
    Return first non-None value in a list of candidates.
    """
    for v in values:
        if v is not None:
            return v
    return None


def coalesce(*values: Any) -> Any:
    """
    Alias for first_non_none (SQL-style COALESCE).
    """
    return first_non_none(*values)


# =========================================================
# SAFE FUNCTION EXECUTION
# =========================================================

def safe_call(fn: Callable[..., T], *args: Any, default: Any = None, **kwargs: Any) -> Any:
    """
    Execute a function safely.

    Returns default if any exception occurs.
    """
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default


def try_or_raise(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Execute function and propagate errors normally.

    Useful when you want explicit failure instead of fallback.
    """
    return fn(*args, **kwargs)


# =========================================================
# COLLECTION HELPERS
# =========================================================

def chunk_list(data: List[T], size: int) -> List[List[T]]:
    """
    Split a list into chunks of fixed size.
    """
    return [data[i:i + size] for i in range(0, len(data), size)]


def flatten(nested: Iterable[Iterable[T]]) -> List[T]:
    """
    Flatten a nested iterable structure.
    """
    return [item for sub in nested for item in sub]


def unique_list(data: List[T]) -> List[T]:
    """
    Return list with duplicates removed while preserving order.
    """
    seen = set()
    result: List[T] = []

    for item in data:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


# =========================================================
# DICTIONARY HELPERS
# =========================================================

def deep_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Safely access nested dictionary values using dot notation.

    Example:
        deep_get(user, "profile.settings.theme")
    """
    keys = path.split(".")
    current = data

    try:
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key, default)
        return current
    except Exception:
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries (later overrides earlier).
    """
    result: Dict[str, Any] = {}

    for d in dicts:
        result.update(d or {})

    return result


# =========================================================
# STRING HELPERS
# =========================================================

def safe_strip(value: Optional[str]) -> str:
    """
    Safely strip a string.
    """
    return value.strip() if isinstance(value, str) else ""


def to_bool(value: Any) -> bool:
    """
    Convert common values to boolean.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")

    if isinstance(value, (int, float)):
        return value != 0

    return False


# =========================================================
# FUNCTION PIPELINE HELPERS
# =========================================================

def pipe(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """
    Functional-style pipeline execution.

    Example:
        pipe(data, clean, validate, transform)
    """
    result = value
    for fn in funcs:
        result = fn(result)
    return result


def identity(x: T) -> T:
    """
    Identity function (useful for defaults).
    """
    return x