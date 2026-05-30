from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
DEFAULT_RATE_LIMIT = {
    "WINDOW_SECONDS": 60,
    "MAX_REQUESTS": 120,
    "BLOCK_SECONDS": 300,
    "WHITELIST_IPS": [],
    "PATH_RULES": {},
}


# ---------------------------------------------------------
# RULE MODEL
# ---------------------------------------------------------
@dataclass(slots=True)
class RateLimitRule:
    window_seconds: int
    max_requests: int
    block_seconds: int

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RateLimitRule":
        return cls(
            window_seconds=int(
                data["WINDOW_SECONDS"]
            ),
            max_requests=int(
                data["MAX_REQUESTS"]
            ),
            block_seconds=int(
                data["BLOCK_SECONDS"]
            ),
        )


# ---------------------------------------------------------
# LOAD CONFIG
# ---------------------------------------------------------
def get_config() -> dict[str, Any]:
    config = getattr(
        settings,
        "WAY_RATE_LIMIT",
        {},
    )

    merged = DEFAULT_RATE_LIMIT.copy()
    merged.update(config)

    return merged


# ---------------------------------------------------------
# REQUEST IP
# ---------------------------------------------------------
def get_client_ip(
    request: HttpRequest,
) -> str:
    forwarded = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if forwarded:
        return (
            forwarded.split(",")[0]
            .strip()
        )

    return request.META.get(
        "REMOTE_ADDR",
        "unknown",
    )


# ---------------------------------------------------------
# CACHE KEYS
# ---------------------------------------------------------
def request_key(
    ip: str,
    path: str,
) -> str:
    return (
        "way:rate:"
        f"{ip}:{path}"
    )


def blocked_key(
    ip: str,
) -> str:
    return (
        "way:block:"
        f"{ip}"
    )


# ---------------------------------------------------------
# RULE RESOLUTION
# ---------------------------------------------------------
def resolve_rule(
    path: str,
) -> RateLimitRule:
    config = get_config()

    path_rules = config.get(
        "PATH_RULES",
        {},
    )

    for prefix, rule in (
        path_rules.items()
    ):
        if path.startswith(
            prefix
        ):
            return (
                RateLimitRule
                .from_dict(rule)
            )

    return RateLimitRule(
        window_seconds=int(
            config[
                "WINDOW_SECONDS"
            ]
        ),
        max_requests=int(
            config[
                "MAX_REQUESTS"
            ]
        ),
        block_seconds=int(
            config[
                "BLOCK_SECONDS"
            ]
        ),
    )


# ---------------------------------------------------------
# BLOCK CHECK
# ---------------------------------------------------------
def is_blocked(
    ip: str,
) -> bool:
    return bool(
        cache.get(
            blocked_key(ip)
        )
    )


def block_ip(
    ip: str,
    seconds: int,
) -> None:
    cache.set(
        blocked_key(ip),
        True,
        timeout=seconds,
    )


# ---------------------------------------------------------
# WHITELIST
# ---------------------------------------------------------
def is_whitelisted(
    ip: str,
) -> bool:
    config = get_config()

    whitelist = (
        config.get(
            "WHITELIST_IPS",
            [],
        )
        or []
    )

    return ip in whitelist


# ---------------------------------------------------------
# COUNTER
# ---------------------------------------------------------
def increment_request(
    ip: str,
    path: str,
    window: int,
) -> int:
    key = request_key(
        ip,
        path,
    )

    current = cache.get(key)

    if current is None:
        cache.set(
            key,
            1,
            timeout=window,
        )
        return 1

    try:
        cache.incr(key)
        value = cache.get(key)

        return int(
            value or 0
        )

    except ValueError:
        cache.set(
            key,
            1,
            timeout=window,
        )
        return 1


# ---------------------------------------------------------
# MAIN CHECK
# ---------------------------------------------------------
def check_rate_limit(
    request: HttpRequest,
) -> tuple[bool, str | None]:
    ip = get_client_ip(
        request
    )

    if is_whitelisted(ip):
        return (
            True,
            None,
        )

    if is_blocked(ip):
        return (
            False,
            "temporarily blocked",
        )

    rule = resolve_rule(
        request.path
    )

    count = increment_request(
        ip=ip,
        path=request.path,
        window=rule.window_seconds,
    )

    if count > rule.max_requests:
        block_ip(
            ip,
            rule.block_seconds,
        )

        return (
            False,
            (
                "rate limit exceeded"
            ),
        )

    return (
        True,
        None,
    )


# ---------------------------------------------------------
# OPTIONAL METRICS
# ---------------------------------------------------------
def get_rate_limit_snapshot(
    request: HttpRequest,
) -> dict[str, Any]:
    ip = get_client_ip(
        request
    )

    rule = resolve_rule(
        request.path
    )

    count = cache.get(
        request_key(
            ip,
            request.path,
        )
    ) or 0

    return {
        "ip": ip,
        "path": request.path,
        "count": count,
        "window": (
            rule.window_seconds
        ),
        "max_requests": (
            rule.max_requests
        ),
        "blocked": is_blocked(
            ip
        ),
        "timestamp": int(
            time.time()
        ),
    }