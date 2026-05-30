from __future__ import annotations

"""
WAY storage infrastructure.

Provides:

- local filesystem storage
- S3/object storage adapter
"""

from infrastructure.storage.local import (
    LocalStorage,
)

from infrastructure.storage.s3 import (
    S3Storage,
)

__all__ = [
    "LocalStorage",
    "S3Storage",
]