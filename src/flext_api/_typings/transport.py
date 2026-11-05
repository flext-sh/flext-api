"""HTTP transport annotation types owned by flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import c


class FlextApiTypingsTransport:
    """Transport typing namespace shard for ``t.Api``.

    Transport annotations belong to ``p.Api``. HTTPX identity stays private to
    ``u.Api``.
    """

    type WebhookDeliveryStatus = c.Api.WebhookDeliveryStatus | str
    type WebhookAlgorithm = c.Api.WebhookAlgorithm | str


__all__: list[str] = ["FlextApiTypingsTransport"]
