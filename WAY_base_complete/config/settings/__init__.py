from __future__ import annotations

import os


ENVIRONMENT = os.getenv("DJANGO_ENV", "dev").lower()

if ENVIRONMENT in ("prod", "production"):
    from .prod import *  # noqa
elif ENVIRONMENT in ("test", "testing"):
    from .test import *  # noqa
else:
    from .dev import *  # noqa