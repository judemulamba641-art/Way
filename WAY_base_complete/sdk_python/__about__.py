"""
WAY Python SDK package metadata.

Centralized package metadata for:
- packaging
- runtime diagnostics
- telemetry
- introspection
- version visibility

This module must remain lightweight and import-safe.
"""

from __future__ import annotations

from typing import Final

__title__: Final[str] = "way-sdk"

__description__: Final[str] = (
    "Official enterprise-grade Python SDK for the WAY AI platform."
)

__author__: Final[str] = "WAY Engineering"

__email__: Final[str] = "engineering@way.local"

__license__: Final[str] = "Proprietary"

__copyright__: Final[str] = "Copyright © WAY"

__url__: Final[str] = "https://way.local"

__docs_url__: Final[str] = "https://way.local/docs"

__repository_url__: Final[str] = "https://way.local/repository"

__keywords__: Final[tuple[str, ...]] = (
    "way",
    "way-sdk",
    "ai",
    "django",
    "rest",
    "channels",
    "celery",
    "redis",
    "postgresql",
    "sdk",
    "python",
)

PACKAGE_METADATA: Final[dict[str, str | tuple[str, ...]]] = {
    "title": __title__,
    "description": __description__,
    "author": __author__,
    "email": __email__,
    "license": __license__,
    "copyright": __copyright__,
    "url": __url__,
    "docs_url": __docs_url__,
    "repository_url": __repository_url__,
    "keywords": __keywords__,
}


def get_package_metadata() -> dict[str, str | tuple[str, ...]]:
    """
    Return immutable-style package metadata copy.

    Useful for:
    - diagnostics
    - structured logging
    - CLI version output
    - telemetry payloads

    Returns:
        dict containing package metadata
    """
    return dict(PACKAGE_METADATA)