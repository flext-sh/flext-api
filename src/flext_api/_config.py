"""FlextApiConfig — frozen config singleton for flext-api (ADR-005 §7).

Model-less: business rules live in ``config/*.yaml`` under the ``Api:`` key and
are exposed through the open ``config.Api`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.Api.<domain>[<key>...]``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from flext_core import FlextConfig


class _ApiNamespace(BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = ConfigDict(extra="allow", frozen=True)


class FlextApiConfig(FlextConfig):
    """Api config auto-loaded model-less from ``config/*.yaml``."""

    Api: _ApiNamespace = _ApiNamespace()


config: FlextApiConfig = FlextApiConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_api import config``."""

__all__: list[str] = ["FlextApiConfig", "config"]
