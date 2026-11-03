# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_api/_protocols/response
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocols

from flext_api import t

if TYPE_CHECKING:
    from flext_api._typings import FlextApiTypingsBase


class FlextApiProtocolsResponse:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class HttpResponse(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def status_code(self) -> t.HttpStatusCode:
            """Structural member projected from the owning model."""
            ...

        @property
        def headers(self) -> Mapping[str, str]:
            """HTTP response headers."""
            ...

        @property
        def body(self) -> FlextApiTypingsBase.ResponseBody | None:
            """Response body."""
            ...

        @property
        def content(self) -> bytes:
            """Exact response body bytes received on the wire."""
            ...

        @property
        def request_id(self) -> str:
            """Associated request ID for tracking."""
            ...


__all__: list[str] = [
    "FlextApiProtocolsResponse",
]
