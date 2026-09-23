"""Common HTTP client base class shared by sync and async clients."""

from __future__ import annotations

from typing import override

from .. import p, r, s, t, u


class FlextApiClientBase(s[bool]):
    """Base HTTP client using FLEXT patterns."""

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
            u.fetch_logger(__name__).info(
                "Execute called with kwargs keys: %s", list(kwargs.keys())
            )
        return r[bool].ok(True)


__all__: t.MutableSequenceOf[str] = ["FlextApiClientBase"]
