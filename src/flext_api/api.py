"""FLEXT API - Unified HTTP Facade.

Single entry point for all HTTP operations. Delegates to FlextApiClient for
actual HTTP work, to FlextApiModels for data validation. 100% GENERIC.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, Self

from flext_core import FlextResult, FlextService

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes


class FlextApi(FlextService[FlextApiConfig]):
    """Unified HTTP API facade - pure delegation pattern.

    Single responsibility: Delegate HTTP operations to FlextApiClient.
    All configuration through FlextApiConfig model.
    All data validation through FlextApiModels.
    100% GENERIC - no domain coupling.
    """

    # Unified namespace - direct access to FLEXT components
    Models: ClassVar = FlextApiModels
    Config: ClassVar = FlextApiConfig

    def __new__(cls, config: FlextApiConfig | None = None) -> Self:
        """Intercept positional config argument and convert to kwargs.

        Args:
            config: Optional FlextApiConfig (passed to __init__ via attribute).

        """
        instance = super().__new__(cls)
        if config is not None:
            # Type-safe attribute assignment for __new__ pattern
            # Use object.__setattr__ to bypass type checker for dynamic attribute
            object.__setattr__(instance, "_flext_api_config", config)
        return instance

    def __init__(self, config: FlextApiConfig | None = None, **kwargs: object) -> None:
        """Initialize with optional config.

        Args:
        config: FlextApiConfig model or None for defaults.
        **kwargs: Additional Pydantic model fields (ignored for this service).

        """
        super().__init__(**kwargs)
        api_config = getattr(self, "_flext_api_config", None)
        if api_config is not None:
            self._config = api_config
            delattr(self, "_flext_api_config")
        elif config is not None:
            self._config = config
        else:
            self._config = FlextApiConfig()
        self._client = FlextApiClient(config=self._config)

    def execute(self, **_kwargs: object) -> FlextResult[FlextApiConfig]:
        """Execute FlextService interface."""
        return FlextResult[FlextApiConfig].ok(self._config)

    def request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request - pure delegation to client.

        Args:
        request: HttpRequest model.

        Returns:
        FlextResult[HttpResponse]: Response or error.

        """
        return self._client.request(request)

    def _validate_request_body(
        self, body: object
    ) -> FlextResult[FlextApiTypes.RequestBody]:
        """Validate request body type - helper to reduce complexity."""
        if isinstance(body, (dict, str, bytes)):
            return FlextResult[FlextApiTypes.RequestBody].ok(body)
        return FlextResult[FlextApiTypes.RequestBody].fail(
            f"Invalid body type: {type(body)}"
        )

    def _extract_body_from_kwargs(
        self,
        data: FlextApiTypes.RequestBody | None,
        request_kwargs: FlextApiTypes.RequestKwargs | None,
    ) -> FlextResult[FlextApiTypes.RequestBody]:
        """Extract body from explicit data or request_kwargs - no fallbacks."""
        # Priority 1: Explicit data parameter
        if data is not None:
            return self._validate_request_body(data)

        # Priority 2: request_kwargs
        if request_kwargs is None:
            return FlextResult[FlextApiTypes.RequestBody].ok({})

        # Check json in kwargs (priority over data)
        if "json" in request_kwargs and request_kwargs["json"] is not None:
            json_value = request_kwargs["json"]
            if isinstance(json_value, dict):
                return FlextResult[FlextApiTypes.RequestBody].ok(json_value)
            return FlextResult[FlextApiTypes.RequestBody].fail(
                f"Invalid json type: {type(json_value)}"
            )

        # Check data in kwargs
        if "data" in request_kwargs and request_kwargs["data"] is not None:
            return self._validate_request_body(request_kwargs["data"])

        # No body provided - empty dict is valid
        return FlextResult[FlextApiTypes.RequestBody].ok({})

    def _merge_headers(
        self,
        explicit_headers: dict[str, str] | None,
        request_kwargs: FlextApiTypes.RequestKwargs | None,
    ) -> FlextResult[dict[str, str]]:
        """Merge headers from kwargs and explicit headers - no fallbacks."""
        combined_headers: dict[str, str] = {}
        if request_kwargs is not None and "headers" in request_kwargs:
            kw_headers_value = request_kwargs["headers"]
            if isinstance(kw_headers_value, dict):
                # Convert WebHeaders (dict[str, str | list[str]]) to dict[str, str]
                for key, value in kw_headers_value.items():
                    if isinstance(value, str):
                        combined_headers[key] = value
                    elif isinstance(value, list):
                        # Convert list to comma-separated string
                        combined_headers[key] = ", ".join(str(v) for v in value)
                    else:
                        combined_headers[key] = str(value)
            elif kw_headers_value is not None:
                return FlextResult[dict[str, str]].fail(
                    f"Invalid headers type: {type(kw_headers_value)}"
                )
        if explicit_headers is not None:
            combined_headers.update(explicit_headers)
        return FlextResult[dict[str, str]].ok(combined_headers)

    def _validate_timeout_value(
        self, timeout_value: object, timeout_min: float, timeout_max: float
    ) -> FlextResult[float]:
        """Validate a single timeout value - helper to reduce complexity."""
        if isinstance(timeout_value, (int, float)):
            timeout_float = float(timeout_value)
            if timeout_min <= timeout_float <= timeout_max:
                return FlextResult[float].ok(timeout_float)
            return FlextResult[float].fail(
                f"Timeout {timeout_float} out of range [{timeout_min}, {timeout_max}]"
            )
        if isinstance(timeout_value, str):
            try:
                timeout_float = float(timeout_value)
                if timeout_min <= timeout_float <= timeout_max:
                    return FlextResult[float].ok(timeout_float)
                return FlextResult[float].fail(
                    f"Timeout {timeout_float} out of range [{timeout_min}, {timeout_max}]"
                )
            except ValueError:
                return FlextResult[float].fail(
                    f"Invalid timeout value: {timeout_value}"
                )
        if timeout_value is not None:
            return FlextResult[float].fail(
                f"Invalid timeout type: {type(timeout_value)}"
            )
        return FlextResult[float].fail("Timeout value is None")

    def _validate_and_extract_timeout(
        self,
        timeout: float | None,
        request_kwargs: FlextApiTypes.RequestKwargs | None,
    ) -> FlextResult[float]:
        """Extract and validate timeout value - no fallbacks."""
        timeout_min = 0.1
        timeout_max = FlextApiConstants.VALIDATION_LIMITS["MAX_TIMEOUT"]

        # Check explicit timeout first
        if timeout is not None:
            return self._validate_timeout_value(timeout, timeout_min, timeout_max)

        # Check request_kwargs
        if request_kwargs is not None and "timeout" in request_kwargs:
            timeout_kwarg = request_kwargs["timeout"]
            if timeout_kwarg is not None:
                return self._validate_timeout_value(
                    timeout_kwarg, timeout_min, timeout_max
                )

        # Use config timeout as default (this is OK - it's a valid default from config)
        # Ensure it's a float
        config_timeout = float(self._config.timeout)
        return FlextResult[float].ok(config_timeout)

    def _http_method(
        self,
        method: str,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
        timeout: float | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Generic HTTP method executor using monadic patterns - no fallbacks.

        Args:
        method: HTTP method (GET, POST, etc.).
        url: Request URL.
        data: Optional body.
        headers: Optional headers.
        request_kwargs: Additional parameters aligned with FlextApiModels.HttpRequest.
        timeout: Optional timeout override.

        Returns:
        FlextResult[HttpResponse]: Response or error.

        """
        # Extract body using monadic pattern
        body_result = self._extract_body_from_kwargs(data, request_kwargs)
        if body_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                body_result.error or "Body extraction failed"
            )

        # Merge headers using monadic pattern
        headers_result = self._merge_headers(headers, request_kwargs)
        if headers_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                headers_result.error or "Header extraction failed"
            )

        # Validate timeout using monadic pattern
        timeout_result = self._validate_and_extract_timeout(timeout, request_kwargs)
        if timeout_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                timeout_result.error or "Timeout extraction failed"
            )

        # Extract query params - use empty dict if not present
        query_params: FlextApiTypes.WebParams = {}
        if request_kwargs is not None and "params" in request_kwargs:
            params_value = request_kwargs["params"]
            if params_value is not None:
                # Convert dict[str, str] to WebParams (dict[str, str | list[str]])
                if isinstance(params_value, dict):
                    query_params = {
                        k: (v if isinstance(v, (str, list)) else str(v))
                        for k, v in params_value.items()
                    }
                else:
                    return FlextResult[FlextApiModels.HttpResponse].fail(
                        f"Invalid params type: {type(params_value)}"
                    )

        # Use body value directly (HttpRequest accepts empty dict or actual body)
        body_value = body_result.unwrap()
        body_final: FlextApiTypes.RequestBody = body_value

        # Create request model
        http_request = FlextApiModels.HttpRequest(
            method=method,
            url=url,
            body=body_final,
            headers=headers_result.unwrap(),
            query_params=query_params,
            timeout=timeout_result.unwrap(),
        )
        return self.request(http_request)

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP GET - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.GET,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def post(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP POST - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.POST,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def put(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP PUT - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.PUT,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP DELETE - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.DELETE,
            url=url,
            headers=headers,
            request_kwargs=request_kwargs,
        )

    def patch(
        self,
        url: str,
        data: FlextApiTypes.RequestBody | None = None,
        headers: dict[str, str] | None = None,
        request_kwargs: FlextApiTypes.RequestKwargs | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP PATCH - delegates to generic method."""
        return self._http_method(
            method=FlextApiConstants.Method.PATCH,
            url=url,
            data=data,
            headers=headers,
            request_kwargs=request_kwargs,
        )


__all__ = ["FlextApi"]
