# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_api/_protocols/request
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

if TYPE_CHECKING:
    from flext_api import c, t


class FlextApiProtocolsRequest:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class HttpRequest(FlextCliProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def method(self) -> c.Api.Method | str:
            """HTTP method."""
            ...

        @property
        def url(self) -> t.NonEmptyStr:
            """Request URL."""
            ...

        @property
        def headers(self) -> Mapping[str, str]:
            """HTTP request headers."""
            ...

        @property
        def body(self) -> t.Api.RequestBody | None:
            """Request body."""
            ...

        @property
        def query_params(self) -> t.Api.WebParams | None:
            """Query parameters."""
            ...

        @property
        def timeout(self) -> t.PositiveTimeout:
            """Request timeout in seconds."""
            ...

        @property
        def sni_hostname(self) -> str | None:
            """Structural member projected from the owning model.

            TLS SNI / certificate hostname to verify when the URL targets an
            explicit IP (httpx sni_hostname extension).
            """
            ...


__all__: list[str] = [
    "FlextApiProtocolsRequest",
]
