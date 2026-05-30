from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional, Union


# =========================================================
# CORE TIME UTILITIES
# =========================================================

def utc_now() -> datetime:
    """
    Returns current UTC time (timezone-aware).

    This is the ONLY safe default datetime for SDK usage.
    """
    return datetime.now(timezone.utc)


def utc_timestamp() -> float:
    """
    Returns current UTC timestamp in seconds.
    """
    return utc_now().timestamp()


def from_timestamp(ts: Union[int, float]) -> datetime:
    """
    Convert UNIX timestamp to timezone-aware UTC datetime.
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc)


# =========================================================
# SERIALIZATION HELPERS
# =========================================================

def to_iso(dt: Optional[datetime] = None) -> str:
    """
    Convert datetime to ISO 8601 string.

    Always returns UTC ISO format.
    """
    dt = dt or utc_now()

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc).isoformat()


def from_iso(date_str: str) -> datetime:
    """
    Parse ISO 8601 string into UTC datetime.

    Automatically normalizes timezone.
    """
    dt = datetime.fromisoformat(date_str)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


# =========================================================
# TIME MANIPULATION HELPERS
# =========================================================

def add_seconds(dt: Optional[datetime], seconds: int) -> datetime:
    """
    Add seconds to a datetime safely.
    """
    dt = dt or utc_now()
    return dt + timedelta(seconds=seconds)


def add_minutes(dt: Optional[datetime], minutes: int) -> datetime:
    """
    Add minutes to a datetime safely.
    """
    dt = dt or utc_now()
    return dt + timedelta(minutes=minutes)


def add_hours(dt: Optional[datetime], hours: int) -> datetime:
    """
    Add hours to a datetime safely.
    """
    dt = dt or utc_now()
    return dt + timedelta(hours=hours)


# =========================================================
# COMPARISON HELPERS
# =========================================================

def is_expired(dt: datetime) -> bool:
    """
    Check if datetime is in the past.
    """
    return dt < utc_now()


def is_future(dt: datetime) -> bool:
    """
    Check if datetime is in the future.
    """
    return dt > utc_now()


def time_diff_seconds(a: datetime, b: datetime) -> float:
    """
    Return difference in seconds between two datetimes.
    """
    return abs((a - b).total_seconds())


# =========================================================
# SAFE NORMALIZATION
# =========================================================

def ensure_utc(dt: datetime) -> datetime:
    """
    Force datetime into UTC timezone.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)