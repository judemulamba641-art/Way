from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from sdk_python.config import Config
from sdk_python.version import __version__


@dataclass(slots=True)
class Settings:
    """
    WAY SDK Runtime Settings.

    This layer sits on top of Config and provides:
    - normalized runtime values
    - computed properties
    - framework interoperability layer
    - SDK identity (user-agent, version binding)
    - safe execution-ready configuration

    IMPORTANT:
    This class should never read environment variables directly.
    It only consumes Config.
    """

    # -----------------------------
    # Core connection
    # -----------------------------
    base_url: str
    api_key: Optional[str]

    # -----------------------------
    # Transport layer
    # -----------------------------
    timeout: int
    retries: int
    max_connections: int
    backoff_factor: float

    # -----------------------------
    # Environment
    # -----------------------------
    environment: str
    region: Optional[str]
    debug: bool

    # -----------------------------
    # Observability
    # -----------------------------
    enable_logging: bool
    enable_tracing: bool

    # -----------------------------
    # Identity
    # -----------------------------
    user_agent: str
    sdk_version: str

    # -----------------------------
    # Extensions
    # -----------------------------
    feature_flags: Dict[str, Any]
    extra: Dict[str, Any]

    # =========================================================
    # FACTORY
    # =========================================================

    @classmethod
    def from_config(cls, config: Config) -> "Settings":
        """
        Build runtime settings from Config.

        This is the ONLY entrypoint for creating Settings.
        Ensures consistent normalization across SDK usage.
        """

        config.validate()

        return cls(
            base_url=config.base_url.rstrip("/"),
            api_key=config.api_key,
            timeout=config.timeout,
            retries=config.retries,
            max_connections=config.max_connections,
            backoff_factor=config.backoff_factor,
            environment=config.environment.lower(),
            region=config.region,
            debug=config.debug,
            enable_logging=config.enable_logging,
            enable_tracing=config.enable_tracing,
            sdk_version=__version__,
            user_agent=cls._build_user_agent(config),
            feature_flags=config.feature_flags or {},
            extra=config.extra or {},
        )

    # =========================================================
    # INTERNAL DERIVATIONS
    # =========================================================

    @staticmethod
    def _build_user_agent(config: Config) -> str:
        """
        Build SDK User-Agent string.

        Format:
        WAY-Python-SDK/{version} ({env}; {region})
        """

        env = config.environment.lower()
        region = config.region or "global"

        return f"WAY-Python-SDK/{__version__} ({env}; {region})"

    # =========================================================
    # ENVIRONMENT HELPERS
    # =========================================================

    def is_production(self) -> bool:
        return self.environment == "production"

    def is_staging(self) -> bool:
        return self.environment == "staging"

    def is_development(self) -> bool:
        return self.environment in ("dev", "development")

    def is_debug(self) -> bool:
        return self.debug

    # =========================================================
    # TRANSPORT HELPERS
    # =========================================================

    def get_timeout(self) -> int:
        """
        Effective timeout for requests.
        Future hook: per-route override support.
        """
        return self.timeout

    def get_retries(self) -> int:
        """
        Retry policy for transport layer.
        """
        return self.retries

    def get_backoff_factor(self) -> float:
        """
        Backoff multiplier for retry system.
        """
        return self.backoff_factor

    # =========================================================
    # FEATURE FLAGS
    # =========================================================

    def feature(self, key: str, default: Any = None) -> Any:
        """
        Safe access to feature flags.
        """
        return self.feature_flags.get(key, default)

    def has_feature(self, key: str) -> bool:
        """
        Check if a feature flag is enabled.
        """
        return key in self.feature_flags

    # =========================================================
    # VALIDATION / SAFETY
    # =========================================================

    def assert_ready(self) -> None:
        """
        Ensure SDK is ready for execution.

        Raises:
            RuntimeError: if configuration is incomplete or invalid
        """

        if not self.base_url:
            raise RuntimeError("WAY SDK: base_url is missing")

        if self.timeout <= 0:
            raise RuntimeError("WAY SDK: invalid timeout")

        if self.retries < 0:
            raise RuntimeError("WAY SDK: invalid retries")

        if self.api_key is None:
            raise RuntimeError(
                "WAY SDK: api_key is missing (authentication required)"
            )

    # =========================================================
    # SERIALIZATION (SAFE)
    # =========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Safe representation of settings for debugging / telemetry.
        Never includes secrets.
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
            "sdk_version": self.sdk_version,
            "feature_flags": list(self.feature_flags.keys()),
        }

    def __repr__(self) -> str:
        return (
            f"<Settings env={self.environment} "
            f"base_url={self.base_url} "
            f"timeout={self.timeout} "
            f"retries={self.retries}>"
        )