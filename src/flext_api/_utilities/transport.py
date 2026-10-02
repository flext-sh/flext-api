"""HTTP transport runtime primitives owned by flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import httpx

if TYPE_CHECKING:
    from flext_api import t


class FlextApiUtilitiesTransport:
    """Transport utility namespace shard for ``u.Api``.

    Owner facade for the httpx runtime classes consumers route through.
    Consumer projects reach httpx through the ``u.Api.Httpx*`` members so no
    consumer module imports httpx directly (transport ownership stays with
    flext-api). Members are the real class objects typed as
    ``ClassVar[type[...]]`` so construction, ``raise``, ``isinstance`` and
    ``except`` keep their runtime and static meaning; annotations use the
    matching ``t.Api.Httpx*`` aliases.
    """

    HttpxClient: ClassVar[type[httpx.Client]] = httpx.Client
    HttpxAsyncClient: ClassVar[type[httpx.AsyncClient]] = httpx.AsyncClient
    HttpxResponse: ClassVar[type[httpx.Response]] = httpx.Response
    HttpxHTTPError: ClassVar[type[httpx.HTTPError]] = httpx.HTTPError
    HttpxHTTPStatusError: ClassVar[type[httpx.HTTPStatusError]] = httpx.HTTPStatusError
    HttpxRequestError: ClassVar[type[httpx.RequestError]] = httpx.RequestError
    HttpxTimeoutException: ClassVar[type[httpx.TimeoutException]] = (
        httpx.TimeoutException
    )


__all__: t.MutableSequenceOf[str] = ["FlextApiUtilitiesTransport"]
