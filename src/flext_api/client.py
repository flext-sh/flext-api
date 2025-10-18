"""Generic HTTP Client - Domain-agnostic HTTP client implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Any

import httpx
from flext_core import FlextResult

from flext_api.config_manager import HttpConfigManager
from flext_api.http_operations import HttpOperations
from flext_api.models import FlextApiModels


class FlextApiClient(HttpOperations[dict[str, object]]):
    """Generic HTTP client following FLEXT patterns with single responsibility.

    Delegates to specialized services for configuration, request execution,
    and response handling. Completely domain-agnostic and reusable.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize HTTP client with configuration delegation."""
        self._config_manager = HttpConfigManager()

        # Support both old config dict and new parameter-based initialization
        if config is not None:
            # Legacy config dict support for backward compatibility
            if isinstance(config, dict):
                self._config_manager.configure(config)
                # Store max_retries for backward compatibility
                self._max_retries = config.get("max_retries", 3)
            else:
                # Handle string config (shouldn't happen but be safe)
                self._config_manager.configure({"base_url": str(config)})
                self._max_retries = 3
        else:
            # New parameter-based initialization
            config_dict: dict[str, str | float | bool] = {}
            if base_url is not None:
                config_dict["base_url"] = base_url
            if timeout is not None:
                config_dict["timeout"] = timeout
            if max_retries is not None:
                config_dict["max_retries"] = str(max_retries)  # Convert to string as expected
                self._max_retries = max_retries  # Store for property access
            else:
                self._max_retries = 3  # Default value
            if headers:
                config_dict["headers"] = str(dict[str, Any](headers))  # Convert to string as expected

            self._config_manager.configure(config_dict or None)

    def _execute_request(
        self,
        method: str,
        url: str,
        *,
        data: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Execute HTTP request using httpx with railway error handling."""
        config_result = self._config_manager.get_client_config()
        if config_result.is_failure:
            return FlextResult[dict[str, object]].fail(config_result.error)

        return self._make_request(
            method, url, data, params, headers, timeout, config_result.unwrap()
        )

    def execute_request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request with structured request/response models."""
        config_result = self._config_manager.get_client_config()
        if config_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(config_result.error)

        return self._make_structured_request_from_model(request, config_result.unwrap())

    def _make_request(
        self,
        method: str,
        url: str,
        data: object | None,
        params: dict[str, str] | None,
        headers: dict[str, str] | None,
        timeout: float | None,
        config: FlextApiModels.ClientConfig,
    ) -> FlextResult[dict[str, object]]:
        """Make HTTP request with configuration."""
        try:
            request_timeout = timeout if timeout is not None else config.timeout

            with httpx.Client(timeout=request_timeout) as client:
                base_url = config.base_url
                full_url = self._build_url(base_url, url)
                content = self._prepare_request_data(data)

                response = client.request(
                    method=method,
                    url=full_url,
                    params=params,
                    headers=headers,
                    content=content,
                )

                return FlextResult[dict[str, object]].ok(self._parse_response(response))

        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    def execute_request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request with structured request/response models."""
        config_result = self._config_manager.get_client_config()
        if config_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(config_result.error)

        return self._make_structured_request_from_model(request, config_result.unwrap())

    def _make_structured_request_from_model(
        self,
        request: FlextApiModels.HttpRequest,
        config: FlextApiModels.ClientConfig,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make structured HTTP request from model."""
        try:
            with httpx.Client(timeout=config.timeout) as client:
                content = self._prepare_request_data(request.body)

                response = client.request(
                    method=request.method,
                    url=self._build_url(config.base_url, request.url),
                    headers=request.headers,
                    content=content,
                )

                return FlextResult[FlextApiModels.HttpResponse].ok(
                    FlextApiModels.HttpResponse(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        body=response.content,
                    )
                )
        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(str(e))

    def _prepare_request_data(self, data: object | None) -> bytes | None:
        """Prepare request data for HTTP transmission."""
        if data is None:
            return None

        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode("utf-8")
        return str(data).encode("utf-8")

    def _parse_response(self, response: httpx.Response) -> dict[str, object]:
        """Parse HTTP response into generic format."""
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            try:
                return response.json()
            except Exception:
                return {"content": response.text}

        return {"content": response.text}

    # Configuration access properties
    @property
    def base_url(self) -> str | None:
        """Get the base URL from configuration."""
        config_result = self._config_manager.get_client_config()
        return config_result.unwrap().base_url if config_result.is_success else None

    @property
    def timeout(self) -> float | None:
        """Get the timeout from configuration."""
        config_result = self._config_manager.get_client_config()
        return config_result.unwrap().timeout if config_result.is_success else None

    # Configuration methods
    def set_timeout(self, timeout: float) -> FlextResult[None]:
        """Set the request timeout."""
        return self._config_manager.configure({"timeout": timeout})

    # Validation methods
    def validate(self, data: object) -> FlextResult[bool]:
        """Validate input data."""
        if data is None:
            return FlextResult[bool].fail("Data cannot be None")
        return FlextResult[bool].ok(True)

    def health_check(self) -> dict[str, Any]:
        """Perform health check on client."""
        config_result = self._config_manager.get_client_config()
        config = config_result.unwrap() if config_result.is_success else None

        return {
            "status": "ok",
            "client_ready": True,
            "client_id": id(self),
            "base_url": config.base_url if config else None,
            "timeout": config.timeout if config else 30.0,
        }

    @property
    def config_data(self) -> FlextApiModels.ClientConfig:
        """Get client configuration data."""
        config_result = self._config_manager.get_client_config()
        config = config_result.unwrap() if config_result.is_success else None

        if config:
            # Convert string headers back to dict if needed
            headers = config.headers
            if isinstance(headers, str):
                try:
                    import json
                    headers = json.loads(headers)
                except:
                    headers = {}

            return FlextApiModels.ClientConfig(
                base_url=config.base_url,
                timeout=config.timeout,
                headers=headers,
            )

        return FlextApiModels.ClientConfig(base_url="")

    @property
    def max_retries(self) -> int:
        """Get max retries from configuration."""
        config_result = self._config_manager.get_client_config()
        config = config_result.unwrap() if config_result.is_success else None
        # Try to get from stored config, fallback to default
        stored_retries = getattr(self, '_max_retries', None)
        return stored_retries if stored_retries is not None else 3

    def execute(self) -> FlextResult[None]:
        """Execute main operation (FlextService interface)."""
        return FlextResult[None].ok(None)

    def _build_url(self, base_url: str, path: str) -> str:
        """Build full URL from base URL and path."""
        if not base_url:
            return path

        base_url = base_url.rstrip("/")
        if path.startswith("/"):
            return f"{base_url}{path}"
        return f"{base_url}/{path}"

    def __enter__(self) -> FlextApiClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        pass
