"""Generic HTTP client facade."""

from __future__ import annotations

from typing import override

from flext_api import FlextApiSettings, p, r, s, t
from flext_api._utilities.client_request import FlextApiClientRequestMixin


class FlextApiClient(FlextApiClientRequestMixin, s[bool]):
    """Generic HTTP client using FLEXT patterns."""

    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        """Bind the client to explicit settings or the global singleton."""
        resolved = settings if settings is not None else FlextApiSettings.fetch_global()
        super().__init__(runtime_settings=resolved)

    @property
    def base_url(self) -> str:
        """The configured API base URL."""
        return self.settings.Api.base_url

    @property
    def timeout(self) -> float:
        """The configured request timeout in seconds."""
        return self.settings.Api.timeout

    @override
    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute service lifecycle parity."""
        if kwargs:
            self.logger.info(f"Execute called with kwargs keys: {list(kwargs.keys())}")
        return r[bool].ok(True)


__all__: t.MutableSequenceOf[str] = ["FlextApiClient"]
