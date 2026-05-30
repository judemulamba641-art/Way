from __future__ import annotations

import re
import json
from typing import Any, Dict, Optional


# =========================================================
# BASIC PATTERNS
# =========================================================

SAFE_STRING_PATTERN = re.compile(r"^[\w\-\.\@\:\s]+$")


# =========================================================
# CORE VALIDATION
# =========================================================

def validate_secure_string(value: Any) -> bool:
    """
    Validate that a string is safe for signing or transport.
    Prevents injection of control characters or malformed input.
    """

    if not isinstance(value, str):
        return False

    return bool(SAFE_STRING_PATTERN.match(value))


def validate_payload_signature(payload: Dict[str, Any]) -> bool:
    """
    Validate that payload is safe for signing.

    Rules:
    - must be dict
    - must be JSON serializable
    - must not contain None keys
    """

    if not isinstance(payload, dict):
        return False

    try:
        # ensure JSON serializable
        json.dumps(payload)
    except Exception:
        return False

    # ensure no None keys
    for k in payload.keys():
        if k is None:
            return False

    return True


# =========================================================
# STRICT SANITIZATION
# =========================================================

def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean payload before transport/signing.

    - removes None keys
    - converts unsafe values to strings
    """

    cleaned: Dict[str, Any] = {}

    for k, v in payload.items():
        if k is None:
            continue

        if isinstance(v, (dict, list, str, int, float, bool)) or v is None:
            cleaned[str(k)] = v if v is not None else ""
        else:
            cleaned[str(k)] = str(v)

    return cleaned