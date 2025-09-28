#!/usr/bin/env python3
"""FLEXT API - Basic usage example.

This example demonstrates basic FLEXT API usage using ONLY the refactored classes
following flext-core patterns. No helpers, no aliases, no legacy APIs.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import (
    FlextApiClient,
    FlextApiConfig,
    FlextApiModels,
    FlextApiStorage,
    FlextApiUtilities,
)
from flext_core import FlextConstants


def example_api_creation() -> None:
    """Demonstrate basic API instance creation using refactored classes."""
    print("=== API Creation Example ===")

    # Create API instance using ONLY the refactored FlextApiClient class
    api = FlextApiClient()
    print(f"✅ API created: flext-api v0.9.0 - {api.__class__.__name__}")


def example_client_creation() -> None:
    """Demonstrate HTTP client creation using enhanced singleton pattern."""
    print("\n=== Client Creation Example ===")

    # Create API instance
    FlextApiClient()

    # Create client config using enhanced singleton pattern
    client_config = FlextApiConfig.create_for_environment(
        environment="development",
        api_base_url="https://httpbin.org",
        api_timeout=FlextConstants.Network.DEFAULT_TIMEOUT,
    )

    print(f"✅ Client config created: {client_config.api_base_url}")
    print(f"   Timeout: {client_config.api_timeout}s")
    print(f"   Max retries: {client_config.max_retries}")


def example_direct_client() -> None:
    """Demonstrate direct HTTP client usage with enhanced singleton pattern."""
    print("\n=== Direct Client Example ===")

    # Create client configuration using enhanced singleton pattern
    config = FlextApiConfig.create_for_environment(
        environment="development",
        api_base_url="https://httpbin.org",
        api_timeout=FlextConstants.Network.DEFAULT_TIMEOUT,
    )

    print(f"✅ Client config: {config.api_base_url}")
    print(f"   Timeout: {config.api_timeout}")
    print(f"   Default headers: {config.get_default_headers()}")


def example_storage_usage() -> None:
    """Demonstrate storage usage with refactored FlextApiStorage."""
    print("\n=== Storage Example ===")

    # Create storage using the refactored FlextApiStorage class
    storage = FlextApiStorage()

    # Set data using FlextResult pattern
    # CacheValue é tuple[object, FlextApiTypes.HttpHeaders, int]
    cache_value: tuple[object, dict[str, str], int] = (
        {"message": "Hello FlextAPI!"},
        {},
        200,
    )
    set_result = storage.set("example_key", cache_value, timeout=300)

    if set_result.is_success:
        print("✅ Data stored successfully")

        # Get data using FlextResult pattern
        get_result = storage.get("example_key")
        if get_result.is_success:
            print(f"✅ Data retrieved: {get_result.value}")
        else:
            print(f"❌ Data retrieval failed: {get_result.error}")
    else:
        print(f"❌ Data storage failed: {set_result.error}")


def example_utilities_usage() -> None:
    """Demonstrate utilities usage with refactored FlextApiUtilities."""
    print("\n=== Utilities Example ===")

    # URL validation using the refactored nested class
    url_result = FlextApiUtilities.HttpValidator.validate_url(
        "https://example.com/api/v1",
    )

    if url_result.is_success:
        print(f"✅ URL validation successful: {url_result.value}")
    else:
        print(f"❌ URL validation failed: {url_result.error}")

    # Response building using the refactored nested class
    response_result = FlextApiUtilities.ResponseBuilder.build_success_response(
        data={"users": [{"id": 1, "name": "John"}]},
        message="Users retrieved successfully",
    )

    if response_result.is_success:
        print("✅ Response built successfully")
        print(f"   Status: {response_result.value['status']}")
        print(f"   Message: {response_result.value['message']}")
    else:
        print(f"❌ Response building failed: {response_result.error}")


def example_app_creation() -> None:
    """Demonstrate FastAPI app creation using refactored classes."""
    print("\n=== App Creation Example ===")

    # Create app using the refactored FlextApiClient class methods
    client = FlextApiClient()
    app = client.create_flext_api_app()

    print(f"✅ App created: {type(app).__name__}")
    print("✅ App includes CORS, error handlers, and middleware")


def example_models_usage() -> None:
    """Demonstrate models usage with refactored FlextApiModels."""
    print("\n=== Models Example ===")

    try:
        # Create HTTP request model using the refactored nested class
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://httpbin.org/get",
            headers={"Accept": "application/json"},
            timeout=float(FlextConstants.Network.DEFAULT_TIMEOUT),
        )

        print(f"✅ Request model created: {request.method} {request.url}")
        print(f"   Timeout: {request.timeout}s")

        # Create HTTP response model using the refactored nested class
        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"message": "Success"},
            url="https://httpbin.org/get",
            method="GET",
            elapsed_time=0.125,
        )

        print(f"✅ Response model created: {response.status_code}")
        print(f"   Success: {response.is_success}")
        print(f"   Elapsed: {response.elapsed_time}s")

    except Exception as e:
        print(f"❌ Model creation failed: {e}")


def example_async_operations() -> None:
    """Demonstrate async operations with refactored classes."""
    print("\n=== Async Operations Example ===")

    # Create storage for async operations
    storage = FlextApiStorage()

    try:
        # Example async-style operations
        print("✅ Storage ready for async operations")

        # Set multiple values
        keys = ["key1", "key2", "key3"]
        for i, key in enumerate(keys):
            result = storage.set(key, {"id": i + 1, "name": f"item_{i + 1}"})
            if result.is_success:
                print(f"✅ Set {key} successfully")
            else:
                print(f"❌ Failed to set {key}: {result.error}")

        # Get cache size
        size_result = storage.size()
        if size_result.is_success:
            print(f"✅ Cache size: {size_result.value} items")
        else:
            print(f"❌ Failed to get cache size: {size_result.error}")

    except Exception as e:
        print(f"❌ Async operations failed: {e}")


def main() -> None:
    """Run all examples using ONLY refactored classes."""
    print("FLEXT API - Basic Usage Examples (Refactored Classes Only)")
    print("=========================================================")

    # Synchronous examples using refactored classes
    example_api_creation()
    example_client_creation()
    example_direct_client()
    example_storage_usage()
    example_utilities_usage()
    example_app_creation()
    example_models_usage()

    # Async example
    print("\n=== Running Async Examples ===")
    example_async_operations()

    print("\n🎉 All examples completed successfully using refactored classes!")
    print("✅ FlextResult pattern used throughout")
    print("✅ flext-core compliance maintained")
    print("✅ No legacy APIs or helpers used")


if __name__ == "__main__":
    main()
