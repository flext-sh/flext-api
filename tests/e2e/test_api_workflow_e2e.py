"""End-to-end tests for complete API workflows.

Tests the full FlextApi workflow from initialization to HTTP client operations.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

import pytest

from flext_api import (
    FlextApi,
    FlextApiBuilder,
    FlextApiCachingPlugin,
    FlextApiClientResponse,
    FlextApiRetryPlugin,
    build_query,
    build_success_response,
    create_flext_api,
)


@pytest.mark.e2e
class TestApiWorkflowE2E:
    """End-to-end tests for complete API workflows."""

    @pytest.mark.asyncio
    async def test_complete_api_workflow(self) -> None:
        """Test complete workflow from API creation to HTTP operations."""
        # 1. Create API instance
        api = create_flext_api()
        assert api is not None

        # 2. Build query using builder patterns
        query = build_query({"status": "active", "limit": 10})
        assert query.filters[0]["field"] == "status"
        assert query.filters[0]["value"] == "active"

        # 3. Build response using builder patterns
        response_data = {"items": [{"id": 1, "name": "test"}], "total": 1}
        response = build_success_response(
            data=response_data,
            message="Data retrieved successfully",
        )
        assert response.success is True
        assert isinstance(response.data, dict)
        assert response.data["total"] == 1

        # 4. Create HTTP client using modern API
        client_result = api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 10.0,
            },
        )
        assert client_result.success

        client = client_result.value

        try:
            # 5. Perform HTTP operations
            get_result = await client.get("/get", params=query.to_dict())
            assert get_result.success

            # 6. Verify response structure
            assert get_result.value is not None
            http_response = cast("FlextApiClientResponse", get_result.value)
            assert http_response.status_code == 200
            assert isinstance(http_response.data, dict)

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self) -> None:
        """Test complete error handling workflow."""
        api = FlextApi()

        # Test client creation with invalid config using modern API
        invalid_result = api.create_client(
            {
                "base_url": "invalid-url-format",
            },
        )
        assert not invalid_result.success
        assert invalid_result.error is not None
        assert "Invalid URL format" in invalid_result.error

        # Test with valid config but unreachable URL using modern API
        client_result = api.create_client(
            {
                "base_url": "https://nonexistent-domain-12345.com",
                "timeout": 2.0,
            },
        )
        assert client_result.success

        client = client_result.value

        try:
            # This should fail gracefully
            result = await client.get("/test")
            assert not result.success
            assert result.error is not None
            assert "Request failed:" in result.error

        finally:
            await client.close()

    def test_builder_patterns_integration(self) -> None:
        """Test integration between different builder patterns."""
        # Query building

        builder = FlextApiBuilder()
        query = (
            builder.for_query()
            .equals("status", "published")
            .greater_than("created_at", "2024-01-01")
            .sort_desc("updated_at")
            .page(2)
            .page_size(25)
            .build()
        )

        assert len(query.filters) == 2
        assert len(query.sorts) == 1
        assert query.page == 2
        assert query.page_size == 25

        # Response building with pagination
        response = (
            builder.for_response()
            .success(data={"items": list(range(25))})
            .with_pagination(total=100, page=2, page_size=25)
            .with_metadata("query_time", "0.042s")
            .build()
        )

        assert response.success is True
        assert response.pagination is not None
        assert response.pagination["total"] == 100
        assert response.pagination["has_next"] is True
        assert response.pagination["has_previous"] is True
        assert response.metadata["query_time"] == "0.042s"

    @pytest.mark.asyncio
    async def test_plugin_system_integration(self) -> None:
        """Test plugin system integration across the API."""
        api = FlextApi()

        # Create client with multiple plugins
        plugins = [
            FlextApiCachingPlugin(ttl=120, max_size=50),
            FlextApiRetryPlugin(max_retries=3, delay=2.0),
        ]

        # This would typically use create_client_with_plugins
        # but we'll test the basic client creation using modern API
        client_result = api.create_client(
            {
                "base_url": "https://httpbin.org",
                "timeout": 5.0,
            },
        )
        assert client_result.success

        client = client_result.value

        # Add plugins manually for testing
        client.plugins.extend(plugins)

        try:
            # Test that plugins are properly configured
            assert len(client.plugins) == 2
            assert isinstance(client.plugins[0], FlextApiCachingPlugin)
            assert isinstance(client.plugins[1], FlextApiRetryPlugin)

            # Test actual request with plugins
            result = await client.get("/delay/1")
            if result.success:
                assert result.value is not None
                response = cast("FlextApiClientResponse", result.value)
                assert response.status_code == 200

        finally:
            await client.close()


# Global API instance for builder tests
api = FlextApi()
