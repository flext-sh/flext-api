"""Generic async HTTP client facade."""

from __future__ import annotations

from .. import t
from ._services import FlextApiClientAsyncRequestMixin
from .base_client import FlextApiClientBase


class FlextApiAsyncClient(FlextApiClientAsyncRequestMixin, FlextApiClientBase):
    """Generic async HTTP client using FLEXT patterns."""


__all__: t.MutableSequenceOf[str] = ["FlextApiAsyncClient"]
