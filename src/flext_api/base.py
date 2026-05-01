"""Shared service foundation for flext-api components.

Provides typed access to the registered ``api`` settings namespace while
preserving flext-web service runtime behavior.
"""

from __future__ import annotations

from abc import ABC
from typing import Annotated, override

from flext_api import t
from flext_api.settings import FlextApiSettings
from flext_core import FlextSettings, s
from flext_web import u


class FlextApiServiceBase[
    TDomainResult: t.JsonPayload | t.SequenceOf[t.JsonPayload],
](s[TDomainResult], ABC):
    """Base class for flext-api services with typed API settings access."""

    settings_type: Annotated[
        type | None,
        u.Field(description="Settings class for API service initialization"),
    ] = FlextApiSettings

    @property
    @override
    def settings(self) -> FlextApiSettings:
        """Return the typed API settings bound to this service runtime."""
        settings = self.runtime_settings
        if settings is not None:
            return FlextApiSettings.model_validate(settings)
        return FlextSettings.fetch_global().fetch_namespace("api", FlextApiSettings)


s = FlextApiServiceBase

__all__: list[str] = ["FlextApiServiceBase", "s"]
