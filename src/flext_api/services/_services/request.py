"""HTTP client request execution helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx
from flext_web import r

from flext_api._typings.types import t
from flext_api.constants import c
from flext_api.models import m
from flext_api.protocols import p
from flext_api.services._services.base_request import FlextApiClientBaseRequestMixin


class FlextApiClientRequestMixin(FlextApiClientBaseRequestMixin):
    """Request execution helpers for FlextApiClient."""

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        """Execute HTTP request from model using monadic patterns.

        Returns:
            The resulting ``p.Result[m.Api.HttpResponse]``.
        """
        prep = self._prepare_request(request)
        if prep.failure:
            return r[m.Api.HttpResponse].from_failure(prep)
        url, headers, body, extensions = prep.value
        client = httpx.Client(timeout=request.timeout)
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
        except c.Api.EXC_HTTPX as exc:
            return self._handle_transport_error(exc, "HTTP client request")
        finally:
            client.close()


__all__: t.MutableSequenceOf[str] = ["FlextApiClientRequestMixin"]
