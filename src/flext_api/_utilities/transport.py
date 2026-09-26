"""HTTP transport runtime primitives owned by flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

import httpx

from .. import t


class FlextApiUtilitiesTransport:
    """Transport utility namespace shard for ``u.Api``."""

    class Httpx:
        """Owner facade for the httpx runtime classes consumers route through.

        Consumer projects reach httpx through ``u.Api.Httpx`` so no consumer
        module imports httpx directly (transport ownership stays with
        flext-api). Members are the real class objects typed as
        ``ClassVar[type[...]]`` so construction, ``raise``, ``isinstance`` and
        ``except`` keep their runtime and static meaning; annotations use the
        matching ``t.Api.Httpx`` aliases.
        """

        Client: ClassVar[type[httpx.Client]] = httpx.Client
        AsyncClient: ClassVar[type[httpx.AsyncClient]] = httpx.AsyncClient
        Response: ClassVar[type[httpx.Response]] = httpx.Response
        HTTPError: ClassVar[type[httpx.HTTPError]] = httpx.HTTPError
        HTTPStatusError: ClassVar[type[httpx.HTTPStatusError]] = httpx.HTTPStatusError
        RequestError: ClassVar[type[httpx.RequestError]] = httpx.RequestError
        TimeoutException: ClassVar[type[httpx.TimeoutException]] = (
            httpx.TimeoutException
        )


__all__: t.MutableSequenceOf[str] = ["FlextApiUtilitiesTransport"]
