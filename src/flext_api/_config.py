"""FlextApiConfig — frozen config singleton for flext-api (ADR-005 §7).

Model-less: business rules live in ``config/*.yaml`` under the ``Api:`` key and
are exposed through the open ``config.Api`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.Api.<domain>[<key>...]``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from flext_core import FlextConfig, FlextSettings

from . import m


class _ApiNamespace(m.BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = m.ConfigDict(extra="allow", frozen=True)


class FlextApiConfig(FlextSettings, FlextConfig):
    """Api config auto-loaded model-less from ``config/*.yaml``.

    MRO carries ``FlextSettings`` FIRST (ENFORCE-042); unlike never-instantiated
    namespace holders, this class IS instantiated by ``fetch_global``, so the
    instance-inert holder contract does not apply and pydantic settings
    construction machinery stays intact.
    """

    Api: Annotated[
        _ApiNamespace,
        m.Field(description="Open namespace exposing ``config/*.yaml`` under ``Api``."),
    ] = _ApiNamespace()


config: FlextApiConfig = FlextApiConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_api import config``."""

__all__: list[str] = ["FlextApiConfig", "config"]
