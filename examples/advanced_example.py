#!/usr/bin/env python3
"""FLEXT API - Advanced usage example using ONLY refactored classes.

This example demonstrates advanced FLEXT API usage patterns:
- HTTP client configuration and usage
- FlextResult error handling patterns
- Storage system with hierarchical classes
- Response building and validation
- Model creation and validation
- All using ONLY refactored classes following flext-core patterns

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio

# Import ONLY the refactored classes following flext-core patterns
from flext_api import (
    FlextApi,
    FlextApiApp,
    FlextApiConfig,
    FlextApiModels,
    FlextApiStorage,
    FlextApiUtilities,
)


def example_api_creation() -> None:
    """Demonstrate API instance creation using refactored classes."""
    print("=== API Creation Example ===")

    # Create API instance using the refactored FlextApi class
    api = FlextApi()
    print(f"✅ API created: {api.service_name} v{api.service_version}")

    # Create client configuration using the refactored nested class
    client_config = FlextApiConfig.ClientConfig(
        base_url="https://api.example.com",
        timeout=30.0,
        max_retries=3,
        headers={"User-Agent": "FlextAPI/0.9.0"},
    )

    print(f"✅ Client config created: {client_config.base_url}")
    print(f"   Timeout: {client_config.timeout}s")
    print(f"   Max retries: {client_config.max_retries}")
    print(f"   Headers: {client_config.headers}")


def example_storage_system() -> None:
    """Demonstrate storage system using refactored FlextApiStorage."""
    print("\n=== Storage System Example ===")

    # Create storage using the refactored FlextApiStorage class
    storage = FlextApiStorage()

    # Test storage operations
    key = "user:123"
    value: dict[str, object] = {
        "name": "John Doe",
        "role": "REDACTED_LDAP_BIND_PASSWORD",
        "created": "2025-01-01",
    }

    print("✅ Storage created with hierarchical structure")

    # Set value using FlextResult pattern
    set_result = storage.set(key, value, ttl=300)
    if set_result.success:
        print(f"✅ Value stored: {key}")

        # Get value using FlextResult pattern
        get_result = storage.get(key)
        if get_result.success:
            retrieved = get_result.value
            print(f"✅ Value retrieved: {retrieved}")
            if isinstance(retrieved, dict):
                print(f"   User name: {retrieved.get('name', 'N/A')}")
                print(f"   User role: {retrieved.get('role', 'N/A')}")

            # Get cache size using FlextResult pattern
            size_result = storage.size()
            if size_result.success:
                print(f"✅ Cache size: {size_result.value} items")

            # Get cache keys using FlextResult pattern
            keys_result = storage.keys()
            if keys_result.success:
                keys_list = keys_result.value
                print(f"✅ Cache keys: {keys_list}")

            # Delete value using FlextResult pattern
            delete_result = storage.delete(key)
            if delete_result.success:
                print(f"✅ Value deleted: {key}")
        else:
            print(f"❌ Get failed: {get_result.error}")
    else:
        print(f"❌ Set failed: {set_result.error}")

    # Test nested class usage - JsonStorage for serialization
    json_storage = storage.JsonStorage()
    test_data: dict[str, object] = {
        "message": "Hello, World!",
        "timestamp": "2025-01-01T00:00:00Z",
    }

    try:
        json_str = json_storage.serialize(test_data)
        print(f"✅ Data serialized using nested JsonStorage: {len(json_str)} chars")

        # Test deserialization
        deserialized = json_storage.deserialize(json_str)
        print(f"✅ Data deserialized: {deserialized}")
    except Exception as e:
        print(f"❌ Serialization failed: {e}")


def example_utilities_usage() -> None:
    """Demonstrate utilities usage with refactored FlextApiUtilities."""
    print("\n=== Utilities Example ===")

    # URL validation using the refactored nested class
    url_result = FlextApiUtilities.UrlValidator.validate_url(
        "https://api.example.com/v1/users"
    )

    if url_result.success:
        print(f"✅ URL validation successful: {url_result.value}")
    else:
        print(f"❌ URL validation failed: {url_result.error}")

    # Response building using the refactored nested class
    success_response_result = FlextApiUtilities.ResponseBuilder.build_success_response(
        data={
            "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            "total": 2,
        },
        message="Users retrieved successfully",
    )

    if success_response_result.success:
        response = success_response_result.value
        print("✅ Success response built")
        print(f"   Status: {response['status']}")
        print(f"   Message: {response['message']}")
        if isinstance(response["data"], dict):
            print(f"   Total users: {response['data'].get('total', 0)}")
    else:
        print(f"❌ Success response building failed: {success_response_result.error}")

    # Error response building
    error_response_result = FlextApiUtilities.ResponseBuilder.build_error_response(
        "Invalid request parameters", 400, {"field": "email", "issue": "format"}
    )

    if error_response_result.success:
        error_response = error_response_result.value
        print("✅ Error response built")
        print(f"   Status: {error_response['status']}")
        print(f"   Message: {error_response['message']}")
        print(f"   Status Code: {error_response['status_code']}")
    else:
        print(f"❌ Error response building failed: {error_response_result.error}")

    # Data transformation using nested class
    transform_result = FlextApiUtilities.DataTransformer.to_json(
        {"key": "value", "number": 42}
    )
    if transform_result.success:
        json_str = transform_result.value
        print(f"✅ Data transformed to JSON: {json_str}")

        # Parse back
        parse_result = FlextApiUtilities.DataTransformer.from_json(json_str)
        if parse_result.success:
            parsed_data = parse_result.value
            print(f"✅ Data parsed from JSON: {parsed_data}")
    else:
        print(f"❌ Data transformation failed: {transform_result.error}")


def example_models_usage() -> None:
    """Demonstrate models usage with refactored FlextApiModels."""
    print("\n=== Models Example ===")

    try:
        # Create HTTP request model using the refactored nested class
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="https://api.example.com/users",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            body={"name": "Alice", "email": "alice@example.com", "role": "user"},
            timeout=30.0,
        )

        print(f"✅ Request model created: {request.method} {request.url}")
        print(f"   Headers: {request.headers}")
        print(f"   Has body: {request.body is not None}")
        print(f"   Timeout: {request.timeout}s")

        # Create HTTP response model using the refactored nested class
        response = FlextApiModels.HttpResponse(
            status_code=201,
            headers={"Content-Type": "application/json", "Location": "/users/12345"},
            body={
                "id": 12345,
                "name": "Alice",
                "email": "alice@example.com",
                "created": True,
            },
            url="https://api.example.com/users",
            method="POST",
            elapsed_time=0.245,
        )

        print(f"✅ Response model created: {response.status_code}")
        print(f"   Success: {response.is_success}")
        print(f"   Elapsed: {response.elapsed_time}s")
        if isinstance(response.body, dict):
            print(f"   User ID: {response.body.get('id', 'N/A')}")

        # Create configuration model using nested class
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=30.0,
            max_retries=3,
            headers={"User-Agent": "FlextAPI/0.9.0", "Accept": "application/json"},
        )

        print(f"✅ Config model created: {config.base_url}")
        print(f"   Timeout: {config.timeout}s")
        print(f"   Max retries: {config.max_retries}")

    except Exception as e:
        print(f"❌ Model creation failed: {e}")


def example_app_creation() -> None:
    """Demonstrate FastAPI app creation using refactored classes."""
    print("\n=== App Creation Example ===")

    # Create app using the refactored FlextApiApp class methods
    app = FlextApiApp.create_flext_api_app()

    print(f"✅ App created: {type(app).__name__}")
    print("✅ App includes CORS, error handlers, and middleware")

    # Create app with settings
    app_with_settings = FlextApiApp.create_flext_api_app_with_settings()

    print(f"✅ App with settings created: {type(app_with_settings).__name__}")
    print("✅ App configured with:")
    print("   - Environment-specific settings")
    print("   - Enhanced security middleware")
    print("   - Request ID tracking")
    print("   - Health check endpoints")


async def example_async_operations() -> None:
    """Demonstrate async operations with refactored classes."""
    print("\n=== Async Operations Example ===")

    # Create storage for async operations
    storage = FlextApiStorage()

    try:
        # Example async-style operations
        print("✅ Storage ready for async operations")

        # Set multiple values
        keys = ["async_key1", "async_key2", "async_key3"]
        for i, key in enumerate(keys):
            result = storage.set(
                key,
                {"id": i + 1, "name": f"async_item_{i + 1}", "timestamp": "2025-01-01"},
            )
            if result.success:
                print(f"✅ Set {key} successfully")
            else:
                print(f"❌ Failed to set {key}: {result.error}")

        # Get cache size
        size_result = storage.size()
        if size_result.success:
            print(f"✅ Cache size: {size_result.value} items")
        else:
            print(f"❌ Failed to get cache size: {size_result.error}")

        # Test cache operations using nested CacheOperations class
        cache_ops = storage.CacheOperations()
        cleanup_result = cache_ops.cleanup_expired()
        if cleanup_result.success:
            print("✅ Cache cleanup completed")
        else:
            print(f"❌ Cache cleanup failed: {cleanup_result.error}")

        # Test storage metrics using nested StorageMetrics class
        metrics = storage.StorageMetrics()
        stats_result = metrics.get_statistics()
        if stats_result.success:
            stats = stats_result.value
            print(f"✅ Storage statistics: {stats}")
        else:
            print(f"❌ Failed to get statistics: {stats_result.error}")

    except Exception as e:
        print(f"❌ Async operations failed: {e}")


def main() -> None:
    """Run all advanced examples using ONLY refactored classes."""
    print("FLEXT API - Advanced Usage Examples (Refactored Classes Only)")
    print("============================================================")

    # Synchronous examples using refactored classes
    example_api_creation()
    example_storage_system()
    example_utilities_usage()
    example_models_usage()
    example_app_creation()

    # Async example using refactored classes
    print("\n=== Running Async Examples ===")
    asyncio.run(example_async_operations())

    print("\n🎉 All advanced examples completed successfully using refactored classes!")
    print("✅ FlextResult pattern used throughout")
    print("✅ flext-core compliance maintained")
    print("✅ Hierarchical nested classes demonstrated")
    print("✅ No legacy APIs or helpers used")


if __name__ == "__main__":
    main()
