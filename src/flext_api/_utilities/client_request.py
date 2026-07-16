"""HTTP client request execution helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from flext_api import c, p, t
from flext_api._utilities.client_codec import FlextApiClientCodecMixin
from flext_core.result import r
from flext_web import u

if TYPE_CHECKING:
    from flext_api import FlextApiSettings


class FlextApiClientRequestMixin(FlextApiClientCodecMixin):
    """Request execution helpers for FlextApiClient."""

    settings: FlextApiSettings

    def request(self, request: p.Api.HttpRequest) -> p.Result[p.Api.HttpResponse]:
        """Execute HTTP request from model using monadic patterns."""
        url_result = self._build_url(request.url)
        if url_result.failure:
            return r[p.Api.HttpResponse].fail(
                url_result.error or "URL validation failed"
            )
        request_body: t.Api.RequestBody = (
            request.body if request.body is not None else b""
        )
        body_result = self._serialize_body(request_body)
        if body_result.failure:
            return r[p.Api.HttpResponse].fail(
                body_result.error or "Body serialization failed"
            )
        return self._execute_http_request(
            request=request, url=url_result.value, serialized_body=body_result.value
        )

    def _build_url(self, path: str) -> p.Result[str]:
        """Build full URL from base_url and path."""
        # NOTE (multi-agent): mro-t9s9 — request defaults belong to this
        # client's injected runtime settings, never the global singleton.
        api_settings = self.settings.Api
        if not path:
            return r[str].fail("URL path cannot be empty")
        path_stripped = path.strip()
        if not path_stripped:
            return r[str].fail("URL path cannot be empty")
        if not api_settings.base_url.strip():
            return r[str].ok(path_stripped)
        base = api_settings.base_url.strip().rstrip("/")
        if path_stripped.startswith("/"):
            return r[str].ok(f"{base}{path_stripped}")
        return r[str].ok(f"{base}/{path_stripped}")

    def _execute_http_request(
        self, request: p.Api.HttpRequest, url: str, serialized_body: bytes
    ) -> p.Result[p.Api.HttpResponse]:
        """Execute HTTP request using httpx client."""
        try:
            headers: t.StrMapping = {
                **self.settings.Api.default_headers,
                **request.headers,
            }
            extensions = (
                {"sni_hostname": request.sni_hostname} if request.sni_hostname else {}
            )
            with httpx.Client(timeout=request.timeout) as client:
                response = client.request(
                    method=str(request.method),
                    url=url,
                    headers=headers,
                    params=request.query_params or {},
                    content=serialized_body or None,
                    extensions=extensions,
                )
            # Any HTTP status (incl. 4xx/5xx) is a successful transport round-trip;
            # HttpResponse classifies it (success/client_error/server_error). Only a
            # transport failure (connection/TLS/timeout/DNS) becomes r.fail below.
            return self._deserialize_body(response).flat_map(
                lambda body: u.try_(
                    lambda: p.Api.HttpResponse(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        body=body,
                        request_id="",
                    ),
                    catch=(c.ValidationError, ValueError, TypeError),
                ).map_error(lambda exc: f"Response model validation failed: {exc}")
            )
        except c.Api.EXC_HTTPX as exc:
            return r[p.Api.HttpResponse].fail_op("HTTP client request", exc)


__all__: t.MutableSequenceOf[str] = ["FlextApiClientRequestMixin"]
