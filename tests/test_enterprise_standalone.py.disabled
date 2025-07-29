#!/usr/bin/env python3
"""Standalone test for FlextApi Enterprise Patterns.

# Constants
DEFAULT_TTL = 600

Tests advanced enterprise patterns.on conftest.py
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from flext_api.helpers.flext_api_patterns import (
    FlextApiClientPool,
    FlextApiEnterpriseOrchestrator,
    FlextApiServiceDefinition,
    FlextApiSmartCache,
    flext_api_create_client_pool,
    flext_api_create_enterprise_orchestrator,
    flext_api_create_smart_cache,
)


async def test_enterprise_patterns() -> bool | None:  # noqa: C901, PLR0915
    """Test enterprise patterns functionality."""
    try:
        # Test 1: Smart Cache
        cache = FlextApiSmartCache(default_ttl=300)

        call_count = 0

        async def fetch_data() -> dict[str, str]:
            nonlocal call_count
            call_count += 1
            return {"data": f"call_{call_count}", "timestamp": call_count}

        # First call should fetch
        result1 = await cache.get_or_fetch("test_key", fetch_data)
        if result1["data"] != "call_1":
            msg = f"Expected call_1, got {result1['data']}"
            raise AssertionError(msg)
        assert call_count == 1

        # Second call should use cache
        result2 = await cache.get_or_fetch("test_key", fetch_data)
        if result2["data"] != "call_1":  # Same as first call
            msg = f"Expected call_1, got {result2['data']}"
            raise AssertionError(msg)
        assert call_count == 1  # No additional call

        stats = cache.get_cache_stats()
        if stats["total_entries"] != 1:
            msg = f"Expected 1, got {stats['total_entries']}"
            raise AssertionError(msg)

        # Test 2: Service Definitions
        service = FlextApiServiceDefinition(
            name="test-service",
            base_url="https://httpbin.org",
            health_endpoint="/status/200",
        )
        if service.name != "test-service":
            msg = f"Expected test-service, got {service.name}"
            raise AssertionError(msg)
        assert service.base_url == "https://httpbin.org"

        # Test 3: Enterprise Orchestrator
        services = [
            FlextApiServiceDefinition(
                name="test-service",
                base_url="https://httpbin.org",
                health_endpoint="/json",
            ),
        ]

        async with FlextApiEnterpriseOrchestrator(services) as orchestrator:
            # Test health check
            health = await orchestrator.health_check_all_services()
            if "overall_health" not in health:
                msg = f"Expected overall_health in {health}"
                raise AssertionError(msg)
            if health["total_count"] != 1:
                msg = f"Expected 1, got {health['total_count']}"
                raise AssertionError(msg)

        # Test 4: Client Pool
        async with FlextApiClientPool(
            base_url="https://httpbin.org",
            min_clients=1,
            max_clients=3,
        ) as pool:
            result = await pool.execute_request("GET", "/json")
            if "success" not in result:
                msg = f"Expected success in {result}"
                raise AssertionError(msg)
            assert "client_id" in result

        # Test 5: Factory Functions
        cache_factory = flext_api_create_smart_cache(ttl=600)
        if not isinstance(cache_factory, FlextApiSmartCache):
            msg = "Expected FlextApiSmartCache instance"
            raise AssertionError(msg)

        orchestrator_factory = flext_api_create_enterprise_orchestrator(services)
        if not isinstance(orchestrator_factory, FlextApiEnterpriseOrchestrator):
            msg = "Expected FlextApiEnterpriseOrchestrator instance"
            raise AssertionError(msg)

        pool_factory = flext_api_create_client_pool(
            base_url="https://httpbin.org",
            min_clients=2,
            max_clients=5,
        )
        if not isinstance(pool_factory, FlextApiClientPool):
            msg = "Expected FlextApiClientPool instance"
            raise AssertionError(msg)

        return True

    except Exception:
        traceback.print_exc()
        return False


async def main() -> None:
    """Main test runner."""

    success = await test_enterprise_patterns()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
