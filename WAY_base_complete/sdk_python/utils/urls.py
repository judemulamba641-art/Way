from __future__ import annotations

from urllib.parse import urljoin, urlencode, urlparse, urlunparse, parse_qsl
from typing import Dict, Any, Optional


# =========================================================
# BASE URL BUILDER
# =========================================================

def build_url(base: str, path: str) -> str:
    """
    Safely join base URL and endpoint path.

    Prevents:
    - double slashes
    - malformed URLs
    """
    return urljoin(base.rstrip("/") + "/", path.lstrip("/"))


# =========================================================
# QUERY PARAMETERS
# =========================================================

def add_query_params(url: str, params: Optional[Dict[str, Any]]) -> str:
    """
    Append query parameters safely to URL.
    """

    if not params:
        return url

    parsed = urlparse(url)
    existing = dict(parse_qsl(parsed.query))
    merged = {**existing, **params}

    new_query = urlencode(merged, doseq=True)

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )


# =========================================================
# URL NORMALIZATION
# =========================================================

def normalize_url(url: str) -> str:
    """
    Normalize URL (remove trailing slash inconsistencies).
    """
    return url.rstrip("/")


def is_valid_url(url: str) -> bool:
    """
    Lightweight URL validation (fast path, no regex overhead heavy).
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False