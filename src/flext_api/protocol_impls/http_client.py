"""HTTP Client Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Self

import httpx
from flext_core import r
from flext_core.loggings import FlextLogger

from flext_api import FlextApiConstants, FlextApiModels, FlextApiTypes, p


class FlextWebClientImplementation(p.HttpClientProtocol):
    """HTTP client implementation conforming to FlextWebClientProtocol."""

    def __init__(self, client_config: FlextApiModels.ClientConfig) -> None:
        """Initialize HTTP client protocol implementation.

        Args:
        client_config: HTTP client configuration

        """
        self._config = client_config
        self.logger = FlextLogger(__name__)

        # Create httpx client with configuration
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                timeout=client_config.timeout,
                connect=client_config.timeout,
                read=client_config.timeout,
                write=client_config.timeout,
                pool=client_config.timeout,
            ),
            limits=httpx.Limits(
                max_connections=FlextApiConstants.HTTPClient.DEFAULT_MAX_CONNECTIONS,
                max_keepalive_connections=(
                    FlextApiConstants.HTTPClient.DEFAULT_MAX_KEEPALIVE_CONNECTIONS
                ),
            ),
            follow_redirects=True,
            verify=client_config.verify_ssl,
        )

    def _prepare_request_headers(self, kwargs: dict[str, object]) -> dict[str, str]:
        """Prepare merged headers from config and request."""
        headers = dict(self._config.headers)
        if "headers" in kwargs:
            kwargs_headers = kwargs["headers"]
            if isinstance(kwargs_headers, dict):
                headers.update({
                    k: v for k, v in kwargs_headers.items() if isinstance(v, str)
                })
        return headers

    def _extract_request_data(
        self,
        kwargs: dict[str, object],
    ) -> dict[str, object | None]:
        """Extract and type request data parameters."""
        params: dict[str, str] | None = None
        if "params" in kwargs:
            params_value = kwargs["params"]
            if isinstance(params_value, dict):
                params = params_value

        json_data: object | None = None
        if "json" in kwargs:
            json_data = kwargs["json"]

        content: object | None = None
        if "content" in kwargs:
            content = kwargs["content"]

        data: object | None = None
        if "data" in kwargs:
            data = kwargs["data"]

        files: object | None = None
        if "files" in kwargs:
            files = kwargs["files"]

        return {
            "params": params,
            "json": json_data,
            "content": content,
            "data": data,
            "files": files,
        }

    def _create_response_from_httpx(
        self,
        httpx_response: httpx.Response,
    ) -> FlextApiModels.HttpResponse:
        """Convert httpx response to FlextApiModels.HttpResponse."""
        return FlextApiModels.HttpResponse(
            status_code=httpx_response.status_code,
            headers=dict(httpx_response.headers),
            body=httpx_response.content,
        )

    def _response_to_dict(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextApiTypes.HttpResponseDict:
        """Convert HttpResponse model to HttpResponseDict for protocol compliance."""
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "body": response.body,
            "request_id": response.request_id,
        }

    def _handle_http_error(
        self,
        e: httpx.HTTPStatusError,
    ) -> r[FlextApiTypes.HttpResponseDict]:
        """Handle HTTP status errors."""
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        self.logger.warning(error_msg)
        response = self._create_response_from_httpx(e.response)
        return r[FlextApiTypes.HttpResponseDict].ok(self._response_to_dict(response))

    def _handle_request_exception(
        self,
        e: Exception,
        error_prefix: str,
    ) -> r[FlextApiTypes.HttpResponseDict]:
        """Handle general request exceptions."""
        error_msg = f"{error_prefix}: {e}"
        if isinstance(e, (httpx.TimeoutException, httpx.NetworkError)):
            self.logger.warning(error_msg)
        else:
            self.logger.error(error_msg)
        return r[FlextApiTypes.HttpResponseDict].fail(error_msg)

    def _build_httpx_kwargs(
        self,
        method: str,
        full_url: str,
        headers: dict[str, str],
        request_data: dict[str, object],
    ) -> dict[str, object]:
        """Build kwargs for httpx.request call."""
        kwargs: dict[str, object] = {
            "method": method,
            "url": full_url,
            "headers": headers,
        }

        # Add optional parameters with type validation
        if (params := request_data.get("params")) is not None and isinstance(
            params,
            dict,
        ):
            kwargs["params"] = params
            if (json_value := request_data.get("json")) is not None:
                kwargs["json"] = json_value
            elif (content := request_data.get("content")) is not None and isinstance(
                content,
                (str, bytes),
            ):
                kwargs["content"] = content
            elif (data := request_data.get("data")) is not None and isinstance(
                data,
                dict,
            ):
                kwargs["data"] = data
        elif (json_value := request_data.get("json")) is not None:
            kwargs["json"] = json_value
        elif (content := request_data.get("content")) is not None and isinstance(
            content,
            (str, bytes),
        ):
            kwargs["content"] = content
        elif (data := request_data.get("data")) is not None and isinstance(data, dict):
            kwargs["data"] = data
        elif (files := request_data.get("files")) is not None and isinstance(
            files,
            dict,
        ):
            kwargs["files"] = files

        return kwargs

    def request(
        self,
        method: str,
        url: str,
        **kwargs: object,
    ) -> r[FlextApiTypes.HttpResponseDict]:
        """Execute an HTTP request conforming to protocol."""
        try:
            full_url_result = self._build_full_url(url)
            if full_url_result.is_failure:
                return r[FlextApiTypes.HttpResponseDict].fail(
                    full_url_result.error or "URL building failed",
                )
            full_url = full_url_result.unwrap()

            headers = self._prepare_request_headers(kwargs)
            request_data = self._extract_request_data(kwargs)

            httpx_kwargs = self._build_httpx_kwargs(
                method,
                full_url,
                headers,
                request_data,
            )
            # Type narrowing: extract specific parameters for httpx.request
            method_raw = httpx_kwargs.get("method", "GET")
            method_str: str = method_raw if isinstance(method_raw, str) else "GET"
            url_raw = httpx_kwargs.get("url", "")
            url_str: str = url_raw if isinstance(url_raw, str) else ""
            if not url_str:
                return r[FlextApiTypes.HttpResponseDict].fail("Invalid URL type")
            headers_raw = httpx_kwargs.get("headers", {})
            headers_dict: dict[str, str] = (
                headers_raw if isinstance(headers_raw, dict) else {}
            )
            # Extract optional parameters with type narrowing
            params_raw = httpx_kwargs.get("params")
            params = (
                params_raw
                if isinstance(params_raw, (dict, list, tuple, str, type(None)))
                else None
            )
            json_data = httpx_kwargs.get("json")
            content_raw = httpx_kwargs.get("content")
            content = (
                content_raw
                if isinstance(content_raw, (str, bytes, type(None)))
                else None
            )
            timeout_raw = httpx_kwargs.get("timeout")
            timeout = (
                timeout_raw
                if isinstance(timeout_raw, (float, tuple, type(None)))
                else None
            )
            # Call httpx.request with explicit typed parameters
            httpx_response = self._client.request(
                method=method_str,
                url=url_str,
                headers=headers_dict,
                params=params,  # type: ignore[arg-type]
                json=json_data,  # type: ignore[arg-type]
                content=content,  # type: ignore[arg-type]
                timeout=timeout,  # type: ignore[arg-type]
            )

            response = self._create_response_from_httpx(httpx_response)
            return r[FlextApiTypes.HttpResponseDict].ok(
                self._response_to_dict(response),
            )

        except httpx.HTTPStatusError as e:
            return self._handle_http_error(e)
        except (httpx.TimeoutException, httpx.NetworkError, Exception) as e:
            error_prefix = (
                "HTTP request timeout"
                if isinstance(e, httpx.TimeoutException)
                else "HTTP network error"
                if isinstance(e, httpx.NetworkError)
                else "HTTP protocol request failed"
            )
            return self._handle_request_exception(e, error_prefix)

    def _build_full_url(self, url: str) -> r[str]:
        """Build full URL from configuration base_url and provided path.

        Args:
        url: The URL path or full URL

        Returns:
        FlextResult with full URL string or error

        """
        if url.startswith(("http://", "https://")):
            return r[str].ok(url)

        if not self._config.base_url:
            return r[str].fail("base_url is required when URL is not absolute")

        base_url_value = self._config.base_url
        if not isinstance(base_url_value, str) or not base_url_value:
            return r[str].fail("base_url must be a non-empty string")

        base_url = str(base_url_value).rstrip("/")
        path = str(url).lstrip("/")
        full_url = f"{base_url}/{path}" if path else base_url
        return r[str].ok(full_url)

    def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if hasattr(self, "_client"):
            self._client.close()

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit context manager and close client."""
        self.close()

    def get(
        self,
        url: str,
        **kwargs: object,
    ) -> r[FlextApiTypes.HttpResponseDict]:
        """Execute HTTP GET request."""
        return self.request(FlextApiConstants.Method.GET, url, **kwargs)

    def post(
        self,
        url: str,
        **kwargs: object,
    ) -> r[FlextApiTypes.HttpResponseDict]:
        """Execute HTTP POST request."""
        return self.request(FlextApiConstants.Method.POST, url, **kwargs)

    def put(
        self,
        url: str,
        **kwargs: object,
    ) -> r[FlextApiTypes.HttpResponseDict]:
        """Execute HTTP PUT request."""
        return self.request(FlextApiConstants.Method.PUT, url, **kwargs)

    def delete(
        self,
        url: str,
        **kwargs: object,
    ) -> r[FlextApiTypes.HttpResponseDict]:
        """Execute HTTP DELETE request."""
        return self.request(FlextApiConstants.Method.DELETE, url, **kwargs)
