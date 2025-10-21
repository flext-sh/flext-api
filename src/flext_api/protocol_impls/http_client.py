"""HTTP Client Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Self

import httpx
from flext_core import FlextLogger, FlextResult

from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols


class FlextWebClientImplementation(FlextApiProtocols.FlextWebClientProtocol):
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
                max_connections=100,  # Connection pooling
                max_keepalive_connections=20,
            ),
            follow_redirects=True,
            verify=client_config.verify_ssl,
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
            full_url = self._build_full_url(url)

            # Prepare headers (merge config headers with request headers)
            request_headers: dict[str, str] = {
                **self._config.headers,
                **{
                    k: v
                    for k, v in (kwargs.get("headers") or {}).items()
                    if isinstance(v, str)
                },
            }

            # Make the HTTP request using httpx client with properly typed arguments
            httpx_response = self._client.request(
                method=method,
                url=full_url,
                headers=request_headers,
                params=kwargs.get("params"),
                json=kwargs.get("json"),
                content=kwargs.get("content"),
                data=kwargs.get("data"),
                files=kwargs.get("files"),
            )

            # Convert httpx response to FlextApiModels.HttpResponse
            response = FlextApiModels.HttpResponse(
                status_code=httpx_response.status_code,
                headers=dict(httpx_response.headers),
                body=httpx_response.content,
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except httpx.TimeoutException as e:
            error_msg = f"HTTP request timeout: {e}"
            self.logger.warning(error_msg)
            return FlextResult[FlextApiModels.HttpResponse].fail(error_msg)

        except httpx.NetworkError as e:
            error_msg = f"HTTP network error: {e}"
            self.logger.warning(error_msg)
            return FlextResult[FlextApiModels.HttpResponse].fail(error_msg)

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            self.logger.warning(error_msg)
            # Still return a response for HTTP errors
            response = FlextApiModels.HttpResponse(
                status_code=e.response.status_code,
                headers=dict(e.response.headers),
                body=e.response.content,
            )
            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except Exception as e:
            error_msg = f"HTTP protocol request failed: {e}"
            self.logger.exception(error_msg)
            return FlextResult[FlextApiModels.HttpResponse].fail(error_msg)

    def _build_full_url(self, url: str) -> str:
        """Build full URL from configuration base_url and provided path.

        Args:
        url: The URL path or full URL

        Returns:
        Full URL string

        """
        if url.startswith(("http://", "https://")):
            return url

        base_url = str(self._config.base_url or "http://localhost:8000").rstrip("/")
        path = str(url).lstrip("/")
        return f"{base_url}/{path}" if path else base_url

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
