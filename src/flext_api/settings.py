"""Generic HTTP Configuration - Pure Pydantic v2.

Minimal HTTP configuration using Pydantic v2 with flext-core constants.
100% GENERIC - no domain coupling. Single responsibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping


def _validate_headers(v: Mapping[str, str]) -> Mapping[str, str]:
    """Validate headers - keys must be non-empty, values must be non-empty."""
    for key, value in v.items():
        key_stripped = key.strip()
        if not key_stripped:
            msg = f"Invalid header key: '{key}'"
            raise ValueError(msg)
        if not value:
            msg = f"Invalid header value for '{key}': '{value}'"
            raise ValueError(msg)
    return v


__all__ = ["FlextApiSettings"]
