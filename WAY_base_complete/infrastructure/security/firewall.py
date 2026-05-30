from __future__ import annotations

import ipaddress
import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


class Firewall:
    """
    WAY infrastructure firewall.

    Features:
        - trusted proxy aware
        - allowlist
        - blocklist
        - private IP validation
        - suspicious user-agent filtering
    """

    DEFAULT_BLOCKED_AGENTS = {
        "curl",
        "wget",
        "python-requests",
        "scrapy",
        "sqlmap",
        "nikto",
    }

    @classmethod
    def config(cls) -> dict[str, Any]:
        """
        Read firewall config.
        """
        return getattr(
            settings,
            "WAY_FIREWALL",
            {},
        )

    @classmethod
    def extract_ip(
        cls,
        request: Any,
    ) -> str | None:
        """
        Resolve client IP.
        """
        forwarded = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if forwarded:
            return (
                forwarded.split(",")[0]
                .strip()
            )

        return request.META.get(
            "REMOTE_ADDR"
        )

    @classmethod
    def is_valid_ip(
        cls,
        ip: str | None,
    ) -> bool:
        """
        Validate IP.
        """
        if not ip:
            return False

        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @classmethod
    def is_private(
        cls,
        ip: str | None,
    ) -> bool:
        """
        Detect private IP.
        """
        if not cls.is_valid_ip(ip):
            return False

        return ipaddress.ip_address(
            ip
        ).is_private

    @classmethod
    def is_blocked_ip(
        cls,
        ip: str | None,
    ) -> bool:
        """
        Check blocklist.
        """
        if not ip:
            return True

        blocked = set(
            cls.config().get(
                "BLOCKED_IPS",
                [],
            )
        )

        return ip in blocked

    @classmethod
    def is_allowed_ip(
        cls,
        ip: str | None,
    ) -> bool:
        """
        Check allowlist.
        """
        allowed = set(
            cls.config().get(
                "ALLOWED_IPS",
                [],
            )
        )

        if not allowed:
            return True

        return ip in allowed

    @classmethod
    def user_agent(
        cls,
        request: Any,
    ) -> str:
        """
        Extract user-agent.
        """
        return (
            request.META.get(
                "HTTP_USER_AGENT",
                "",
            )
            .strip()
            .lower()
        )

    @classmethod
    def is_blocked_agent(
        cls,
        request: Any,
    ) -> bool:
        """
        Detect blocked clients.
        """
        user_agent = cls.user_agent(
            request
        )

        blocked = (
            cls.DEFAULT_BLOCKED_AGENTS
            | set(
                cls.config().get(
                    "BLOCKED_AGENTS",
                    [],
                )
            )
        )

        return any(
            item in user_agent
            for item in blocked
        )

    @classmethod
    def allowed(
        cls,
        request: Any,
    ) -> bool:
        """
        Main firewall decision.
        """
        ip = cls.extract_ip(
            request
        )

        if not cls.is_valid_ip(ip):
            logger.warning(
                "Firewall rejected invalid IP",
                extra={
                    "ip": ip,
                },
            )
            return False

        if cls.is_blocked_ip(ip):
            logger.warning(
                "Firewall blocked IP",
                extra={
                    "ip": ip,
                },
            )
            return False

        if not cls.is_allowed_ip(ip):
            logger.warning(
                "Firewall denied non-allowed IP",
                extra={
                    "ip": ip,
                },
            )
            return False

        if cls.is_blocked_agent(
            request
        ):
            logger.warning(
                "Firewall blocked agent",
                extra={
                    "ip": ip,
                    "agent": cls.user_agent(
                        request
                    ),
                },
            )
            return False

        return True

    @classmethod
    def summary(
        cls,
        request: Any,
    ) -> dict[str, Any]:
        """
        Debug payload.
        """
        ip = cls.extract_ip(
            request
        )

        return {
            "ip": ip,
            "private": cls.is_private(
                ip
            ),
            "allowed": cls.allowed(
                request
            ),
            "user_agent": cls.user_agent(
                request
            ),
        }