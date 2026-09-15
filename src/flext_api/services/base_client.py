"""Common HTTP client base class shared by sync and async clients."""

from __future__ import annotations

from typing import override

from .. import FlextApiSettings, p, r, s, t, u


class FlextApiClientBase(s[bool]):
    """Base HTTP client using FLEXT patterns."""

    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        """Bind the client to explicit settings or the global singleton."""
        resolved = settings if settings is not None else FlextApiSettings.fetch_global()
        s.__init__(self, runtime_settings=resolved)

    @property
    def client_settings(self) -> FlextApiSettings:
        """The typed API settings bound to this client."""
        current = super().settings
        if isinstance(current, FlextApiSettings):
            return current
        return FlextApiSettings.fetch_global()

    @property
    def base_url(self) -> str:
        """The configured API base URL."""
        return self.client_settings.Api.base_url

    @property
    def timeout(self) -> float:
        """The configured request timeout in seconds."""
        return self.client_settings.Api.timeout

    @override
    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute service lifecycle parity."""
        if kwargs:
            u.fetch_logger(__name__).info(
                "Execute called with kwargs keys: %s", list(kwargs.keys())
            )
        return r[bool].ok(True)


__all__: t.MutableSequenceOf[str] = ["FlextApiClientBase"]
