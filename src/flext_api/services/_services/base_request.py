"""Common HTTP request execution helpers shared by sync and async clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ... import c, m, p, r, t, u
from . import FlextApiClientCodecMixin

if TYPE_CHECKING:
    from ... import FlextApiSettings


class FlextApiClientBaseRequestMixin(FlextApiClientCodecMixin):
    """Shared request execution helpers for sync and async clients."""

    if TYPE_CHECKING:

        @property
        def client_settings(self) -> FlextApiSettings:
            """Typed settings supplied by the concrete client base."""

    def _build_url(self, path: str) -> p.Result[str]:
        """Build full URL from base_url and path."""
        # NOTE (multi-agent): mro-t9s9 — request defaults belong to this
        # client's injected runtime settings, never the global singleton.
        api_settings = self.client_settings.Api
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

    def _prepare_request(
        self, request: m.Api.HttpRequest
    ) -> p.Result[tuple[str, t.StrMapping, bytes, t.MappingKV[str, str]]]:
        """Prepare URL, headers, body, and extensions for HTTP request."""
        url_result = self._build_url(request.url)
        if url_result.failure:
            return r[
                tuple[str, t.StrMapping, bytes, t.MappingKV[str, str]]
            ].from_failure(url_result)
        request_body: t.Api.RequestBody = (
            request.body if request.body is not None else b""
        )
        body_result = self._serialize_body(request_body)
        if body_result.failure:
            return r[
                tuple[str, t.StrMapping, bytes, t.MappingKV[str, str]]
            ].from_failure(body_result)
        headers: t.StrMapping = {
            **self.client_settings.Api.default_headers,
            **request.headers,
        }
        extensions: t.MutableStrMapping = {}
        if request.sni_hostname:
            extensions["sni_hostname"] = request.sni_hostname
        return r[tuple[str, t.StrMapping, bytes, t.MappingKV[str, str]]].ok((
            url_result.value,
            headers,
            body_result.value,
            extensions,
        ))

    def _handle_response(
        self, response: httpx.Response
    ) -> p.Result[m.Api.HttpResponse]:
        """Process HTTP response into HttpResponse model."""
        return self._deserialize_body(response).flat_map(
            lambda body: u.try_(
                lambda: m.Api.HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                    request_id="",
                ),
                catch=(c.ValidationError, ValueError, TypeError),
            ).map_error(lambda exc: f"Response model validation failed: {exc}")
        )

    def _handle_transport_error(
        self, exc: Exception, op: str
    ) -> p.Result[m.Api.HttpResponse]:
        """Convert transport exception to failure result."""
        return r[m.Api.HttpResponse].fail_op(op, exc)


__all__: t.MutableSequenceOf[str] = ["FlextApiClientBaseRequestMixin"]
