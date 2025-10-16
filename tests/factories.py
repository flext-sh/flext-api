"""Test factories for flext-api tests.

This module provides factory functions for creating test data and objects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from typing import cast

from faker import Faker
from flext_core import FlextResult, FlextTypes
from flext_tests import FlextTestsDomains, FlextTestsUtilities

from flext_api import FlextApiClient, FlextApiConfig, FlextApiStorage
from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes

# Configure Faker for consistent test data
fake = Faker()
Faker.seed(12345)


class FlextApiFactories:
    """Factory methods using flext_tests EM ABSOLUTO - NO local implementations.

    This class has many public methods by design as it serves as a comprehensive
    factory for creating test objects. Each method creates a specific type of
    test data or object, which is a legitimate use case for having many methods.
    """

    @staticmethod
    def create_client_config(**overrides: object) -> FlextApiTypes.ResponseDict:
        """Create client config using FlextTestsDomains - ABSOLUTE usage.

        Returns:
            FlextApiTypes.ResponseDict: Client configuration dictionary.

        """
        # Use FlextTestsDomains for base configuration
        base_config = FlextTestsDomains.create_configuration()

        # Ensure required client fields
        client_config = {
            "base_url": base_config.get("base_url", "https://httpbin.org"),
            "timeout": base_config.get("timeout", 30.0),
            "max_retries": base_config.get("max_retries", 3),
            "headers": base_config.get(
                "headers",
                {"User-Agent": "FlextAPI-Test/0.9.0"},
            ),
        }
        client_config.update(overrides)
        from typing import cast

        return cast("FlextApiTypes.ResponseDict", client_config)

    @staticmethod
    def create_client(**overrides: object) -> FlextApiClient:
        """Create FlextApiClient using FlextTestsDomains config.

        Returns:
            FlextApiClient: Configured client instance.

        """
        config = FlextApiFactories.create_client_config(**overrides)
        timeout_val = config["timeout"]
        headers_val = config.get("headers", {})
        return FlextApiClient(
            base_url=str(config["base_url"]),
            timeout=int(timeout_val) if isinstance(timeout_val, (int, float)) else 30,
            max_retries=cast("int", config["max_retries"]),
            headers=cast("dict[str, str]", headers_val)
            if isinstance(headers_val, dict)
            else {},
        )

    @staticmethod
    def create_api_config(**overrides: object) -> FlextApiConfig:
        """Create FlextApiConfig using FlextTestsDomains - ABSOLUTE usage.

        Returns:
            FlextApiConfig: Configured API config instance.

        """
        # Use FlextTestsDomains for realistic configuration
        config_data = FlextTestsDomains.create_configuration()

        # Build with type-safe defaults
        defaults = {
            "api_host": str(
                config_data.get(
                    "host",
                    FlextApiConstants.DEFAULT_BASE_URL.split("://")[1].split(":")[0],
                )
            ),
            "api_port": cast(
                "int", config_data.get("port", FlextApiConstants.HTTP_PORT)
            ),
            "api_base_url": str(config_data.get("base_url", "https://httpbin.org")),
            "api_timeout": cast("float", config_data.get("default_timeout", 30.0)),
            "max_retries": cast("int", config_data.get("max_retries", 3)),
        }

        # Apply overrides safely with type checking
        for key, value in overrides.items():
            if key in defaults and isinstance(value, (str, int, float)):
                defaults[key] = value

        return FlextApiConfig(
            base_url=cast("str", defaults["base_url"]),
            timeout=cast("int", defaults["timeout"]),
            max_retries=cast("int", defaults["max_retries"]),
        )

    @staticmethod
    def create_storage_config(**overrides: object) -> dict[str, str | int | bool]:
        """Create storage config using FlextTestsDomains.

        Returns:
            FlextApiTypes.ResponseDict: Storage configuration dictionary.

        """
        # Use FlextTestsDomains for storage configuration
        base_config = FlextTestsDomains.create_configuration()

        storage_config = {
            "backend": str(base_config.get("storage_backend", "memory")),
            "namespace": f"test_{base_config.get('namespace', uuid.uuid4().hex[:8])!s}",
            "enable_caching": bool(base_config.get("enable_caching", True)),
            "cache_ttl_seconds": cast("int", base_config.get("cache_ttl", 300)),
        }
        # Apply overrides with type filtering
        storage_config.update({
            key: value
            for key, value in overrides.items()
            if isinstance(value, (str, int, bool))
        })
        return storage_config

    @staticmethod
    def create_storage(**overrides: object) -> FlextApiStorage:
        """Create FlextApiStorage using FlextTestsDomains config.

        Returns:
            FlextApiStorage: Configured storage instance.

        """
        config = FlextApiFactories.create_storage_config(**overrides)
        return FlextApiStorage(config)

    @staticmethod
    def create_request_data(**overrides: object) -> FlextApiTypes.ResponseDict:
        """Create HTTP request data using FlextTestsDomains - ABSOLUTE.

        Returns:
            FlextApiTypes.ResponseDict: Request data dictionary.

        """
        # Use FlextTestsDomains for payload structure
        payload_data = FlextTestsDomains.create_payload()

        base_request: FlextTypes.Dict = {
            "method": payload_data.get("method", "GET"),
            "url": payload_data.get("url", "https://httpbin.org/get"),
            "headers": payload_data.get(
                "headers",
                {"Content-Type": "application/json"},
            ),
            "params": payload_data.get("params", {}),
            "timeout": payload_data.get("timeout", 30.0),
            "request_id": str(uuid.uuid4()),
        }
        base_request.update(overrides)
        return base_request

    @staticmethod
    def create_response_data(**overrides: object) -> FlextApiTypes.ResponseDict:
        """Create HTTP response data using FlextTestsDomains - ABSOLUTE.

        Returns:
            FlextApiTypes.ResponseDict: Response data dictionary.

        """
        # Use FlextTestsDomains for API response structure
        api_response = FlextTestsDomains.api_response_data()

        response_data = {
            "status_code": 200,
            "data": api_response.get("data", {}),
            "headers": api_response.get(
                "headers",
                {"Content-Type": "application/json"},
            ),
            "elapsed_time": api_response.get("elapsed_time", 0.5),
            "request_id": str(api_response.get("request_id", str(uuid.uuid4()))),
            "from_cache": bool(api_response.get("from_cache", False)),
            "success": True,
        }
        # Update with overrides, ensuring type compatibility
        for key, value in overrides.items():
            if key in response_data and isinstance(
                value, (str, int, float, bool, dict, list)
            ):
                response_data[key] = value

        # Update success based on status code
        if "status_code" in overrides and isinstance(response_data["status_code"], int):
            response_data["success"] = 200 <= response_data["status_code"] < 400

        return response_data

    @staticmethod
    def create_user_data(**overrides: object) -> FlextApiTypes.ResponseDict:
        """Create user data using FlextTestsDomains - ABSOLUTE.

        Returns:
            FlextApiTypes.ResponseDict: User data dictionary.

        """
        user_data = FlextTestsDomains.create_user()
        user_data.update(overrides)
        return user_data

    @staticmethod
    def create_error_result(
        error_message: str = "Test error",
    ) -> FlextResult[FlextApiTypes.ResponseDict]:
        """Create error FlextResult using FlextTestsUtilities - ABSOLUTE.

        Returns:
            FlextResult[FlextApiTypes.ResponseDict]: Error result instance.

        """
        return cast(
            "FlextResult[FlextApiTypes.ResponseDict]",
            FlextTestsUtilities.create_test_result(success=False, error=error_message),
        )

    @staticmethod
    def create_success_result(
        data: FlextApiTypes.ResponseDict | None = None,
    ) -> FlextResult[FlextApiTypes.ResponseDict]:
        """Create success FlextResult using FlextTestsUtilities - ABSOLUTE.

        Returns:
            FlextResult[FlextApiTypes.ResponseDict]: Success result instance.

        """
        if data is None:
            data = {"success": True, "message": "Test operation successful"}
        return cast(
            "FlextResult[FlextApiTypes.ResponseDict]",
            FlextTestsUtilities.create_test_result(success=True, data=data),
        )

    @staticmethod
    def batch_request_data(count: int = 5) -> list[FlextApiTypes.ResponseDict]:
        """Create batch requests using FlextTestsUtilities - ABSOLUTE.

        Returns:
            list[FlextApiTypes.ResponseDict]: List of request data dictionaries.

        """
        return [FlextApiFactories.create_request_data() for _ in range(count)]

    @staticmethod
    def batch_response_data(count: int = 5) -> list[FlextApiTypes.ResponseDict]:
        """Create batch responses using FlextTestsUtilities - ABSOLUTE.

        Returns:
            list[FlextApiTypes.ResponseDict]: List of response data dictionaries.

        """
        return [FlextApiFactories.create_response_data() for _ in range(count)]

    @staticmethod
    def create_service_data(**overrides: object) -> FlextApiTypes.ResponseDict:
        """Create service data using FlextTestsDomains - ABSOLUTE.

        Returns:
            FlextApiTypes.ResponseDict: Service data dictionary.

        """
        service_data = FlextTestsDomains.create_service()
        service_data.update(overrides)
        return service_data

    @staticmethod
    def create_payload_data(**overrides: object) -> FlextApiTypes.ResponseDict:
        """Create payload data using FlextTestsDomains - ABSOLUTE.

        Returns:
            FlextApiTypes.ResponseDict: Payload data dictionary.

        """
        payload_data = FlextTestsDomains.create_payload()
        payload_data.update(overrides)
        return payload_data

    @staticmethod
    def create_configuration_data(
        **overrides: object,
    ) -> FlextApiTypes.ResponseDict:
        """Create configuration data using FlextTestsDomains - ABSOLUTE.

        Returns:
            FlextApiTypes.ResponseDict: Configuration data dictionary.

        """
        config_data = FlextTestsDomains.create_configuration()
        config_data.update(overrides)
        return config_data

    @staticmethod
    def batch_users(count: int = 5) -> list[FlextApiTypes.ResponseDict]:
        """Create batch users using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of user dictionaries.

        """
        return FlextTestsDomains.batch_users(count)

    @staticmethod
    def get_valid_email_cases() -> FlextTypes.StringList:
        """Get valid emails using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of valid email strings.

        """
        return FlextTestsDomains.valid_email_cases()

    @staticmethod
    def get_invalid_email_cases() -> FlextTypes.StringList:
        """Get invalid emails using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of invalid email strings.

        """
        return FlextTestsDomains.invalid_email_cases()

    @staticmethod
    def get_valid_ages() -> FlextTypes.IntList:
        """Get valid ages using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of valid age integers.

        """
        return FlextTestsDomains.valid_ages()

    @staticmethod
    def get_invalid_ages() -> FlextTypes.IntList:
        """Get invalid ages using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of invalid age integers.

        """
        return FlextTestsDomains.invalid_ages()

    @staticmethod
    def create_test_data(
        count: int = 10,
        prefix: str = "flext_api",
    ) -> list[FlextApiTypes.ResponseDict]:
        """Create test data using FlextTestsUtilities - ABSOLUTE.

        Returns:
            List of test data dictionaries.

        """
        return FlextTestsUtilities.create_test_data(size=count, prefix=prefix)

    @staticmethod
    def create_functional_service(
        service_type: str = "api",
        **config: object,
    ) -> object:
        """Create functional service using FlextTestsUtilities - ABSOLUTE.

        Returns:
            Functional service object.

        """
        return FlextTestsUtilities.functional_service(service_type, **config)

    @staticmethod
    def create_api_response(
        *,
        success: bool = True,
        data: object = None,
    ) -> FlextApiTypes.ResponseDict:
        """Create API response using FlextTestsUtilities - ABSOLUTE.

        Returns:
            API response dictionary.

        """
        return FlextTestsUtilities.create_api_response(success=success, data=data)


# NO BACKWARD COMPATIBILITY ALIASES - USE DIRECT CLASS ONLY:
# from tests.factories import FlextApiFactories
# FlextApiFactories.create_client()

__all__ = [
    "FlextApiFactories",
]
