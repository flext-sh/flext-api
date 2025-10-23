"""HTTP Client Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Any, Self

import httpx
from flext_core import FlextLogger, FlextResult

from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols


class FlextWebClientImplementation(FlextApiProtocols.HttpClientProtocol):
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
            }

            kwargs_headers = kwargs.get("headers")
            if isinstance(kwargs_headers, dict):
                request_headers.update({
                    k: v for k, v in kwargs_headers.items() if isinstance(v, str)
                })

            # Extract typed parameters from kwargs with safe casting
            params: dict[str, str] | None = None
            if isinstance(kwargs.get("params"), dict):
                params = kwargs.get("params")  # type: ignore[assignment]

            json_data: Any = None
            if "json" in kwargs:
                json_data = kwargs.get("json")

            content_data: Any = None
            if "content" in kwargs:
                content_data = kwargs.get("content")

            form_data: Any = None
            if "data" in kwargs:
                form_data = kwargs.get("data")

            files_data: Any = None
            if "files" in kwargs:
                files_data = kwargs.get("files")

            # Make the HTTP request using httpx client with properly typed arguments
            httpx_response = self._client.request(
                method=method,
                url=full_url,
                headers=request_headers,
                params=params,  # type: ignore[arg-type]
                json=json_data,
                content=content_data,  # type: ignore[arg-type]
                data=form_data,  # type: ignore[arg-type]
                files=files_data,  # type: ignore[arg-type]
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
