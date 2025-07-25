#!/usr/bin/env python3
"""Standalone test for FlextApi Quick Helpers.

Tests the massive code reduction helpers without dependencies on conftest.py
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_quick_helpers() -> bool | None:
    """Test quick helpers functionality."""
    try:
        from flext_api.helpers.flext_api_quick import (
            FlextApiMicroserviceIntegrator,
            FlextApiResponseAggregator,
            flext_api_enterprise_client,
            flext_api_quick_bulk,
            flext_api_quick_get,
            flext_api_quick_post,
        )

        # Test 1: Quick GET
        result = await flext_api_quick_get("https://httpbin.org/json")
        assert result["success"] is True
        assert result["status"] == 200
        assert result["data"] is not None

        # Test 2: Quick POST
        test_data = {"name": "test", "value": 123}
        result = await flext_api_quick_post("https://httpbin.org/post", test_data)
        assert result["success"] is True
        assert result["status"] == 200
        assert result["data"]["json"]["name"] == "test"

        # Test 3: Bulk requests
        requests = [
            {"method": "GET", "url": "https://httpbin.org/json"},
            {"method": "GET", "url": "https://httpbin.org/uuid"},
        ]
        results = await flext_api_quick_bulk(requests)
        assert len(results) == 2
        successful = sum(1 for r in results if r["success"])
        assert successful >= 1  # At least one should succeed

        # Test 4: Enterprise client creation
        client = flext_api_enterprise_client(
            "https://httpbin.org",
            enable_all_features=True
        )
        assert client.config.base_url == "https://httpbin.org"
        assert client.config.cache_enabled is True

        # Test 5: Microservice integrator
        services = {"test": "https://httpbin.org"}
        async with FlextApiMicroserviceIntegrator(services) as integrator:
            result = await integrator.call_service("test", "/json")
            assert result["success"] is True

        # Test 6: Response aggregator
        requests = [
            {"method": "GET", "url": "/json", "key": "json_data"},
            {"method": "GET", "url": "/uuid", "key": "uuid_data"},
        ]
        result = await FlextApiResponseAggregator.aggregate_concurrent(
            requests, base_url="https://httpbin.org"
        )
        assert result["success"] is True
        assert result["metadata"]["total_requests"] == 2

        return True

    except Exception:
        traceback.print_exc()
        return False

async def test_massive_code_reduction() -> bool | None:
    """Demonstrate massive code reduction examples."""
    try:
        from flext_api.helpers.flext_api_quick import (
            FlextApiMicroserviceIntegrator,
            flext_api_enterprise_client,
            flext_api_quick_get,
        )

        # Example 1: Traditional approach vs FlextApi


        # Actually test it
        await flext_api_quick_get("https://httpbin.org/json")

        # Example 2: Microservice integration

        services = {"service1": "https://httpbin.org", "service2": "https://httpbin.org"}
        async with FlextApiMicroserviceIntegrator(services) as integrator:
            # Multiple service calls with 1 line
            calls = [
                {"service": "service1", "endpoint": "/json"},
                {"service": "service2", "endpoint": "/uuid"},
            ]
            results = await integrator.call_multiple_services(calls)
            sum(1 for r in results if not isinstance(r, Exception) and r.get("success"))


        return True

    except Exception:
        return False

async def main() -> bool:
    """Run all tests and demonstrations."""
    # Run functionality tests
    test_success = await test_quick_helpers()

    if test_success:
        # Run code reduction demonstration
        demo_success = await test_massive_code_reduction()

        if demo_success:
            return True

    return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
