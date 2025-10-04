"""HTTP Client Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from typing import Self

import httpx
from flext_core import FlextLogger, FlextResult, FlextTypes

from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols


class HttpClientImplementation(FlextApiProtocols.HttpClientProtocol):
    """HTTP client implementation conforming to HttpClientProtocol."""

    def __init__(self, client_config: FlextApiModels.ClientConfig) -> None:
        """Initialize HTTP client protocol implementation.

        Args:
            client_config: HTTP client configuration

        """
        self._config = client_config
        self._logger = FlextLogger(__name__)

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
                max_connections=100,  # Connection pooling
                max_keepalive_connections=20,
            ),
            follow_redirects=True,
            verify=True,  # SSL verification enabled by default
        )

    def request(
        self,
        method: str,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute an HTTP request conforming to protocol."""
        try:
            # Build full URL
            if url.startswith(("http://", "https://")):
                full_url = url
            else:
                # Ensure base_url is a proper string
                base_url_str = str(self._config.base_url)
                if base_url_str.startswith("ParseResult("):
                    # Handle case where base_url is stored as ParseResult string representation
                    # Extract the actual URL from the string representation
                    match = re.search(
                        r"scheme='([^']*)'.*netloc='([^']*)'", base_url_str
                    )
                    if match:
                        scheme, netloc = match.groups()
                        base_url_str = f"{scheme}://{netloc}"
                    else:
                        base_url_str = "http://localhost:8000"  # fallback

                base_url_clean = base_url_str.rstrip("/")
                url_clean = url.lstrip("/")
                full_url = (
                    f"{base_url_clean}/{url_clean}" if url_clean else base_url_clean
                )

            # Prepare headers
            request_headers: dict[str, str] = dict(self._config.headers or {})
            headers_value = kwargs.get("headers")
            if headers_value and isinstance(headers_value, dict):
                request_headers.update(headers_value)

            # Prepare request parameters
            request_kwargs: FlextTypes.Dict = {
                "method": method,
                "url": full_url,
                "headers": request_headers,
            }

            # Add other parameters from kwargs
            allowed_keys = {"params", "data", "json", "content", "files"}
            request_kwargs.update({
                key: value for key, value in kwargs.items() if key in allowed_keys
            })

            # Make the HTTP request using httpx client
            httpx_response = self._client.request(**request_kwargs)

            # Convert httpx response to FlextApiModels.HttpResponse
            response = FlextApiModels.HttpResponse(
                status_code=httpx_response.status_code,
                headers=dict(httpx_response.headers),
                body=httpx_response.content,
                url=str(httpx_response.url),
                method=method,
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except httpx.TimeoutException as e:
            error_msg = f"HTTP request timeout: {e}"
            self._logger.warning(error_msg)
            return FlextResult[FlextApiModels.HttpResponse].fail(error_msg)

        except httpx.NetworkError as e:
            error_msg = f"HTTP network error: {e}"
            self._logger.warning(error_msg)
            return FlextResult[FlextApiModels.HttpResponse].fail(error_msg)

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            self._logger.warning(error_msg)
            # Still return a response for HTTP errors
            response = FlextApiModels.HttpResponse(
                status_code=e.response.status_code,
                headers=dict(e.response.headers),
                body=e.response.content,
                url=str(e.response.url),
                method=method,
            )
            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except Exception as e:
            error_msg = f"HTTP protocol request failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[FlextApiModels.HttpResponse].fail(error_msg)

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
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP GET request."""
        return self.request("GET", url, **kwargs)

    def post(
        self,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP POST request."""
        return self.request("POST", url, **kwargs)

    def put(
        self,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP PUT request."""
        return self.request("PUT", url, **kwargs)

    def delete(
        self,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP DELETE request."""
        return self.request("DELETE", url, **kwargs)
