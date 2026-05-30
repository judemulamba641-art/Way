from __future__ import annotations

import base64
import os
from typing import Optional


# =========================================================
# SIMPLE SYMMETRIC ENCRYPTION (SDK SAFE BASE LAYER)
# =========================================================

# NOTE:
# This is a lightweight XOR-based fallback encryption layer.
# In production, you can swap this with:
# - cryptography.fernet
# - AWS KMS
# - OpenSSL backend

_DEFAULT_KEY = os.getenv("WAY_ENCRYPTION_KEY", "way-default-key")


def _derive_key(key: str) -> bytes:
    """
    Derive fixed-length key from input string.
    """
    return key.encode("utf-8")[:32].ljust(32, b"0")


# =========================================================
# ENCRYPTION
# =========================================================

def encrypt(data: str, key: Optional[str] = None) -> str:
    """
    Encrypt string data using simple XOR + base64 encoding.

    NOTE:
    This is a lightweight SDK-level encryption layer.
    For high-security production secrets, replace with KMS/Fernet.
    """

    if not isinstance(data, str):
        data = str(data)

    key_bytes = _derive_key(key or _DEFAULT_KEY)
    data_bytes = data.encode("utf-8")

    encrypted = bytes(
        b ^ key_bytes[i % len(key_bytes)]
        for i, b in enumerate(data_bytes)
    )

    return base64.urlsafe_b64encode(encrypted).decode("utf-8")


# =========================================================
# DECRYPTION
# =========================================================

def decrypt(data: str, key: Optional[str] = None) -> str:
    """
    Decrypt string data encoded by encrypt().
    """

    key_bytes = _derive_key(key or _DEFAULT_KEY)
    decoded = base64.urlsafe_b64decode(data.encode("utf-8"))

    decrypted = bytes(
        b ^ key_bytes[i % len(key_bytes)]
        for i, b in enumerate(decoded)
    )

    return decrypted.decode("utf-8", errors="ignore")