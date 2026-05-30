from __future__ import annotations

import hmac
import hashlib
import time
from typing import Optional, Dict, Any

from sdk_python.security.hashing import hash_sha256


# =========================================================
# SIGNATURE CORE
# =========================================================

def sign_hmac(
    payload: str,
    secret: str,
    *,
    timestamp: Optional[int] = None,
    include_timestamp: bool = True,
) -> str:
    """
    Generate HMAC-SHA256 signature for payload.

    Used for:
    - API request signing
    - webhook validation
    - transport integrity layer
    """

    if not isinstance(payload, str):
        payload = str(payload)

    ts = str(timestamp or int(time.time())) if include_timestamp else ""

    message = f"{ts}.{payload}" if include_timestamp else payload

    signature = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{ts}.{signature}" if include_timestamp else signature


# =========================================================
# VERIFICATION
# =========================================================

def verify_signature(
    payload: str,
    signature: str,
    secret: str,
    *,
    max_age: int = 300,
) -> bool:
    """
    Verify HMAC signature with optional timestamp validation.

    Args:
        payload: original payload
        signature: received signature
        secret: shared secret
        max_age: max allowed age in seconds
    """

    try:
        if "." in signature:
            ts_str, sig = signature.split(".", 1)
            timestamp = int(ts_str)

            # check expiry
            if abs(int(time.time()) - timestamp) > max_age:
                return False

            expected = sign_hmac(payload, secret, timestamp=timestamp)
        else:
            expected = sign_hmac(payload, secret, include_timestamp=False)
            sig = signature

        return hmac.compare_digest(expected, signature)

    except Exception:
        return False