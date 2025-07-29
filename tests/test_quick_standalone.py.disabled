#!/usr/bin/env python3
"""Standalone test for FlextApi Quick Helpers.

Tests the massive code reduction helpers.on conftest.py
"""

import asyncio
import sys
import traceback

from flext_api.helpers.flext_api_quick import (
    FlextApiMicroserviceIntegrator,
    FlextApiResponseAggregator,
    flext_api_enterprise_client,
    flext_api_quick_bulk,
    flext_api_quick_get,
    flext_api_quick_post,
)

# Constants
HTTP_OK = 200
EXPECTED_BULK_SIZE = 2


async def test_quick_helpers() -> bool | None:  # noqa: C901, PLR0915
    """Test quick helpers functionality."""
    try:
        # Test 1: Quick GET
        result = await flext_api_quick_get("https://httpbin.org/json")
        if not result["success"]:
            msg = f"Expected True, got {result['success']}"
            raise AssertionError(msg)
        if result["status"] != HTTP_OK:
            msg = f"Expected {200}, got {result['status']}"
            raise AssertionError(msg)
        assert result["data"] is not None

        # Test 2: Quick POST
        test_data = {"name": "test", "value": 123}
        result = await flext_api_quick_post("https://httpbin.org/post", test_data)
        if not result["success"]:
            msg = f"Expected True, got {result['success']}"
            raise AssertionError(msg)
        if result["status"] != HTTP_OK:
            msg = f"Expected {200}, got {result['status']}"
            raise AssertionError(msg)
        assert result["data"]["json"]["name"] == "test"

        # Test 3: Bulk requests
        requests = [
            {"method": "GET", "url": "https://httpbin.org/json"},
            {"method": "GET", "url": "https://httpbin.org/uuid"},
        ]
        results = await flext_api_quick_bulk(requests)
        if len(results) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(results)}"
            raise AssertionError(msg)
        successful = sum(1 for r in results if r["success"])
        if successful < 1:  # At least one should succeed
            msg = f"Expected {successful} >= {1}"
            raise AssertionError(msg)

        # Test 4: Enterprise client creation
        client = flext_api_enterprise_client(
            "https://httpbin.org",
            enable_all_features=True,
        )
        if client.config.base_url != "https://httpbin.org":
            msg = f"Expected https://httpbin.org, got {client.config.base_url}"
            raise AssertionError(msg)
        if not client.config.cache_enabled:
            msg = f"Expected True, got {client.config.cache_enabled}"
            raise AssertionError(msg)

        # Test 5: Microservice integrator
        services = {"test": "https://httpbin.org"}
        async with FlextApiMicroserviceIntegrator(services) as integrator:
            result = await integrator.call_service("test", "/json")
            if not result["success"]:
                msg = f"Expected True, got {result['success']}"
                raise AssertionError(msg)

        # Test 6: Response aggregator
        requests = [
            {"method": "GET", "url": "/json", "key": "json_data"},
            {"method": "GET", "url": "/uuid", "key": "uuid_data"},
        ]
        result = await FlextApiResponseAggregator.aggregate_concurrent(
            requests,
            base_url="https://httpbin.org",
        )
        if not result["success"]:
            msg = f"Expected True, got {result['success']}"
            raise AssertionError(msg)
        if result["metadata"]["total_requests"] != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {result['metadata']['total_requests']}"
            raise AssertionError(msg)

        return True

    except Exception:
        traceback.print_exc()
        return False


async def main() -> None:
    """Main test runner."""

    success = await test_quick_helpers()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
