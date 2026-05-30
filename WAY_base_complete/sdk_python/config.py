from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union
import os
import json


@dataclass(slots=True)
class Config:
    """
    WAY SDK Core Configuration.

    This is the foundational configuration layer for the SDK.

    Design principles:
    - Environment-driven (12-factor app style)
    - Override-friendly (dict / runtime injection / tests)
    - Framework-agnostic (Django / FastAPI / pure Python)
    - Safe defaults for production stability
    - Extensible for future enterprise features

    Responsibilities:
    - API connection settings
    - Authentication configuration
    - Transport tuning (timeouts, retries)
    - Environment selection
    - Debug / observability flags
    """

    # -----------------------------
    # Core connection settings
    # -----------------------------
    base_url: str = field(
        default_factory=lambda: os.getenv("WAY_BASE_URL", "https://api.way.local")
    )

    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("WAY_API_KEY")
    )

    environment: str = field(
        default_factory=lambda: os.getenv("WAY_ENV", "production")
    )

    region: Optional[str] = field(
        default_factory=lambda: os.getenv("WAY_REGION")
    )

    # -----------------------------
    # Transport configuration
    # -----------------------------
    timeout: int = field(
        default_factory=lambda: int(os.getenv("WAY_TIMEOUT", "30"))
    )

    retries: int = field(
        default_factory=lambda: int(os.getenv("WAY_RETRIES", "3"))
    )

    max_connections: int = field(
        default_factory=lambda: int(os.getenv("WAY_MAX_CONNECTIONS", "100"))
    )

    backoff_factor: float = field(
        default_factory=lambda: float(os.getenv("WAY_BACKOFF_FACTOR", "0.5"))
    )

    # -----------------------------
    # Debug / observability
    # -----------------------------
    debug: bool = field(
        default_factory=lambda: os.getenv("WAY_DEBUG", "false").lower() == "true"
    )

    enable_logging: bool = field(
        default_factory=lambda: os.getenv("WAY_LOGGING", "true").lower() == "true"
    )

    enable_tracing: bool = field(
        default_factory=lambda: os.getenv("WAY_TRACING", "false").lower() == "true"
    )

    # -----------------------------
    # Feature flags (future-proof)
    # -----------------------------
    feature_flags: Dict[str, Any] = field(default_factory=dict)

    # -----------------------------
    # Extra metadata (extensibility)
    # -----------------------------
    extra: Dict[str, Any] = field(default_factory=dict)

    # =========================================================
    # ENV / FACTORY METHODS
    # =========================================================

    @classmethod
    def from_env(cls) -> "Config":
        """
        Build configuration from environment variables.
        Default entrypoint for production usage.
        """
        return cls()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Build configuration from dictionary (CLI, Django, tests, runtime injection).
        """

        return cls(
            base_url=data.get("base_url", os.getenv("WAY_BASE_URL", "")),
            api_key=data.get("api_key", os.getenv("WAY_API_KEY")),
            environment=data.get("environment", os.getenv("WAY_ENV", "production")),
            region=data.get("region", os.getenv("WAY_REGION")),
            timeout=int(data.get("timeout", os.getenv("WAY_TIMEOUT", 30))),
            retries=int(data.get("retries", os.getenv("WAY_RETRIES", 3))),
            max_connections=int(
                data.get("max_connections", os.getenv("WAY_MAX_CONNECTIONS", 100))
            ),
            backoff_factor=float(
                data.get("backoff_factor", os.getenv("WAY_BACKOFF_FACTOR", 0.5))
            ),
            debug=bool(data.get("debug", os.getenv("WAY_DEBUG", False))),
            enable_logging=bool(
                data.get("enable_logging", os.getenv("WAY_LOGGING", True))
            ),
            enable_tracing=bool(
                data.get("enable_tracing", os.getenv("WAY_TRACING", False))
            ),
            feature_flags=data.get("feature_flags", {}),
            extra=data.get("extra", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Config":
        """
        Build configuration from JSON string (useful for CLI / remote bootstrap).
        """
        return cls.from_dict(json.loads(json_str))

    # =========================================================
    # ENVIRONMENT HELPERS
    # =========================================================

    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    def is_staging(self) -> bool:
        return self.environment.lower() == "staging"

    def is_development(self) -> bool:
        return self.environment.lower() in ("dev", "development")

    def is_debug(self) -> bool:
        return self.debug

    # =========================================================
    # FEATURE FLAGS
    # =========================================================

    def feature(self, key: str, default: Any = None) -> Any:
        """
        Access feature flags safely.
        """
        return self.feature_flags.get(key, default)

    def enable_feature(self, key: str, value: Any = True) -> None:
        """
        Dynamically enable a feature flag at runtime.
        """
        self.feature_flags[key] = value

    # =========================================================
    # SANITIZATION / SAFETY
    # =========================================================

    def validate(self) -> None:
        """
        Validate configuration integrity.

        Raises:
            ValueError: if config is invalid
        """

        if not self.base_url:
            raise ValueError("base_url is required")

        if self.timeout <= 0:
            raise ValueError("timeout must be > 0")

        if self.retries < 0:
            raise ValueError("retries must be >= 0")

    def sanitized(self) -> Dict[str, Any]:
        """
        Return safe config representation (no secrets).
        Useful for logging / debugging / telemetry.
        """

        return {
            "base_url": self.base_url,
            "environment": self.environment,
            "region": self.region,
            "timeout": self.timeout,
            "retries": self.retries,
            "max_connections": self.max_connections,
            "backoff_factor": self.backoff_factor,
            "debug": self.debug,
            "enable_logging": self.enable_logging,
            "enable_tracing": self.enable_tracing,
            "feature_flags": list(self.feature_flags.keys()),
            "extra_keys": list(self.extra.keys()),
        }