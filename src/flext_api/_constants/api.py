"""API constants namespace combiner."""

from __future__ import annotations

from flext_api._constants.api_values import FlextApiConstantsValues


class FlextApiConstantsApi(FlextApiConstantsValues):
    """Canonical ``c.Api`` constants namespace."""


__all__: list[str] = ["FlextApiConstantsApi"]
