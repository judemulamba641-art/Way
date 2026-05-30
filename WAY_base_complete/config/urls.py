from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse


# ---------------------------------------------------------
# Healthcheck (important for Docker / Kubernetes / Nginx)
# ---------------------------------------------------------
def healthcheck(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "way",
        }
    )


# ---------------------------------------------------------
# API root (future gateway entrypoint)
# ---------------------------------------------------------
def api_root(request):
    return JsonResponse(
        {
            "service": "WAY API",
            "status": "running",
            "versioning": "/api/v1/",
        }
    )


# ---------------------------------------------------------
# URL Configuration
# ---------------------------------------------------------
urlpatterns = [
    # -----------------------------------------------------
    # Admin
    # -----------------------------------------------------
    path("admin/", admin.site.urls),

    # -----------------------------------------------------
    # Health / monitoring
    # -----------------------------------------------------
    path("health/", healthcheck),
    path("", api_root),

    # -----------------------------------------------------
    # API versioning (core architecture)
    # -----------------------------------------------------
    path(
        "api/v1/",
        include("way.core.api.v1.urls"),
    ),

    # -----------------------------------------------------
    # Future versions (reserved)
    # -----------------------------------------------------
    # path("api/v2/", include("way.core.api.v2.urls")),
]