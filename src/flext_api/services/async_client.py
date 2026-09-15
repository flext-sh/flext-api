"""Generic async HTTP client facade."""

from __future__ import annotations

from .. import FlextApiSettings, t
from ._services import FlextApiClientAsyncRequestMixin
from .base_client import FlextApiClientBase


class FlextApiAsyncClient(FlextApiClientBase, FlextApiClientAsyncRequestMixin):
    """Generic async HTTP client using FLEXT patterns."""

    def __init__(self, *, settings: FlextApiSettings | None = None) -> None:
        """Bind one async client to explicit settings or the global singleton."""
        super().__init__(settings=settings)


__all__: t.MutableSequenceOf[str] = ["FlextApiAsyncClient"]
