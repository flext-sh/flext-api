"""HTTP client request execution helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence

from flext_api import p, r, u
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
        prep = self._prepare_request(request)
        if prep.failure:
            return r[p.Api.HttpResponse].from_failure(prep)
        url, headers, body, extensions = prep.value
        client = u.Api.HttpxClient(timeout=request.timeout)
        try:
            response = client.request(
                method=str(request.method),
                url=url,
                headers=headers,
                params=request.query_params or {},
                content=body,
                extensions=extensions,
            )
            return self._handle_response(response)
        except u.Api.EXC_HTTPX as exc:
            return self._handle_transport_error(exc, "HTTP client request")
        finally:
            client.close()


__all__: MutableSequence[str] = ["FlextApiClientRequest"]
