"""HTTP transport annotation types owned by flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx


class FlextApiTypingsTransport:
    """Transport typing namespace shard for ``t.Api``."""

    class Httpx:
        """Annotation aliases for the httpx runtime classes in ``u.Api.Httpx``."""

        type Client = httpx.Client
        type AsyncClient = httpx.AsyncClient
        type Response = httpx.Response


__all__: list[str] = ["FlextApiTypingsTransport"]
