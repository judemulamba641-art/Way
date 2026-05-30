from __future__ import annotations

import hashlib
import hmac
from typing import Optional


# =========================================================
# CORE HASHING FUNCTIONS
# =========================================================

def hash_sha256(data: str) -> str:
    """
    Generate SHA-256 hash of input string.
    """
    if not isinstance(data, str):
        data = str(data)

    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def hash_sha512(data: str) -> str:
    """
    Generate SHA-512 hash of input string.
    """
    if not isinstance(data, str):
        data = str(data)

    return hashlib.sha512(data.encode("utf-8")).hexdigest()


# =========================================================
# SAFE VERIFICATION
# =========================================================

def verify_hash(data: str, expected_hash: str, algorithm: str = "sha256") -> bool:
    """
    Verify hash integrity safely.

    Args:
        data: original data
        expected_hash: hash to compare
        algorithm: sha256 or sha512
    """

    if algorithm == "sha256":
        computed = hash_sha256(data)
    elif algorithm == "sha512":
        computed = hash_sha512(data)
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    return hmac.compare_digest(computed, expected_hash)