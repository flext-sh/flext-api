"""HTTP Client Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Self, override

import httpx
from flext_core import FlextLogger, r
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from flext_api import FlextApiConstants, m, p, t


class _HttpClientRequestOptions(BaseModel):
    """Internal model for HTTP client request options.

    Validates and structures optional request parameters passed to httpx.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    params: Mapping[str, str] | None = Field(
        default=None, description="Query parameters"
    )
    json_data: t.Container | None = Field(default=None, description="JSON body")
    content: bytes | None = Field(default=None, description="Raw content body")
    data: Mapping[str, object] | None = Field(default=None, description="Form data")
    timeout: float | None = Field(default=None, description="Request timeout")
    headers: Mapping[str, str] = Field(
        default_factory=dict, description="Request headers"
    )


class FlextWebClientImplementation(p.Api.Client.HttpClientProtocol):
    """HTTP client implementation conforming to FlextWebClientProtocol."""

    def __init__(self, client_config: m.ClientConfig) -> None:
        """Initialize HTTP client protocol implementation.

        Args:
        client_config: HTTP client configuration

        """
        self._config = client_config
        self.logger = FlextLogger(__name__)
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                timeout=client_config.timeout,
                connect=client_config.timeout,
                read=client_config.timeout,
                write=client_config.timeout,
                pool=client_config.timeout,
            ),
            limits=httpx.Limits(
                max_connections=FlextApiConstants.Api.HTTPClient.DEFAULT_MAX_CONNECTIONS,
                max_keepalive_connections=FlextApiConstants.Api.HTTPClient.DEFAULT_MAX_KEEPALIVE_CONNECTIONS,
            ),
            follow_redirects=True,
            verify=client_config.verify_ssl,
        )

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit context manager and close client."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        self._client.close()

    @override
    def delete(self, url: str, **kwargs: t.Scalar) -> r[t.Api.HttpResponseDict]:
        """Execute HTTP DELETE request."""
        return self.request(FlextApiConstants.Api.Method.DELETE, url, **kwargs)

    @override
    def get(self, url: str, **kwargs: t.Scalar) -> r[t.Api.HttpResponseDict]:
        """Execute HTTP GET request."""
        return self.request(FlextApiConstants.Api.Method.GET, url, **kwargs)

    @override
    def post(self, url: str, **kwargs: t.Scalar) -> r[t.Api.HttpResponseDict]:
        """Execute HTTP POST request."""
        return self.request(FlextApiConstants.Api.Method.POST, url, **kwargs)

    @override
    def put(self, url: str, **kwargs: t.Scalar) -> r[t.Api.HttpResponseDict]:
        """Execute HTTP PUT request."""
        return self.request(FlextApiConstants.Api.Method.PUT, url, **kwargs)

    @override
    def request(
        self, method: str, url: str, **kwargs: t.Scalar
    ) -> r[t.Api.HttpResponseDict]:
        """Execute an HTTP request conforming to protocol."""
        full_url_result = self._build_full_url(url)
        if full_url_result.is_failure:
            return r[t.Api.HttpResponseDict].fail(
                full_url_result.error or "URL building failed"
            )
        options_result = self._build_request_options(kwargs)
        if options_result.is_failure:
            return r[t.Api.HttpResponseDict].fail(
                options_result.error or "Invalid request options"
            )
        options = options_result.value
        headers = self._prepare_request_headers(options)
        return self._execute_httpx_request(
            method, full_url_result.value, headers, options
        )

    def _build_full_url(self, url: str) -> r[str]:
        """Build full URL from configuration base_url and provided path."""
        if url.startswith(("http://", "https://")):
            return r[str].ok(url)
        base_url = self._config.base_url
        if not base_url:
            return r[str].fail("base_url is required when URL is not absolute")
        normalized_base = base_url.rstrip("/")
        normalized_path = str(url).lstrip("/")
        full_url = (
            f"{normalized_base}/{normalized_path}"
            if normalized_path
            else normalized_base
        )
        return r[str].ok(full_url)

    def _build_request_options(
        self, kwargs: Mapping[str, object]
    ) -> r[_HttpClientRequestOptions]:
        """Build typed request options from arbitrary kwargs."""
        try:
            options = _HttpClientRequestOptions.model_validate(kwargs)
        except ValidationError as exc:
            details = (
                exc.errors()[0]["msg"] if exc.errors() else "Invalid request kwargs"
            )
            return r[_HttpClientRequestOptions].fail(str(details))
        return r[_HttpClientRequestOptions].ok(options)

    def _create_response_from_httpx(
        self, httpx_response: httpx.Response
    ) -> m.HttpResponse:
        """Convert httpx response to FlextApiModels.HttpResponse."""
        return m.HttpResponse(
            status_code=httpx_response.status_code,
            headers=dict(httpx_response.headers),
            body=httpx_response.content,
        )

    def _execute_httpx_request(
        self,
        method: str,
        full_url: str,
        headers: Mapping[str, str],
        options: _HttpClientRequestOptions,
    ) -> r[t.Api.HttpResponseDict]:
        """Execute request using typed options."""
        try:
            httpx_response = self._client.request(
                method=method,
                url=full_url,
                headers=headers,
                params=options.params,
                json=options.json_data,
                content=options.content,
                data=options.data,
                timeout=options.timeout,
            )
            response = self._create_response_from_httpx(httpx_response)
            return r[t.Api.HttpResponseDict].ok(self._response_to_dict(response))
        except httpx.HTTPStatusError as exc:
            error_msg = f"HTTP error {exc.response.status_code}: {exc.response.text}"
            self.logger.warning(error_msg)
            response = self._create_response_from_httpx(exc.response)
            return r[t.Api.HttpResponseDict].ok(self._response_to_dict(response))
        except httpx.TimeoutException as exc:
            error_msg = f"HTTP request timeout: {exc}"
            self.logger.warning(error_msg)
            return r[t.Api.HttpResponseDict].fail(error_msg)
        except httpx.NetworkError as exc:
            error_msg = f"HTTP network error: {exc}"
            self.logger.warning(error_msg)
            return r[t.Api.HttpResponseDict].fail(error_msg)
        except (
            ValueError,
            TypeError,
            KeyError,
            httpx.HTTPError,
            ConnectionError,
        ) as exc:
            error_msg = f"HTTP protocol request failed: {exc}"
            self.logger.exception(error_msg)
            return r[t.Api.HttpResponseDict].fail(error_msg)

    def _prepare_request_headers(
        self,
        options: _HttpClientRequestOptions,
    ) -> Mapping[str, str]:
        """Prepare merged headers from config and request."""
        headers = dict(self._config.headers)
        headers.update(options.headers)
        return headers

    def _response_to_dict(self, response: m.HttpResponse) -> t.Api.HttpResponseDict:
        """Convert HttpResponse model to HttpResponseDict for protocol compliance."""
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "body": response.body,
            "request_id": response.request_id,
        }
