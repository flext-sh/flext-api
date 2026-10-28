"""HTTP transport annotation types owned by flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx

from flext_api import c


class FlextApiTypingsTransport:
    """Transport typing namespace shard for ``t.Api``.

    Annotation aliases for the httpx runtime classes in ``u.Api.Httpx*``.
    """

    type HttpxClient = httpx.Client
    type HttpxAsyncClient = httpx.AsyncClient
    type HttpxResponse = httpx.Response
    type WebhookDeliveryStatus = c.Api.WebhookDeliveryStatus | str
    type WebhookAlgorithm = c.Api.WebhookAlgorithm | str


__all__: list[str] = ["FlextApiTypingsTransport"]
