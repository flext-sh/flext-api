"""FLEXT API Client - HTTP client using flext-core foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx
from flext_core import FlextCore

from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels


class FlextApiClient:
    """Unified HTTP client orchestrator providing enterprise-grade HTTP operations.

    The FlextApiClient serves as the foundation HTTP client for the entire FLEXT
    providing comprehensive HTTP operations, connection management, and error handling
    through the FlextCore.Result railway pattern. This is the MANDATORY HTTP client for all
    FLEXT projects - NO custom HTTP implementations allowed.
    """

    class ConfigurationManager:
        """Configuration management for FlextApiClient."""

        def __init__(self) -> None:
            """Initialize configuration manager."""
            self._config: FlextApiConfig | None = None

        def configure(
            self, config: FlextApiConfig | dict[str, Any] | None = None
        ) -> FlextCore.Result[None]:
            """Configure the HTTP client."""
            try:
                if config is None:
                    self._config = FlextApiConfig()
                elif isinstance(config, dict):
                    self._config = FlextApiConfig(**config)
                elif isinstance(config, FlextApiConfig):
                    self._config = config
                else:
                    return FlextCore.Result[None].fail(
                        f"Invalid configuration type: {type(config)}"
                    )

                return self._validate_configuration()
            except Exception as e:
                return FlextCore.Result[None].fail(f"Configuration failed: {e}")

        def _validate_configuration(self) -> FlextCore.Result[None]:
            """Validate current configuration."""
            if self._config is None:
                return FlextCore.Result[None].fail("No configuration set")

            if self._config.timeout <= 0:
                return FlextCore.Result[None].fail("Timeout must be positive")

            if self._config.max_retries < 0:
                return FlextCore.Result[None].fail("Max retries cannot be negative")

            return FlextCore.Result[None].ok(None)

        def get_client_config(self) -> FlextCore.Result[FlextApiModels.ClientConfig]:
            """Get client configuration."""
            if self._config is None:
                return FlextCore.Result[FlextApiModels.ClientConfig].fail(
                    "No configuration set"
                )

            return FlextCore.Result[FlextApiModels.ClientConfig].ok(
                FlextApiModels.ClientConfig(
                    base_url=self._config.base_url
                    or FlextApiConstants.DEFAULT_BASE_URL,
                    timeout=self._config.timeout,
                    headers=self._config.get_default_headers()
                    if hasattr(self._config, "get_default_headers")
                    else {},
                )
            )

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Initialize FlextApiClient with configuration."""
        self._config_manager = self.ConfigurationManager()
        self._config_manager.configure({
            "base_url": base_url,
            "timeout": timeout,
            "max_retries": max_retries,
            "headers": dict(headers) if headers else {},
        })

    def request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
        """Execute HTTP request."""
        config_result = self._config_manager.get_client_config()
        if config_result.is_failure:
            return FlextCore.Result[FlextApiModels.HttpResponse].fail(
                config_result.error
            )

        try:
            with httpx.Client(timeout=config_result.unwrap().timeout) as client:
                response = client.request(
                    method=request.method,
                    url=f"{config_result.unwrap().base_url}{request.url}",
                    headers=request.headers,
                    content=request.body,
                )
                return FlextCore.Result[FlextApiModels.HttpResponse].ok(
                    FlextApiModels.HttpResponse(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        body=response.text,
                    )
                )
        except Exception as e:
            return FlextCore.Result[FlextApiModels.HttpResponse].fail(str(e))
