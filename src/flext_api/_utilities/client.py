"""Generic HTTP client facade."""

from __future__ import annotations

from typing import override

from flext_api import p, r, s, t
from flext_api._utilities.client_request import FlextApiClientRequestMixin


class FlextApiClient(FlextApiClientRequestMixin, s[bool]):
    """Generic HTTP client using FLEXT patterns."""

    @override
    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute service lifecycle parity."""
        if kwargs:
            self.logger.info(f"Execute called with kwargs keys: {list(kwargs.keys())}")
        return r[bool].ok(True)


__all__: t.MutableSequenceOf[str] = ["FlextApiClient"]
