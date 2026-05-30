from __future__ import annotations

import sys
import platform
import warnings
from typing import Any, Dict, Optional, Tuple

from sdk_python.version import __version__


"""
WAY SDK Compatibility Layer.

This module ensures forward and backward compatibility across:
- Python versions
- Runtime environments (local, Docker, cloud)
- Dependency variations
- Internal SDK evolution

It acts as a safe abstraction layer to prevent breaking changes
from propagating into user applications.
"""


# =========================================================
# PYTHON VERSION COMPATIBILITY
# =========================================================

MIN_PYTHON_VERSION: Tuple[int, int] = (3, 10)
MAX_TESTED_PYTHON_VERSION: Tuple[int, int] = (3, 13)


def get_python_version() -> Tuple[int, int, int]:
    """
    Returns current Python version as tuple.
    """
    return sys.version_info[:3]


def is_supported_python() -> bool:
    """
    Check if current Python version is officially supported.
    """
    major, minor, _ = sys.version_info[:3]
    return (major, minor) >= MIN_PYTHON_VERSION


def assert_python_compatibility() -> None:
    """
    Hard fail if Python version is unsupported.
    """
    if not is_supported_python():
        raise RuntimeError(
            f"WAY SDK requires Python >= {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}"
        )


# =========================================================
# RUNTIME ENVIRONMENT DETECTION
# =========================================================

def get_runtime_info() -> Dict[str, Any]:
    """
    Collect runtime environment metadata.
    Useful for debugging, telemetry, and support.
    """

    return {
        "sdk_version": __version__,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "system": platform.system(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
    }


def is_running_in_docker() -> bool:
    """
    Detect Docker container environment.
    """
    try:
        with open("/proc/1/cgroup", "r") as f:
            return "docker" in f.read()
    except Exception:
        return False


def is_running_in_cloud() -> bool:
    """
    Heuristic detection for cloud environments.
    (AWS / GCP / Azure / generic containers)
    """
    cloud_indicators = [
        "AWS_EXECUTION_ENV",
        "GCP_PROJECT",
        "AZURE_FUNCTIONS_ENVIRONMENT",
    ]

    return any(env in __import__("os").environ for env in cloud_indicators)


# =========================================================
# FEATURE COMPATIBILITY HELPERS
# =========================================================

def warn_deprecated(feature: str, replacement: Optional[str] = None) -> None:
    """
    Emit deprecation warning for SDK users.
    """
    message = f"[WAY SDK] Feature '{feature}' is deprecated."

    if replacement:
        message += f" Use '{replacement}' instead."

    warnings.warn(message, DeprecationWarning, stacklevel=2)


def ensure_feature_flag(
    flags: Dict[str, Any],
    key: str,
    default: Any = False,
) -> Any:
    """
    Safe feature flag access with fallback compatibility.
    Prevents KeyError in older SDK configurations.
    """
    return flags.get(key, default)


# =========================================================
# API COMPATIBILITY LAYER
# =========================================================

def normalize_api_response(response: Any) -> Any:
    """
    Normalize API responses across SDK versions.

    This ensures backward compatibility when backend evolves.
    """

    if response is None:
        return {}

    # Already normalized dict
    if isinstance(response, dict):
        return response

    # DRF-style response object
    if hasattr(response, "data"):
        return response.data

    # Requests-style response
    if hasattr(response, "json"):
        try:
            return response.json()
        except Exception:
            return {"raw": response.text}

    return {"value": response}


def extract_error_message(error: Any) -> str:
    """
    Normalize error objects across transport layers.
    """

    if isinstance(error, Exception):
        return str(error)

    if isinstance(error, dict):
        return error.get("message", str(error))

    return str(error)


# =========================================================
# SDK COMPATIBILITY CHECK
# =========================================================

def check_sdk_compatibility(min_version: str) -> bool:
    """
    Check SDK version compatibility.
    """

    def parse(v: str) -> Tuple[int, int, int]:
        return tuple(map(int, v.split(".")))  # type: ignore

    current = parse(__version__)
    required = parse(min_version)

    return current >= required


# =========================================================
# SAFE FALLBACK UTILITIES
# =========================================================

def safe_getattr(obj: Any, attr: str, default: Any = None) -> Any:
    """
    Safe getattr with fallback.
    """
    return getattr(obj, attr, default)


def safe_import(module: str) -> Optional[Any]:
    """
    Safe dynamic import helper.
    Prevents hard failures in optional dependencies.
    """
    try:
        return __import__(module, fromlist=["*"])
    except ImportError:
        return None


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "MIN_PYTHON_VERSION",
    "MAX_TESTED_PYTHON_VERSION",
    "get_python_version",
    "is_supported_python",
    "assert_python_compatibility",
    "get_runtime_info",
    "is_running_in_docker",
    "is_running_in_cloud",
    "warn_deprecated",
    "ensure_feature_flag",
    "normalize_api_response",
    "extract_error_message",
    "check_sdk_compatibility",
    "safe_getattr",
    "safe_import",
]