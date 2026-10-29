"""Layer-zero configuration namespace for flext-api.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.config_namespace import FlextApiConfigNamespace


class FlextApiModelsConfig(FlextApiConfigNamespace):
    """Config models for flext-api."""


__all__: list[str] = ["FlextApiModelsConfig"]
