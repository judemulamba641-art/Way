from __future__ import annotations

"""
WAY Infrastructure Layer

This package contains all system-level integrations:
- Cache (Redis / Memory)
- Messaging (Celery / Channels)
- Database utilities
- Storage providers
- Monitoring & observability
- Security helpers

IMPORTANT:
This layer MUST NOT contain business logic.
It is strictly for infrastructure concerns.
"""