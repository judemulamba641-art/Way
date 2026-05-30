from __future__ import annotations

import os

ENV = os.getenv("DJANGO_ENV", "dev")


if ENV == "prod":
    from .prod import *
else:
    from .dev import *