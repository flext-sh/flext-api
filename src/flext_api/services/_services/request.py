"""HTTP client request execution helpers."""

from __future__ import annotations

import httpx

from ... import c, m, p, r, t
from .base_request import FlextApiClientBaseRequestMixin


class FlextApiClientRequestMixin(FlextApiClientBaseRequestMixin):
    """Request execution helpers for FlextApiClient."""

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        """Execute HTTP request from model using monadic patterns."""
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
