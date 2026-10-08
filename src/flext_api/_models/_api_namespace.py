"""Api namespace module.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_api/_models/_api_namespace
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m


class FlextApiModelsApiNamespace(m.BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = m.ConfigDict(extra="allow", frozen=True)
