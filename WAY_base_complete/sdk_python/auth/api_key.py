# sdk_python/auth/api_key.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict

from sdk_python.auth.base import (
    BaseAuthStrategy,
    StatelessAuthStrategy,
    AuthType,
    AuthCredentials,
    AuthContext,
    AuthResult,
    AuthError,
)


@dataclass(frozen=True, slots=True)
class APIKeyConfig:
    """
    Normalized API key configuration.

    Supports flexible header/query injection strategies.
    """
    key: str
    prefix: str = "ApiKey"
    header_name: str = "Authorization"
    query_param: Optional[str] = None  # optional fallback (rare SaaS use-case)
    metadata: Dict[str, str] = None


class APIKeyAuth(StatelessAuthStrategy):
    """
    API Key authentication strategy.

    Designed for:
    - SaaS APIs (WAY backend)
    - server-to-server auth
    - lightweight client auth
    - stateless secure requests
    """

    auth_type: AuthType = AuthType.API_KEY

    def _authenticate(
        self,
        credentials: AuthCredentials,
        context: AuthContext
    ) -> AuthResult:
        """
        Build API key authentication result.
        """

        config = self._extract_config(credentials)

        # Primary mechanism: Authorization header
        headers = {
            config.header_name: f"{config.prefix} {config.key}"
        }

        # Optional fallback: query param injection (rare but supported)
        query_params = {}
        if config.query_param:
            query_params[config.query_param] = config.key

        return AuthResult(
            headers=headers,
            query_params=query_params,
            signature=None,
            expires_at=None,  # API keys are usually long-lived
        )

    def _extract_config(self, credentials: AuthCredentials) -> APIKeyConfig:
        """
        Validate and normalize API key credentials.
        """

        key = credentials.require("api_key")

        if not isinstance(key, str) or not key.strip():
            raise AuthError("API key must be a non-empty string")

        prefix = credentials.get("prefix", "ApiKey")
        header_name = credentials.get("header_name", "Authorization")
        query_param = credentials.get("query_param")

        metadata = credentials.get("metadata", {})

        if not isinstance(prefix, str):
            raise AuthError("prefix must be a string")

        if not isinstance(header_name, str):
            raise AuthError("header_name must be a string")

        if query_param is not None and not isinstance(query_param, str):
            raise AuthError("query_param must be a string or None")

        if not isinstance(metadata, dict):
            raise AuthError("metadata must be a dict")

        return APIKeyConfig(
            key=key,
            prefix=prefix,
            header_name=header_name,
            query_param=query_param,
            metadata=metadata,
        )