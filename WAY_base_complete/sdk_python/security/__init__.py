"""
WAY SDK Security Module.

This module provides cryptographic and security primitives used across the SDK:

- hashing (data integrity, password hashing, signatures)
- signing (request signing, HMAC, integrity validation)
- encryption (sensitive payload protection)
- validation (security-level input validation)

Design principles:
- zero dependency on transport/client layers
- pure cryptographic + validation logic only
- reusable across auth, storage, transport, realtime
- stable public API surface for long-term compatibility
"""

from sdk_python.security.hashing import (
    hash_sha256,
    hash_sha512,
    verify_hash,
)

from sdk_python.security.signing import (
    sign_hmac,
    verify_signature,
)

from sdk_python.security.encryption import (
    encrypt,
    decrypt,
)

from sdk_python.security.validator import (
    validate_payload_signature,
    validate_secure_string,
)


# =========================================================
# PUBLIC API SURFACE
# =========================================================

__all__ = [
    # hashing
    "hash_sha256",
    "hash_sha512",
    "verify_hash",

    # signing
    "sign_hmac",
    "verify_signature",

    # encryption
    "encrypt",
    "decrypt",

    # validation
    "validate_payload_signature",
    "validate_secure_string",
]