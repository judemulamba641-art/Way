# sdk_python/auth/jwt.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import time
import base64
import json
import hmac
import hashlib

from sdk_python.auth.base import (
    BaseAuthStrategy,
    AuthType,
    AuthCredentials,
    AuthContext,
    AuthResult,
    AuthError,
)


# ----------------------------
# JWT CONFIGURATION CORE
# ----------------------------

@dataclass(frozen=True, slots=True)
class JWTConfig:
    """
    Normalized JWT configuration.

    Supports HS256 by default (HMAC SHA-256).
    Future-ready for RS256 (via external signing adapter).
    """
    secret: str
    algorithm: str = "HS256"
    issuer: Optional[str] = None
    audience: Optional[str] = None
    expires_in: int = 3600
    header_prefix: str = "Bearer"


# ----------------------------
# JWT STRATEGY
# ----------------------------

class JWTAuth(BaseAuthStrategy):
    """
    Enterprise-grade JWT authentication strategy.

    Features:
    - HS256 signing (default)
    - claims validation
    - expiration handling
    - transport-ready headers
    - future RS256 extension point
    """

    auth_type: AuthType = AuthType.JWT

    # ----------------------------
    # CORE AUTH FLOW
    # ----------------------------

    def _authenticate(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:

        config = self._extract_config(credentials, context)

        header, payload = self._build_jwt_structure(credentials, context, config)
        token = self._encode_jwt(header, payload, config)

        return AuthResult(
            headers={
                "Authorization": f"{config.header_prefix} {token}"
            },
            expires_at=payload.get("exp"),
            signature=token,
        )

    # ----------------------------
    # CONFIG NORMALIZATION
    # ----------------------------

    def _extract_config(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> JWTConfig:

        secret = credentials.require("secret")

        if not isinstance(secret, str) or not secret.strip():
            raise AuthError("JWT secret must be a non-empty string")

        return JWTConfig(
            secret=secret,
            algorithm=credentials.get("algorithm", "HS256"),
            issuer=credentials.get("issuer"),
            audience=credentials.get("audience"),
            expires_in=int(credentials.get("expires_in", 3600)),
            header_prefix=credentials.get("prefix", "Bearer"),
        )

    # ----------------------------
    # JWT STRUCTURE BUILDING
    # ----------------------------

    def _build_jwt_structure(
        self,
        credentials: AuthCredentials,
        context: AuthContext,
        config: JWTConfig
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:

        now = int(time.time())

        header = {
            "typ": "JWT",
            "alg": config.algorithm,
        }

        payload: Dict[str, Any] = {
            "iat": now,
            "exp": now + config.expires_in,
            "service": context.service,
            "endpoint": context.endpoint,
            "method": context.method,
        }

        if config.issuer:
            payload["iss"] = config.issuer

        if config.audience:
            payload["aud"] = config.audience

        # allow custom claims
        custom_claims = credentials.get("claims", {})
        if isinstance(custom_claims, dict):
            payload.update(custom_claims)

        return header, payload

    # ----------------------------
    # JWT ENCODING (HS256)
    # ----------------------------

    def _encode_jwt(
        self,
        header: Dict[str, Any],
        payload: Dict[str, Any],
        config: JWTConfig
    ) -> str:

        if config.algorithm != "HS256":
            raise AuthError(
                f"Unsupported JWT algorithm: {config.algorithm}. "
                "Only HS256 is currently supported."
            )

        header_b64 = self._b64_encode(header)
        payload_b64 = self._b64_encode(payload)

        signing_input = f"{header_b64}.{payload_b64}".encode()

        signature = hmac.new(
            config.secret.encode(),
            signing_input,
            hashlib.sha256
        ).digest()

        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    # ----------------------------
    # UTIL: BASE64 JSON
    # ----------------------------

    def _b64_encode(self, data: Dict[str, Any]) -> str:
        raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    # ----------------------------
    # REFRESH STRATEGY
    # ----------------------------

    def refresh(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        """
        JWT refresh = re-sign with new exp.
        """
        return self.authenticate(credentials, context)