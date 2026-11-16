"""HTTP client request execution helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence

from flext_api import p, u
from flext_api.services._services import FlextApiClientBaseRequest


class FlextApiClientRequest(FlextApiClientBaseRequest):
    """Request execution helpers for FlextApiClient."""

    def request(self, request: p.Api.HttpRequest) -> p.Result[p.Api.HttpResponse]:
        """Execute an HTTP request from the request model using monadic patterns.

        Args:
            request: Prepared HTTP request model.

        Returns:
            Response payload or error result.

        """
        return self._execute_request(request, self._send)

    @staticmethod
    def _send(
        request: p.Api.HttpRequest,
        url: str,
        headers: Mapping[str, str],
        body: bytes,
        extensions: Mapping[str, str],
    ) -> p.Api.HttpWireResponse:
        """Send one prepared request through the synchronous client.

        Returns:
            The raw wire response.

        """
        with u.Api.HttpxClient(timeout=request.timeout) as client:
            return client.request(
                method=str(request.method),
                url=url,
                headers=headers,
                params=request.query_params or {},
                content=body,
                extensions=extensions,
            )


__all__: MutableSequence[str] = ["FlextApiClientRequest"]
