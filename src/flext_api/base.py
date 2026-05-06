"""Shared service foundation for flext-api components.

Provides typed access to the registered ``api`` settings namespace while
preserving flext-web service runtime behavior.
"""

from __future__ import annotations

from abc import ABC
from typing import Annotated, override

from flext_api import FlextApiSettings, p, t
from flext_core import s
from flext_web import u


class FlextApiServiceBase[
    TDomainResult: t.JsonPayload | t.SequenceOf[t.JsonPayload],
](s[TDomainResult], ABC):
    """Base class for flext-api services with typed API settings access."""

    settings_type: Annotated[
        type | None,
        u.Field(description="Settings class for API service initialization"),
    ] = FlextApiSettings

    def __init__(
        self,
        *,
        settings_type: type | None = None,
        runtime_settings: p.Settings | None = None,
        settings_overrides: t.JsonMapping | None = None,
        initial_context: p.Context | None = None,
    ) -> None:
        """Bootstrap API services with one concrete runtime settings contract."""
        super().__init__(
            settings_type=settings_type,
            runtime_settings=runtime_settings,
            settings_overrides=settings_overrides,
            initial_context=initial_context,
        )

    @property
    @override
    def settings(self) -> FlextApiSettings:
        """Return the typed API settings bound to this service runtime."""
        settings = self.runtime_settings
        if settings is not None:
            return FlextApiSettings.model_validate(settings)
        return FlextApiSettings.fetch_global()


s = FlextApiServiceBase

__all__: list[str] = ["FlextApiServiceBase", "s"]
