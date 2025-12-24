"""Test factories for flext-api tests.

This module provides factory functions for creating test data and objects.
Uses Python 3.13+ syntax for modern type system and code reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid

from faker import Faker
from flext_core import FlextResult, r
from flext_tests import FlextTestsDomains, u

from flext_api import FlextApiClient, FlextApiSettings, FlextApiStorage
from flext_api.typings import t as t_api

# Replace all t_api. with t_api. throughout this file

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
    def create_client_config(**overrides: object) -> t_api.ResponseDict:
        """Create client config using FlextTestsDomains - ABSOLUTE usage.

        Returns:
            t_api.ResponseDict: Client configuration dictionary.

        """
        # Use FlextTestsDomains for base configuration
        base_config = FlextTestsDomains.create_configuration()

        # Ensure required client fields with proper type narrowing
        base_url_val = base_config.get("base_url", "https://httpbin.org")
        timeout_val = base_config.get("timeout", 30.0)
        max_retries_val = base_config.get("max_retries", 3)
        headers_val = base_config.get("headers", {"User-Agent": "FlextAPI-Test/0.9.0"})

        client_config: dict[str, t_api.JsonValue] = {
            "base_url": str(base_url_val)
            if base_url_val is not None
            else "https://httpbin.org",
            "timeout": float(timeout_val)
            if isinstance(timeout_val, (int, float))
            else 30.0,
            "max_retries": int(max_retries_val)
            if isinstance(max_retries_val, (int, float))
            else 3,
            "headers": {
                k: str(v)
                for k, v in (
                    headers_val.items()
                    if isinstance(headers_val, dict)
                    else {"User-Agent": "FlextAPI-Test/0.9.0"}.items()
                )
            },
        }
        # Apply overrides with type filtering
        valid_overrides = {
            key: value
            for key, value in overrides.items()
            if isinstance(value, (str, int, float, bool, type(None)))
        }
        client_config.update(valid_overrides)

        return client_config

    @staticmethod
    def create_client(**overrides: object) -> FlextApiClient:
        """Create FlextApiClient using FlextTestsDomains config.

        Returns:
            FlextApiClient: Configured client instance.

        """
        config = FlextApiFactories.create_client_config(**overrides)
        # Create FlextApiSettings from dictionary values with proper type narrowing
        base_url_val = config.get("base_url", "https://httpbin.org")
        timeout_val = config.get("timeout", 30.0)
        max_retries_val = config.get("max_retries", 3)
        headers_val = config.get("headers", {})

        timeout_float = (
            float(timeout_val) if isinstance(timeout_val, (int, float, str)) else 30.0
        )
        max_retries_int = (
            int(max_retries_val)
            if isinstance(max_retries_val, (int, float, str))
            else 3
        )
        headers_dict = headers_val if isinstance(headers_val, dict) else {}

        api_config = FlextApiSettings(
            base_url=str(base_url_val)
            if base_url_val is not None
            else "https://httpbin.org",
            timeout=timeout_float,
            max_retries=max_retries_int,
            headers={
                k: str(v)
                for k, v in headers_dict.items()
                if isinstance(v, (str, int, float, bool))
            },
        )
        return FlextApiClient(config=api_config)

    @staticmethod
    def create_api_config(**overrides: object) -> FlextApiSettings:
        """Create FlextApiSettings using FlextTestsDomains - ABSOLUTE usage.

        Returns:
            FlextApiSettings: Configured API config instance.

        """
        # Use FlextTestsDomains for realistic configuration
        config_data = FlextTestsDomains.create_configuration()

        # Extract base URL and parse if needed
        base_url = str(config_data.get("base_url", "https://httpbin.org"))
        if "://" in base_url:
            base_url = base_url.split("://")[1].split(":")[0]

        # Build with type-safe defaults using proper type narrowing
        base_url_override = overrides.get("base_url")
        base_url_from_config = config_data.get("base_url", "https://httpbin.org")
        base_url_val = str(
            base_url_override
            if base_url_override is not None
            else base_url_from_config,
        )

        timeout_override = overrides.get("timeout")
        timeout_from_config = config_data.get("default_timeout", 30.0)
        timeout_raw = (
            timeout_override if timeout_override is not None else timeout_from_config
        )
        timeout_val = (
            float(timeout_raw) if isinstance(timeout_raw, (int, float, str)) else 30.0
        )

        max_retries_override = overrides.get("max_retries")
        max_retries_from_config = config_data.get("max_retries", 3)
        max_retries_raw = (
            max_retries_override
            if max_retries_override is not None
            else max_retries_from_config
        )
        max_retries_val = (
            int(max_retries_raw)
            if isinstance(max_retries_raw, (int, float, str))
            else 3
        )

        return FlextApiSettings(
            base_url=base_url_val,
            timeout=timeout_val,
            max_retries=max_retries_val,
        )

    @staticmethod
    def create_storage_config(**overrides: object) -> dict[str, str | int | bool]:
        """Create storage config using FlextTestsDomains.

        Returns:
            dict[str, str | int | bool]: Storage configuration dictionary.

        """
        # Use FlextTestsDomains for storage configuration
        base_config = FlextTestsDomains.create_configuration()

        cache_ttl_val = base_config.get("cache_ttl", 300)
        cache_ttl_int = (
            int(cache_ttl_val) if isinstance(cache_ttl_val, (int, float, str)) else 300
        )

        storage_config: dict[str, str | int | bool] = {
            "backend": str(base_config.get("storage_backend", "memory")),
            "namespace": f"test_{base_config.get('namespace', uuid.uuid4().hex[:8])!s}",
            "enable_caching": bool(base_config.get("enable_caching", True)),
            "cache_ttl_seconds": cache_ttl_int,
        }
        # Apply overrides with type filtering
        valid_overrides = {
            key: value
            for key, value in overrides.items()
            if isinstance(value, (str, int, bool))
        }
        storage_config.update(valid_overrides)
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
    def create_request_data(**overrides: object) -> t_api.ResponseDict:
        """Create HTTP request data using FlextTestsDomains - ABSOLUTE.

        Returns:
            t_api.ResponseDict: Request data dictionary.

        """
        # Use FlextTestsDomains for payload structure
        payload_data = FlextTestsDomains.create_payload()

        # Build request with proper type narrowing
        headers_val = payload_data.get("headers", {"Content-Type": "application/json"})
        headers_dict = (
            headers_val
            if isinstance(headers_val, dict)
            else {"Content-Type": "application/json"}
        )

        params_val = payload_data.get("params", {})
        params_dict = params_val if isinstance(params_val, dict) else {}

        timeout_val = payload_data.get("timeout", 30.0)
        timeout_float = (
            float(timeout_val) if isinstance(timeout_val, (int, float, str)) else 30.0
        )

        base_request: dict[str, t_api.JsonValue] = {
            "method": str(payload_data.get("method", "GET")),
            "url": str(payload_data.get("url", "https://httpbin.org/get")),
            "headers": {
                k: str(v) if not isinstance(v, list) else [str(item) for item in v]
                for k, v in headers_dict.items()
            },
            "params": params_dict,
            "timeout": timeout_float,
            "request_id": str(uuid.uuid4()),
        }
        # Apply overrides with type filtering
        for key, value in overrides.items():
            if isinstance(value, (str, int, float, bool, type(None), dict, list)):
                if isinstance(value, dict):
                    base_request[key] = {k: str(v) for k, v in value.items()}
                elif isinstance(value, list):
                    base_request[key] = [
                        str(item)
                        if not isinstance(item, (str, int, float, bool, type(None)))
                        else item
                        for item in value
                    ]
                else:
                    base_request[key] = value
        return base_request

    @staticmethod
    def create_response_data(**overrides: object) -> t_api.ResponseDict:
        """Create HTTP response data using FlextTestsDomains - ABSOLUTE.

        Returns:
            t_api.ResponseDict: Response data dictionary.

        """
        # Use FlextTestsDomains for API response structure
        api_response = FlextTestsDomains.api_response_data()

        # Build response with proper type narrowing
        data_val = api_response.get("data", {})
        data_dict: dict[str, t_api.JsonValue] = (
            dict(data_val.items()) if isinstance(data_val, dict) else {}
        )

        headers_val = api_response.get("headers", {"Content-Type": "application/json"})
        headers_dict = (
            headers_val
            if isinstance(headers_val, dict)
            else {"Content-Type": "application/json"}
        )

        elapsed_time_val = api_response.get("elapsed_time", 0.5)
        elapsed_time_float = (
            float(elapsed_time_val)
            if isinstance(elapsed_time_val, (int, float, str))
            else 0.5
        )

        request_id_val = api_response.get("request_id", str(uuid.uuid4()))
        request_id_str = (
            str(request_id_val) if request_id_val is not None else str(uuid.uuid4())
        )

        from_cache_val = api_response.get("from_cache", False)
        from_cache_bool = bool(from_cache_val) if from_cache_val is not None else False

        response_data: dict[str, t_api.JsonValue] = {
            "status_code": 200,
            "data": data_dict,
            "headers": {
                k: str(v) if not isinstance(v, list) else [str(item) for item in v]
                for k, v in headers_dict.items()
            },
            "elapsed_time": elapsed_time_float,
            "request_id": request_id_str,
            "from_cache": from_cache_bool,
            "success": True,
        }
        # Update with overrides, ensuring type compatibility
        for key, value in overrides.items():
            if isinstance(value, (str, int, float, bool, type(None), dict, list)):
                if isinstance(value, dict):
                    response_data[key] = {
                        k: str(v)
                        if not isinstance(v, (str, int, float, bool, type(None)))
                        else v
                        for k, v in value.items()
                    }
                elif isinstance(value, list):
                    response_data[key] = [
                        str(item)
                        if not isinstance(item, (str, int, float, bool, type(None)))
                        else item
                        for item in value
                    ]
                else:
                    response_data[key] = value

        # Update success based on status code
        status_code = response_data.get("status_code")
        if isinstance(status_code, int):
            http_ok = 200
            http_bad_request = 400
            response_data["success"] = http_ok <= status_code < http_bad_request

        return response_data

    @staticmethod
    def create_user_data(**overrides: object) -> t_api.ResponseDict:
        """Create user data using FlextTestsDomains - ABSOLUTE.

        Returns:
            t_api.ResponseDict: User data dictionary.

        """
        # Filter overrides to only str | bool as required by create_user
        valid_overrides: dict[str, str | bool] = {
            k: (str(v) if not isinstance(v, bool) else v)
            for k, v in overrides.items()
            if isinstance(v, (str, bool))
            or (isinstance(v, (int, float)) and k in ("active", "enabled"))
        }
        return FlextTestsDomains.create_user(**valid_overrides)

    @staticmethod
    def create_error_result(
        error_message: str = "Test error",
    ) -> FlextResult[t_api.ResponseDict]:
        """Create error FlextResult using FlextTestsUtilities - ABSOLUTE.

        Returns:
            FlextResult[t_api.ResponseDict]: Error result instance.

        """
        return r[t_api.ResponseDict].fail(error_message)

    @staticmethod
    def create_success_result(
        data: t_api.ResponseDict | None = None,
    ) -> FlextResult[t_api.ResponseDict]:
        """Create success FlextResult using FlextTestsUtilities - ABSOLUTE.

        Returns:
            FlextResult[t_api.ResponseDict]: Success result instance.

        """
        if data is None:
            data = {"success": True, "message": "Test operation successful"}
        return r[t_api.ResponseDict].ok(data)

    @staticmethod
    def batch_request_data(count: int = 5) -> list[t_api.ResponseDict]:
        """Create batch requests using FlextTestsUtilities - ABSOLUTE.

        Returns:
            list[t_api.ResponseDict]: List of request data dictionaries.

        """
        return [FlextApiFactories.create_request_data() for _ in range(count)]

    @staticmethod
    def batch_response_data(count: int = 5) -> list[t_api.ResponseDict]:
        """Create batch responses using FlextTestsUtilities - ABSOLUTE.

        Returns:
            list[t_api.ResponseDict]: List of response data dictionaries.

        """
        return [FlextApiFactories.create_response_data() for _ in range(count)]

    @staticmethod
    def create_service_data(**overrides: object) -> t_api.ResponseDict:
        """Create service data using FlextTestsDomains - ABSOLUTE.

        Returns:
            t_api.ResponseDict: Service data dictionary.

        """
        service_data = FlextTestsDomains.create_service()
        # Apply overrides with type filtering
        filtered_overrides: dict[str, t_api.JsonValue] = {
            k: v
            for k, v in overrides.items()
            if isinstance(v, (str, int, float, bool, type(None), dict, list))
        }
        result: dict[str, t_api.JsonValue] = {
            k: str(v)
            if not isinstance(v, (str, int, float, bool, type(None), dict, list))
            else v
            for k, v in {**service_data, **filtered_overrides}.items()
        }
        return result

    @staticmethod
    def create_payload_data(**overrides: object) -> t_api.ResponseDict:
        """Create payload data using FlextTestsDomains - ABSOLUTE.

        Returns:
            t_api.ResponseDict: Payload data dictionary.

        """
        payload_data = FlextTestsDomains.create_payload()
        # Apply overrides with type filtering
        filtered_overrides: dict[str, t_api.JsonValue] = {
            k: v
            for k, v in overrides.items()
            if isinstance(v, (str, int, float, bool, type(None), dict, list))
        }
        result: dict[str, t_api.JsonValue] = {
            k: str(v)
            if not isinstance(v, (str, int, float, bool, type(None), dict, list))
            else v
            for k, v in {**payload_data, **filtered_overrides}.items()
        }
        return result

    @staticmethod
    def create_configuration_data(
        **overrides: object,
    ) -> t_api.ResponseDict:
        """Create configuration data using FlextTestsDomains - ABSOLUTE.

        Returns:
            t_api.ResponseDict: Configuration data dictionary.

        """
        config_data = FlextTestsDomains.create_configuration()
        # Apply overrides with type filtering
        filtered_overrides: dict[str, t_api.JsonValue] = {
            k: v
            for k, v in overrides.items()
            if isinstance(v, (str, int, float, bool, type(None), dict, list))
        }
        result: dict[str, t_api.JsonValue] = {
            k: str(v)
            if not isinstance(v, (str, int, float, bool, type(None), dict, list))
            else v
            for k, v in {**config_data, **filtered_overrides}.items()
        }
        return result

    @staticmethod
    def batch_users(count: int = 5) -> list[t_api.ResponseDict]:
        """Create batch users using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of user dictionaries.

        """
        users = FlextTestsDomains.batch_users(count)
        # Convert to proper type
        return [
            {
                k: str(v)
                if not isinstance(v, (str, int, float, bool, type(None), dict, list))
                else v
                for k, v in user.items()
            }
            for user in users
        ]

    @staticmethod
    def get_valid_email_cases() -> list[str]:
        """Get valid emails using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of valid email strings.

        """
        cases = FlextTestsDomains.valid_email_cases()
        return [str(case) if not isinstance(case, str) else case for case in cases]

    @staticmethod
    def get_invalid_email_cases() -> list[str]:
        """Get invalid emails using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of invalid email strings.

        """
        cases = FlextTestsDomains.invalid_email_cases()
        # invalid_email_cases returns list[tuple[str, bool]], extract just the email strings
        return [str(email) for email, _is_valid in cases]

    @staticmethod
    def get_valid_ages() -> list[int]:
        """Get valid ages using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of valid age integers.

        """
        return FlextTestsDomains.valid_ages()

    @staticmethod
    def get_invalid_ages() -> list[int]:
        """Get invalid ages using FlextTestsDomains - ABSOLUTE.

        Returns:
            List of invalid age integers.

        """
        ages = FlextTestsDomains.invalid_ages()
        return [int(age) if isinstance(age, (int, float, str)) else 0 for age in ages]

    @staticmethod
    def create_test_data(
        count: int = 10,
        prefix: str = "flext_api",
    ) -> list[t_api.ResponseDict]:
        """Create test data using flext_tests API.

        Returns:
            List of test data dictionaries.

        """
        result: list[t_api.ResponseDict] = []
        for i in range(count):
            data = u.Tests.Factory.create_test_data(
                id=f"{prefix}_{i}",
                name=f"{prefix}_item_{i}",
                value=f"test_value_{i}",
            )
            # Convert ConfigurationDict to ResponseDict with proper type narrowing
            typed_data: dict[str, t_api.JsonValue] = {
                k: str(v)
                if not isinstance(v, (str, int, float, bool, type(None), dict, list))
                else v
                for k, v in data.items()
            }
            result.append(typed_data)
        return result

    @staticmethod
    def create_functional_service(
        service_type: str = "api",
        **config: object,
    ) -> object:
        """Create functional service using flext_tests API.

        Returns:
            Functional service object.

        """
        # Filter config to only valid types
        filtered_config = {
            k: v
            for k, v in config.items()
            if isinstance(v, (str, int, float, bool, type(None), dict, list))
        }
        return FlextTestsDomains.create_service(
            service_type=service_type,
            **filtered_config,
        )

    @staticmethod
    def create_api_response(
        *,
        success: bool = True,
        data: object = None,
    ) -> t_api.ResponseDict:
        """Create API response using flext_tests API.

        Returns:
            API response dictionary.

        """
        status = "success" if success else "error"
        response = FlextTestsDomains.api_response_data(
            status=status,
            include_data=data is not None,
        )
        if data is not None:
            # Convert data to JsonValue type
            if isinstance(data, (str, int, float, bool, type(None), dict, list)):
                response["data"] = data
            else:
                response["data"] = str(data)
        # Convert ConfigurationDict to ResponseDict with proper type narrowing
        result: dict[str, t_api.JsonValue] = {
            k: str(v)
            if not isinstance(v, (str, int, float, bool, type(None), dict, list))
            else v
            for k, v in response.items()
        }
        return result


# NO BACKWARD COMPATIBILITY ALIASES - USE DIRECT CLASS ONLY:
# from tests.factories import FlextApiFactories
# FlextApiFactories.create_client()

__all__ = [
    "FlextApiFactories",
]
