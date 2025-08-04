"""Functional examples tests for flext-api.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApi,
    FlextApiClient,
    FlextApiClientConfig,
    build_query,
    build_query_dict,
    build_success_response,
    create_flext_api,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestFunctionalExamples:
    """Functional examples showing real usage patterns."""

    def test_complete_api_workflow(self) -> None:
        """Test complete API workflow from creation to usage."""
        # Create API instance
        api = create_flext_api()
        assert api is not None

        # Build a query (returns structured query object)
        query = build_query({"status": "active", "limit": 10})
        query_dict = query.to_dict()
        if "filters" not in query_dict:
            raise AssertionError(f"Expected filters in {query_dict}")
        filters = query_dict["filters"]
        assert isinstance(filters, list), f"Expected list, got {type(filters)}"
        if len(filters) != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected 2, got {len(filters)}")

        # Create client configuration
        client_config = {"base_url": "https://api.example.com", "timeout": 30}
        client_result = api.flext_api_create_client(client_config)

        # Should succeed
        assert client_result.success
        assert client_result.data is not None

    def test_client_configuration_examples(self) -> None:
        """Test various client configuration examples."""
        # Minimal configuration
        config1 = FlextApiClientConfig(base_url="https://api.example.com")
        client1 = FlextApiClient(config1)
        if client1.config.base_url != "https://api.example.com":
            raise AssertionError(
                f"Expected https://api.example.com, got {client1.config.base_url}"
            )
        assert client1.config.timeout == 30.0  # Default value

        # Full configuration
        config2 = FlextApiClientConfig(
            base_url="https://api.example.com",
            timeout=60.0,
            headers={"Authorization": "Bearer token123"},
            max_retries=5,
        )
        client2 = FlextApiClient(config2)
        if client2.config.timeout != 60.0:
            raise AssertionError(f"Expected 60.0, got {client2.config.timeout}")
        assert client2.config.headers == {"Authorization": "Bearer token123"}
        if client2.config.max_retries != 5:
            raise AssertionError(f"Expected 5, got {client2.config.max_retries}")

    def test_query_building_examples(self) -> None:
        """Test various query building examples."""
        # Simple query
        query1 = build_query_dict({"name": "test"})
        if "filters" not in query1:
            raise AssertionError(f"Expected filters in {query1}")
        filters1 = query1["filters"]
        assert isinstance(filters1, list), f"Expected list, got {type(filters1)}"
        if len(filters1) != 1:
            raise AssertionError(f"Expected 1, got {len(filters1)}")
        assert isinstance(filters1[0], dict), f"Expected dict, got {type(filters1[0])}"
        assert filters1[0]["field"] == "name"

        # Complex query with multiple filters
        query2 = build_query_dict(
            {
                "status": "active",
                "created_after": "2023-01-01",
                "limit": 50,
                "sort": "name",
            }
        )
        if "filters" not in query2:
            raise AssertionError(f"Expected filters in {query2}")
        filters2 = query2["filters"]
        assert isinstance(filters2, list), f"Expected list, got {type(filters2)}"
        if len(filters2) != 4:
            raise AssertionError(f"Expected 4, got {len(filters2)}")

        # Empty query
        query3 = build_query_dict({})
        if "filters" not in query3:
            raise AssertionError(f"Expected filters in {query3}")
        filters3 = query3["filters"]
        assert isinstance(filters3, list), f"Expected list, got {type(filters3)}"
        if len(filters3) != 0:
            raise AssertionError(f"Expected 0, got {len(filters3)}")

    def test_response_building_examples(self) -> None:
        """Test various response building examples."""
        # Success response with data
        data = {"id": 1, "name": "test", "status": "active"}
        response1 = build_success_response(data, "Resource created successfully")

        assert response1["success"] is True
        assert response1["data"] == data
        assert response1["message"] == "Resource created successfully"

        # Success response without data
        response2 = build_success_response(None, "Operation completed")

        assert response2["success"] is True
        assert response2["data"] is None
        assert response2["message"] == "Operation completed"

        # Success response with metadata
        metadata: dict[str, object] = {"total": 100, "page": 1, "page_size": 10}
        response3 = build_success_response(data, "Data retrieved", metadata)

        assert response3["success"] is True
        assert response3["data"] == data
        assert response3["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_async_client_usage(self) -> None:
        """Test async client usage patterns."""
        # Create client with configuration
        config = FlextApiClientConfig(
            base_url="https://api.example.com",
            timeout=30.0,
            headers={"User-Agent": "FlextApi/1.0"},
        )
        client = FlextApiClient(config)

        # Start the client
        await client.start()
        assert client.status == "running"

        try:
            # Mock HTTP responses to avoid external dependencies
            from unittest.mock import AsyncMock, patch

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.json.return_value = {"slideshow": {"title": "Sample"}}
            mock_response.text.return_value = '{"slideshow": {"title": "Sample"}}'

            with patch("aiohttp.ClientSession.request") as mock_request:
                mock_request.return_value.__aenter__.return_value = mock_response

                # Make a GET request
                result = await client.get("/json")
                assert result.success
                response = result.data
                assert response is not None
                assert response.status_code == 200
                assert isinstance(response.data, dict)
                assert "slideshow" in response.data

                # Make a POST request
                post_data = {"name": "test", "value": 123}
                mock_response.json.return_value = {"json": post_data}

                result = await client.post("/post", json_data=post_data)
                assert result.success
                response = result.data
                assert response is not None
                assert response.status_code == 200
                assert isinstance(response.data, dict)
                assert response.data["json"] == post_data

        finally:
            # Stop the client
            await client.stop()
            assert client.status == "stopped"

    def test_error_handling_examples(self) -> None:
        """Test error handling patterns."""
        # Test invalid configuration
        api = FlextApi()

        # Test with empty configuration
        result = api.flext_api_create_client({})
        assert not result.success
        assert result.error is not None
        assert "base_url" in result.error.lower()

        # Test with invalid URL
        result = api.flext_api_create_client({"base_url": "invalid-url"})
        assert not result.success
        assert result.error is not None
        assert "invalid" in result.error.lower()

    def test_builder_pattern_examples(self) -> None:
        """Test builder pattern usage."""
        from flext_api.builder import FlextApiQueryBuilder, FlextApiResponseBuilder

        # Query builder example
        query = (
            FlextApiQueryBuilder()
            .equals("status", "active")
            .greater_than("age", 18)
            .sort_desc("created_at")
            .page(2)
            .page_size(25)
            .build()
        )

        assert len(query.filters) == 2
        assert len(query.sorts) == 1
        assert query.page == 2
        assert query.page_size == 25

        # Response builder example
        response = (
            FlextApiResponseBuilder()
            .success({"id": 1, "name": "test"}, "Resource created")
            .metadata({"request_id": "12345"})
            .build()
        )

        assert response.success is True
        assert isinstance(response.data, dict)
        assert response.data["id"] == 1
        assert response.message == "Resource created"
        assert isinstance(response.metadata, dict)
        assert response.metadata["request_id"] == "12345"

    def test_plugin_integration_examples(self) -> None:
        """Test plugin integration examples."""
        from flext_api.client import (
            FlextApiClientRequest,
            FlextApiClientResponse,
            FlextApiPlugin,
        )

        # Create a custom plugin
        class CustomPlugin(FlextApiPlugin):
            def __init__(self) -> None:
                super().__init__(name="custom-plugin")

            async def before_request(
                self, request: FlextApiClientRequest
            ) -> FlextApiClientRequest:
                # Add custom header
                if request.headers is None:
                    object.__setattr__(request, "headers", {})
                assert request.headers is not None
                request.headers["X-Custom-Header"] = "custom-value"
                return request

            async def after_request(
                self,
                request_or_response: FlextApiClientRequest | FlextApiClientResponse,
                response: FlextApiClientResponse | None = None,
            ) -> FlextApiClientResponse:
                # Handle both signatures
                if response is None:
                    # New signature: after_request(response)
                    if isinstance(request_or_response, FlextApiClientResponse):
                        return request_or_response
                    # Fallback: create a basic response if request was passed
                    return FlextApiClientResponse(status_code=200, data=None)
                # Old signature: after_request(request, response)
                return response

        # Use plugin with client
        config = FlextApiClientConfig(base_url="https://httpbin.org")
        plugin = CustomPlugin()
        client = FlextApiClient(config, plugins=[plugin])

        assert len(client.plugins) == 1
        assert client.plugins[0].name == "custom-plugin"

    def test_performance_optimization_examples(self) -> None:
        """Test performance optimization examples."""
        # Test connection pooling
        config = FlextApiClientConfig(
            base_url="https://httpbin.org",
            timeout=10.0,
            max_retries=3,
        )
        client = FlextApiClient(config)

        # Test that configuration is properly set
        assert client.config.timeout == 10.0
        assert client.config.max_retries == 3
        assert client.config.base_url == "https://httpbin.org"

    def test_security_examples(self) -> None:
        """Test security configuration examples."""
        # Test with security headers
        config = FlextApiClientConfig(
            base_url="https://api.example.com",
            headers={
                "Authorization": "Bearer secure-token",
                "X-API-Key": "secure-api-key",
                "Content-Security-Policy": "default-src 'self'",
            },
        )
        client = FlextApiClient(config)

        # Verify security headers are set
        assert client.config.headers is not None
        assert "Authorization" in client.config.headers
        assert "X-API-Key" in client.config.headers
        assert "Content-Security-Policy" in client.config.headers
        assert client.config.headers["Authorization"] == "Bearer secure-token"
