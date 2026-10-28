"""Shared service foundation for flext-api components.

Provides typed access to the registered ``api`` settings namespace while
preserving flext-web service runtime behavior.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import override

from flext_core import FlextService

from flext_api import FlextApiSettings, m


class FlextApiServiceBase[TDomainResult](
    FlextService[TDomainResult],
):
    """Base class for flext-api services with typed API settings access."""

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

__all__: MutableSequence[str] = ["FlextApiServiceBase", "s"]
