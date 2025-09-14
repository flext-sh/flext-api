"""Test factories for flext-api tests.

This module provides factory functions for creating test data and objects.
"""

from __future__ import annotations

import uuid
from typing import cast

from faker import Faker
from flext_core import FlextResult, FlextTypes
from flext_tests import FlextTestsDomains, FlextTestsUtilities

from flext_api import FlextApiClient, FlextApiConfig, FlextApiStorage

# MAXIMUM usage of flext_tests - use EM ABSOLUTO


# Configure Faker for consistent test data
fake = Faker()
Faker.seed(12345)


class FlextApiFactories:
    """Factory methods using flext_tests EM ABSOLUTO - NO local implementations."""

    @staticmethod
    def create_client_config(**overrides: object) -> FlextTypes.Core.Dict:
        """Create client config using FlextTestsDomains - ABSOLUTE usage."""
        # Use FlextTestsDomains for base configuration
        base_config = FlextTestsDomains.create_configuration()

        # Ensure required client fields
        client_config = {
            "base_url": str(base_config.get("base_url", "https://httpbin.org")),
            "timeout": cast("float", base_config.get("timeout", 30.0)),
            "max_retries": cast("int", base_config.get("max_retries", 3)),
            "headers": base_config.get(
                "headers", {"User-Agent": "FlextAPI-Test/0.9.0"}
            ),
        }
        client_config.update(overrides)
        return client_config

    @staticmethod
    def create_client(**overrides: object) -> FlextApiClient:
        """Create FlextApiClient using FlextTestsDomains config."""
        config = FlextApiFactories.create_client_config(**overrides)
        return FlextApiClient(
            base_url=str(config["base_url"]),
            timeout=cast("float", config["timeout"]),
            max_retries=cast("int", config["max_retries"]),
            headers=config.get("headers", {}),
        )

    @staticmethod
    def create_api_config(**overrides: object) -> FlextApiConfig:
        """Create FlextApiConfig using FlextTestsDomains - ABSOLUTE usage."""
        # Use FlextTestsDomains for realistic configuration
        config_data = FlextTestsDomains.create_configuration()

        # Build with type-safe defaults
        defaults = {
            "api_host": str(config_data.get("host", "127.0.0.1")),
            "api_port": cast("int", config_data.get("port", 8000)),
            "api_base_url": str(config_data.get("base_url", "https://httpbin.org")),
            "api_timeout": cast("float", config_data.get("default_timeout", 30.0)),
            "max_retries": cast("int", config_data.get("max_retries", 3)),
        }

        # Apply overrides safely
        for key, value in overrides.items():
            if key in defaults:
                defaults[key] = value

        return FlextApiConfig(
            api_host=cast("str", defaults["api_host"]),
            api_port=cast("int", defaults["api_port"]),
            api_base_url=cast("str", defaults["api_base_url"]),
            api_timeout=cast("float", defaults["api_timeout"]),
            max_retries=cast("int", defaults["max_retries"]),
        )

    @staticmethod
    def create_storage_config(**overrides: object) -> FlextTypes.Core.Dict:
        """Create storage config using FlextTestsDomains."""
        # Use FlextTestsDomains for storage configuration
        base_config = FlextTestsDomains.create_configuration()

        storage_config = {
            "backend": str(base_config.get("storage_backend", "memory")),
            "namespace": f"test_{base_config.get('namespace', uuid.uuid4().hex[:8])!s}",
            "enable_caching": bool(base_config.get("enable_caching", True)),
            "cache_ttl_seconds": cast("int", base_config.get("cache_ttl", 300)),
        }
        storage_config.update(overrides)
        return storage_config

    @staticmethod
    def create_storage(**overrides: object) -> FlextApiStorage:
        """Create FlextApiStorage using FlextTestsDomains config."""
        config = FlextApiFactories.create_storage_config(**overrides)
        return FlextApiStorage(config)

    @staticmethod
    def create_request_data(**overrides: object) -> FlextTypes.Core.Dict:
        """Create HTTP request data using FlextTestsDomains - ABSOLUTE."""
        # Use FlextTestsDomains for payload structure
        payload_data = FlextTestsDomains.create_payload()

        base_request = {
            "method": str(payload_data.get("method", "GET")),
            "url": str(payload_data.get("url", "https://httpbin.org/get")),
            "headers": payload_data.get(
                "headers", {"Content-Type": "application/json"}
            ),
            "params": payload_data.get("params", {}),
            "timeout": cast("float", payload_data.get("timeout", 30.0)),
            "request_id": str(uuid.uuid4()),
        }
        base_request.update(overrides)
        return base_request

    @staticmethod
    def create_response_data(**overrides: object) -> FlextTypes.Core.Dict:
        """Create HTTP response data using FlextTestsDomains - ABSOLUTE."""
        # Use FlextTestsDomains for API response structure
        api_response = FlextTestsDomains.api_response_data()

        response_data = {
            "status_code": 200,
            "data": api_response.get("data", {}),
            "headers": api_response.get(
                "headers", {"Content-Type": "application/json"}
            ),
            "elapsed_time": cast("float", api_response.get("elapsed_time", 0.5)),
            "request_id": str(api_response.get("request_id", str(uuid.uuid4()))),
            "from_cache": bool(api_response.get("from_cache", False)),
            "success": True,
        }
        response_data.update(overrides)

        # Update success based on status code
        if "status_code" in overrides and isinstance(response_data["status_code"], int):
            response_data["success"] = 200 <= response_data["status_code"] < 400

        return response_data

    @staticmethod
    def create_user_data(**overrides: object) -> FlextTypes.Core.Dict:
        """Create user data using FlextTestsDomains - ABSOLUTE."""
        user_data = FlextTestsDomains.create_user()
        user_data.update(overrides)
        return user_data

    @staticmethod
    def create_error_result(
        error_message: str = "Test error",
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Create error FlextResult using FlextTestsUtilities - ABSOLUTE."""
        return cast(
            "FlextResult[FlextTypes.Core.Dict]",
            FlextTestsUtilities.create_test_result(success=False, error=error_message),
        )

    @staticmethod
    def create_success_result(
        data: FlextTypes.Core.Dict | None = None,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Create success FlextResult using FlextTestsUtilities - ABSOLUTE."""
        if data is None:
            data = {"success": True, "message": "Test operation successful"}
        return cast(
            "FlextResult[FlextTypes.Core.Dict]",
            FlextTestsUtilities.create_test_result(success=True, data=data),
        )

    @staticmethod
    def batch_request_data(count: int = 5) -> list[FlextTypes.Core.Dict]:
        """Create batch requests using FlextTestsUtilities - ABSOLUTE."""
        return [FlextApiFactories.create_request_data() for _ in range(count)]

    @staticmethod
    def batch_response_data(count: int = 5) -> list[FlextTypes.Core.Dict]:
        """Create batch responses using FlextTestsUtilities - ABSOLUTE."""
        return [FlextApiFactories.create_response_data() for _ in range(count)]

    @staticmethod
    def create_service_data(**overrides: object) -> FlextTypes.Core.Dict:
        """Create service data using FlextTestsDomains - ABSOLUTE."""
        service_data = FlextTestsDomains.create_service()
        service_data.update(overrides)
        return service_data

    @staticmethod
    def create_payload_data(**overrides: object) -> FlextTypes.Core.Dict:
        """Create payload data using FlextTestsDomains - ABSOLUTE."""
        payload_data = FlextTestsDomains.create_payload()
        payload_data.update(overrides)
        return payload_data

    @staticmethod
    def create_configuration_data(**overrides: object) -> FlextTypes.Core.Dict:
        """Create configuration data using FlextTestsDomains - ABSOLUTE."""
        config_data = FlextTestsDomains.create_configuration()
        config_data.update(overrides)
        return config_data

    @staticmethod
    def batch_users(count: int = 5) -> list[FlextTypes.Core.Dict]:
        """Create batch users using FlextTestsDomains - ABSOLUTE."""
        return FlextTestsDomains.batch_users(count)

    @staticmethod
    def get_valid_email_cases() -> list[str]:
        """Get valid emails using FlextTestsDomains - ABSOLUTE."""
        return FlextTestsDomains.valid_email_cases()

    @staticmethod
    def get_invalid_email_cases() -> list[str]:
        """Get invalid emails using FlextTestsDomains - ABSOLUTE."""
        return FlextTestsDomains.invalid_email_cases()

    @staticmethod
    def get_valid_ages() -> list[int]:
        """Get valid ages using FlextTestsDomains - ABSOLUTE."""
        return FlextTestsDomains.valid_ages()

    @staticmethod
    def get_invalid_ages() -> list[int]:
        """Get invalid ages using FlextTestsDomains - ABSOLUTE."""
        return FlextTestsDomains.invalid_ages()

    @staticmethod
    def create_test_data(
        count: int = 10, prefix: str = "flext_api"
    ) -> list[FlextTypes.Core.Dict]:
        """Create test data using FlextTestsUtilities - ABSOLUTE."""
        return FlextTestsUtilities.create_test_data(size=count, prefix=prefix)

    @staticmethod
    def create_functional_service(
        service_type: str = "api", **config: object
    ) -> object:
        """Create functional service using FlextTestsUtilities - ABSOLUTE."""
        return FlextTestsUtilities.functional_service(service_type, **config)

    @staticmethod
    def create_api_response(
        *, success: bool = True, data: object = None
    ) -> FlextTypes.Core.Dict:
        """Create API response using FlextTestsUtilities - ABSOLUTE."""
        return FlextTestsUtilities.create_api_response(success=success, data=data)


# NO BACKWARD COMPATIBILITY ALIASES - USE DIRECT CLASS ONLY:
# from tests.factories import FlextApiFactories
# FlextApiFactories.create_client()

__all__ = [
    "FlextApiFactories",
]
