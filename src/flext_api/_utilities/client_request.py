"""HTTP client request execution helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from flext_api import c, m, p, t
from flext_api._utilities.client_codec import FlextApiClientCodecMixin
from flext_core.result import r
from flext_web import u

if TYPE_CHECKING:
    from flext_api.settings import FlextApiSettings


class FlextApiClientRequestMixin(FlextApiClientCodecMixin):
    """Request execution helpers for FlextApiClient."""

    if TYPE_CHECKING:

        @property
        def settings(self) -> FlextApiSettings:
            """Settings contract supplied by FlextApiServiceBase at runtime."""
            ...

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        """Execute HTTP request from model using monadic patterns."""
        url_result = self._build_url(request.url)
        if url_result.failure:
            return r[m.Api.HttpResponse].fail(
                url_result.error or "URL validation failed",
            )
        request_body: t.Api.RequestBody = (
            request.body if request.body is not None else b""
        )
        body_result = self._serialize_body(request_body)
        if body_result.failure:
            return r[m.Api.HttpResponse].fail(
                body_result.error or "Body serialization failed",
            )
        return self._execute_http_request(
            request=request,
            url=url_result.value,
            serialized_body=body_result.value,
        )

    def _build_url(self, path: str) -> p.Result[str]:
        """Build full URL from base_url and path."""
        if not path:
            return r[str].fail("URL path cannot be empty")
        path_stripped = path.strip()
        if not path_stripped:
            return r[str].fail("URL path cannot be empty")
        if not self.settings.base_url.strip():
            return r[str].ok(path_stripped)
        base = self.settings.base_url.strip().rstrip("/")
        if path_stripped.startswith("/"):
            return r[str].ok(f"{base}{path_stripped}")
        return r[str].ok(f"{base}/{path_stripped}")

    def _execute_http_request(
        self,
        request: m.Api.HttpRequest,
        url: str,
        serialized_body: bytes,
    ) -> p.Result[m.Api.HttpResponse]:
        """Execute HTTP request using httpx client."""
        try:
            headers: t.StrMapping = {
                **self.settings.default_headers,
                **request.headers,
            }
            with httpx.Client(timeout=request.timeout) as client:
                response = client.request(
                    method=str(request.method),
                    url=url,
                    headers=headers,
                    params=request.query_params or {},
                    content=serialized_body or None,
                )
            if response.status_code >= c.Api.HTTP_ERROR_MIN:
                return r[m.Api.HttpResponse].fail(
                    f"HTTP {response.status_code}: {response.reason_phrase}",
                )
            return self._deserialize_body(response).flat_map(
                lambda body: u.try_(
                    lambda: m.Api.HttpResponse.model_validate({
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "body": body,
                        "request_id": "",
                    }),
                    catch=(c.ValidationError, ValueError, TypeError),
                ).map_error(lambda exc: f"Response model validation failed: {exc}"),
            )
        except c.Api.EXC_HTTPX as exc:
            return r[m.Api.HttpResponse].fail_op("HTTP client request", exc)


__all__: t.MutableSequenceOf[str] = ["FlextApiClientRequestMixin"]
