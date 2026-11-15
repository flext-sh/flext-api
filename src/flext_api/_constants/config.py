"""API config constants — stand-in for facade MRO composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api._constants.config_values import FlextApiConfig


class FlextApiConstantsConfig(FlextApiConfig):
    """SSOT for API-specific config loading defaults via stand-in composition."""

    pass


__all__: list[str] = ["FlextApiConstantsConfig"]
