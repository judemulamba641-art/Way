from __future__ import annotations

import logging

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .firewall import Firewall
from .rate_limit import RateLimiter

logger = logging.getLogger(__name__)


class FirewallMiddleware(
    MiddlewareMixin
):
    """
    Global firewall protection.

    Runs early before views.
    """

    def process_request(
        self,
        request,
    ):
        allowed = (
            Firewall.allowed(
                request
            )
        )

        if allowed:
            return None

        logger.warning(
            "Firewall denied request",
            extra={
                "path": request.path,
                "method": request.method,
                "ip": (
                    Firewall.extract_ip(
                        request
                    )
                ),
            },
        )

        return JsonResponse(
            {
                "detail": (
                    "Access denied."
                ),
                "code": (
                    "firewall_blocked"
                ),
            },
            status=403,
        )


class RateLimitMiddleware(
    MiddlewareMixin
):
    """
    Global request throttling.
    """

    def process_request(
        self,
        request,
    ):
        allowed = (
            RateLimiter.allowed(
                request
            )
        )

        if allowed:
            return None

        logger.warning(
            "Rate limit exceeded",
            extra={
                "path": request.path,
                "method": request.method,
                "ip": (
                    Firewall.extract_ip(
                        request
                    )
                ),
            },
        )

        return JsonResponse(
            {
                "detail": (
                    "Too many requests."
                ),
                "code": (
                    "rate_limited"
                ),
            },
            status=429,
        )


class SecurityHeadersMiddleware(
    MiddlewareMixin
):
    """
    Adds secure headers.
    """

    def process_response(
        self,
        request,
        response,
    ):
        response[
            "X-Frame-Options"
        ] = "DENY"

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        response[
            "Referrer-Policy"
        ] = (
            "same-origin"
        )

        response[
            "Permissions-Policy"
        ] = (
            "geolocation=(), "
            "camera=(), "
            "microphone=()"
        )

        return response