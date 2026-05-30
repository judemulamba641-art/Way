#!/usr/bin/env python
"""
WAY manage.py

Entrée principale Django pour l'environnement développement.

- settings dev par défaut
- compatible Celery / DRF / commands custom
- messages explicites
- structure enterprise-ready
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def ensure_env_file() -> None:
    env_file = BASE_DIR / ".env"

    if not env_file.exists():
        print(
            "[WAY][WARN] Aucun fichier .env trouvé. "
            "Les variables d’environnement système seront utilisées."
        )


def ensure_virtualenv() -> None:
    if sys.prefix == sys.base_prefix:
        print(
            "[WAY][INFO] Aucun virtualenv détecté "
            "(acceptable en dev si environnement contrôlé)."
        )


def configure_settings() -> None:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "way.settings.dev",
    )

    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


def main() -> None:
    ensure_virtualenv()
    ensure_env_file()
    configure_settings()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django n'est pas installé ou le venv WAY n'est pas activé."
        ) from exc

    print("[WAY] Runtime dev initialisé")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()