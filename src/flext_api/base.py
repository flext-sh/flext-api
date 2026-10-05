"""Shared service foundation for flext-api components.

Provides typed access to the registered ``api`` settings namespace while
preserving flext-web service runtime behavior.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC
from typing import override

from flext_api import FlextApiSettings, m, p, t
from flext_core import FlextService


class FlextApiServiceBase[TDomainResult: t.JsonPayload | t.SequenceOf[t.JsonPayload]](
    FlextService[TDomainResult],
    ABC,
):
    """Base class for flext-api services with typed API settings access."""

    def __init__(
        self,
        *,
        settings_type: type | None = None,
        runtime_settings: p.Settings | None = None,
        settings_overrides: t.ScalarMapping | None = None,
        initial_context: p.Context | None = None,
    ) -> None:
        """Bootstrap API services with one concrete runtime settings contract."""
        super().__init__(
            settings_type=settings_type or FlextApiSettings,
            runtime_settings=runtime_settings,
            settings_overrides=settings_overrides,
            initial_context=initial_context,
        )

    @property
    @override
    def settings(self) -> FlextApiSettings:
        """The typed API settings bound to this service runtime.

        Raises:
            TypeError: If ``not isinstance(current, FlextApiSettings)``.
        """
        current = super().settings
        if not isinstance(current, FlextApiSettings):
            msg = (
                f"{type(self).__name__} runtime settings must be FlextApiSettings, "
                f"got {type(current).__name__}"
            )
            raise TypeError(msg)
        return current

    @classmethod
    def runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        """Return runtime bootstrap options for API services."""
        return m.RuntimeBootstrapOptions(settings_type=FlextApiSettings)


s = FlextApiServiceBase

__all__: t.MutableSequenceOf[str] = ["FlextApiServiceBase", "s"]
