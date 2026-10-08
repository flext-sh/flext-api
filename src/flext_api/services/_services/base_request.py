"""Common HTTP request execution helpers shared by sync and async clients.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx

from flext_api import c, m, p, r, settings, t, u
from flext_api.services import FlextApiClientCodecMixin


class FlextApiClientBaseRequestMixin(FlextApiClientCodecMixin):
    """Shared request execution helpers for sync and async clients."""

    @staticmethod
    def _build_url(path: str) -> p.Result[str]:
        """Build full URL from base_url and path.

        Returns:
            The resulting ``p.Result[str]``.
        """
        api_settings = settings.Api
        path_stripped = path.strip()
        if not path_stripped:
            return r[str].fail(c.Api.URL_PATH_EMPTY_ERROR)
        if not api_settings.base_url.strip():
            return r[str].ok(path_stripped)
        separator = c.Api.URL_PATH_SEPARATOR
        base = api_settings.base_url.strip().rstrip(separator)
        if path_stripped.startswith(separator):
            return r[str].ok(f"{base}{path_stripped}")
        return r[str].ok(f"{base}{separator}{path_stripped}")

    def _prepare_request(
        self,
        request: m.Api.HttpRequest,
    ) -> p.Result[tuple[str, t.StrMapping, bytes, t.StrMapping]]:
        """Prepare URL, headers, body, and extensions for HTTP request.

        Returns:
            The resulting ``p.Result[tuple[str, t.StrMapping, bytes, t.StrMapping]]``.
        """
        url_result = self._build_url(request.url)
        if url_result.failure:
            return r[tuple[str, t.StrMapping, bytes, t.StrMapping]].from_failure(
                url_result,
            )
        request_body: t.Api.RequestBody = (
            request.body if request.body is not None else b""
        )
        body_result = self._serialize_body(request_body)
        if body_result.failure:
            return r[tuple[str, t.StrMapping, bytes, t.StrMapping]].from_failure(
                body_result,
            )
        headers: t.StrMapping = {**settings.Api.default_headers, **request.headers}
        extensions: t.StrMapping = (
            {c.Api.REQUEST_EXTENSION_SNI_HOSTNAME: request.sni_hostname}
            if request.sni_hostname
            else {}
        )
        return r[tuple[str, t.StrMapping, bytes, t.StrMapping]].ok((
            url_result.value,
            headers,
            body_result.value,
            extensions,
        ))

    def _handle_response(
        self,
        response: httpx.Response,
    ) -> p.Result[m.Api.HttpResponse]:
        """Process HTTP response into HttpResponse model.

        Returns:
            The resulting ``p.Result[m.Api.HttpResponse]``.
        """
        return self._deserialize_body(response).flat_map(
            lambda body: u.try_(
                lambda: m.Api.HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                    content=response.content,
                    request_id="",
                ),
                catch=(c.ValidationError, ValueError, TypeError),
            ).map_error(lambda exc: f"Response model validation failed: {exc}"),
        )

    @staticmethod
    def _handle_transport_error(
        exc: Exception,
        op: str,
    ) -> p.Result[m.Api.HttpResponse]:
        """Convert transport exception to failure result.

        Returns:
            The resulting ``p.Result[m.Api.HttpResponse]``.
        """
        return r[m.Api.HttpResponse].fail_op(op, exc)


__all__: t.MutableSequenceOf[str] = ["FlextApiClientBaseRequestMixin"]
