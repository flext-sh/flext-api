from __future__ import annotations
from flext_api import m
from flext_api._config import FlextApiConfig, config, __all__


class _ApiNamespace(m.BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = m.ConfigDict(extra="allow", frozen=True)
