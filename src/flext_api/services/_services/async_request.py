"""HTTP async client request execution helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence

from flext_api import p, u
from flext_api.services._services import FlextApiClientBaseRequest


class FlextApiClientAsyncRequest(FlextApiClientBaseRequest):
    """Async request execution helpers for FlextApiAsyncClient."""

    async def request(self, request: p.Api.HttpRequest) -> p.Result[p.Api.HttpResponse]:
        """Execute an async HTTP request from the request model.

        Args:
            request: Prepared HTTP request model.

        Returns:
            Response payload or error result.

        """
        return await self._execute_request_async(request, self._send)

    @staticmethod
    async def _send(
        request: p.Api.HttpRequest,
        url: str,
        headers: Mapping[str, str],
        body: bytes,
        extensions: Mapping[str, str],
    ) -> p.Api.HttpWireResponse:
        """Send one prepared request through the asynchronous client.

        Returns:
            The raw wire response.

        """
        async with u.Api.HttpxAsyncClient(
            timeout=request.timeout, verify=request.verify_tls
        ) as client:
            return await client.request(
                method=str(request.method),
                url=url,
                headers=headers,
                params=request.query_params,
                content=body,
                extensions=extensions,
            )


__all__: MutableSequence[str] = ["FlextApiClientAsyncRequest"]
