"""HTTP async client request execution helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx

from flext_api import m, p, r, t
from flext_api.services._services.base_request import FlextApiClientBaseRequestMixin


class FlextApiClientAsyncRequestMixin(FlextApiClientBaseRequestMixin):
    """Async request execution helpers for FlextApiAsyncClient."""

    async def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        """Execute async HTTP request from model using monadic patterns.

        Returns:
            The resulting ``p.Result[m.Api.HttpResponse]``.
        """
        prep = self._prepare_request(request)
        if prep.failure:
            return r[m.Api.HttpResponse].from_failure(prep)
        url, headers, body, extensions = prep.value
        async with httpx.AsyncClient(timeout=request.timeout) as client:
            response = await client.request(
                method=str(request.method),
                url=url,
                headers=headers,
                params=request.query_params or {},
                content=body,
                extensions=extensions,
            )
        return self._handle_response(response)


__all__: t.MutableSequenceOf[str] = ["FlextApiClientAsyncRequestMixin"]
