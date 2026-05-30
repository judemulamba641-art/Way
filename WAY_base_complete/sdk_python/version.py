"""
WAY Python SDK version management.

Single source of truth for:
- semantic versioning
- runtime compatibility
- release visibility
- diagnostics
- telemetry

Keep this module lightweight and dependency-free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


VERSION: Final[tuple[int, int, int]] = (1, 0, 0)

__version__: Final[str] = ".".join(map(str, VERSION))


@dataclass(slots=True, frozen=True)
class SemanticVersion:
    """
    Strongly typed semantic version.

    Example:
        SemanticVersion(1, 2, 0)
    """

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        for value in (self.major, self.minor, self.patch):
            if value < 0:
                raise ValueError(
                    "Semantic version values must be non-negative integers."
                )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __iter__(self):
        yield self.major
        yield self.minor
        yield self.patch

    def to_tuple(self) -> tuple[int, int, int]:
        """
        Return tuple representation.
        """
        return (
            self.major,
            self.minor,
            self.patch,
        )

    def to_dict(self) -> dict[str, int]:
        """
        Return mapping representation.
        """
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
        }

    def is_compatible_with(
        self,
        other: "SemanticVersion",
    ) -> bool:
        """
        Major-version compatibility check.

        Returns:
            True when compatible.
        """
        return self.major == other.major


SDK_VERSION: Final[SemanticVersion] = SemanticVersion(*VERSION)


def get_version() -> str:
    """
    Return current version string.
    """
    return __version__


def get_version_tuple() -> tuple[int, int, int]:
    """
    Return version tuple.
    """
    return VERSION


def get_semantic_version() -> SemanticVersion:
    """
    Return semantic version object.
    """
    return SDK_VERSION


def parse_version(value: str) -> SemanticVersion:
    """
    Parse version string.

    Args:
        value:
            Semantic version string.

    Raises:
        ValueError:
            Invalid version format.

    Returns:
        Parsed SemanticVersion.
    """
    try:
        major_str, minor_str, patch_str = value.strip().split(".")
        return SemanticVersion(
            major=int(major_str),
            minor=int(minor_str),
            patch=int(patch_str),
        )
    except (AttributeError, ValueError) as exc:
        raise ValueError(
            f"Invalid semantic version: {value!r}"
        ) from exc


def is_version_compatible(value: str) -> bool:
    """
    Check whether external version is SDK compatible.

    Args:
        value:
            External version string.

    Returns:
        Compatibility boolean.
    """
    other = parse_version(value)
    return SDK_VERSION.is_compatible_with(other)