from __future__ import annotations

from typing import Any, Dict, List, Union, Optional, TypeAlias


# =========================================================
# CORE JSON TYPES
# =========================================================

JSONPrimitive: TypeAlias = Union[str, int, float, bool, None]

JSONObject: TypeAlias = Dict[str, Any]

JSONArray: TypeAlias = List[Any]

JSONValue: TypeAlias = Union[
    JSONPrimitive,
    JSONObject,
    JSONArray,
]


# =========================================================
# SDK CORE TYPES
# =========================================================

Headers: TypeAlias = Dict[str, str]
QueryParams: TypeAlias = Dict[str, Any]

Payload: TypeAlias = Dict[str, Any]

ResponseType: TypeAlias = Any


# =========================================================
# OPTIONAL HELPERS
# =========================================================

Maybe: TypeAlias = Optional[Any]