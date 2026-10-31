"""Layer-zero configuration schema shared by config and its public model holder.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m


class FlextApiConfigNamespace:
    """Own the configuration namespace without importing project facades."""

    class ConfigNamespace(m.BaseModel):
        """Open, frozen namespace exposing every declared YAML domain."""

        model_config = m.ConfigDict(extra="allow", frozen=True)


__all__: list[str] = ["FlextApiConfigNamespace"]
