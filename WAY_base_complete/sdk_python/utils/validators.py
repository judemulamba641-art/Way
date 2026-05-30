from __future__ import annotations

import re
from typing import Any, Optional, Dict


# =========================================================
# PATTERNS
# =========================================================

API_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{10,}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# =========================================================
# CORE VALIDATORS
# =========================================================

def validate_api_key(key: Optional[str]) -> bool:
    """
    Validate WAY API key format.
    """
    if not isinstance(key, str):
        return False
    return bool(API_KEY_PATTERN.match(key))


def validate_email(email: str) -> bool:
    """
    Validate email format (lightweight check).
    """
    return bool(EMAIL_PATTERN.match(email))


def validate_non_empty(value: Any) -> bool:
    """
    Ensure value is not empty.
    """
    if value is None:
        return False

    if isinstance(value, str):
        return len(value.strip()) > 0

    if isinstance(value, (list, dict, set, tuple)):
        return len(value) > 0

    return True


def validate_payload(payload: Dict[str, Any]) -> bool:
    """
    Basic validation for SDK payloads.
    Ensures it's a non-empty dict.
    """
    return isinstance(payload, dict) and len(payload) > 0


# =========================================================
# SAFE SANITIZATION
# =========================================================

def sanitize_string(value: str) -> str:
    """
    Sanitize input string (trim + remove control chars).
    """
    if not isinstance(value, str):
        return ""

    return "".join(c for c in value.strip() if c.isprintable())


def clamp_length(value: str, max_length: int = 255) -> str:
    """
    Clamp string length safely.
    """
    if not isinstance(value, str):
        return ""

    return value[:max_length]