"""Functional examples tests for flext-api - REAL EXECUTION WITHOUT MOCKS.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApi,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiPlugin,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    build_query,
    build_query_dict,
    build_success_response,
    create_flext_api,
    create_memory_storage,
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
            msg = f"Expected filters in {query_dict}"
            raise AssertionError(msg)
        filters = query_dict["filters"]
        assert isinstance(filters, list), f"Expected list, got {type(filters)}"
        if len(filters) != EXPECTED_BULK_SIZE:
            msg = f"Expected 2, got {len(filters)}"
            raise AssertionError(msg)

        # Create client configuration using modern API
        client_config = {"base_url": "https://api.example.com", "timeout": 30}
        client_result = api.create_client(client_config)

        # Should succeed
        assert client_result.success
        assert client_result.value is not None

    def test_client_configuration_examples(self) -> None:
        """Test various client configuration examples."""
        # Minimal configuration
        config1 = FlextApiClientConfig(base_url="https://api.example.com")
        client1 = FlextApiClient(config1)
        if client1.config.base_url != "https://api.example.com":
            msg = f"Expected https://api.example.com, got {client1.config.base_url}"
            raise AssertionError(
                msg,
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
            msg = f"Expected 60.0, got {client2.config.timeout}"
            raise AssertionError(msg)
        assert client2.config.headers == {"Authorization": "Bearer token123"}
        if client2.config.max_retries != 5:
            msg = f"Expected 5, got {client2.config.max_retries}"
            raise AssertionError(msg)

    def test_query_building_examples(self) -> None:
        """Test various query building examples."""
        # Simple query
        query1 = build_query_dict({"name": "test"})
        if "filters" not in query1:
            msg = f"Expected filters in {query1}"
            raise AssertionError(msg)
        filters1 = query1["filters"]
        assert isinstance(filters1, list), f"Expected list, got {type(filters1)}"
        if len(filters1) != 1:
            msg = f"Expected 1, got {len(filters1)}"
            raise AssertionError(msg)
        assert isinstance(filters1[0], dict), f"Expected dict, got {type(filters1[0])}"
        assert filters1[0]["field"] == "name"

        # Complex query with multiple filters
        query2 = build_query_dict(
            {
                "status": "active",
                "created_after": "2023-01-01",
                "limit": 50,
                "sort": "name",
            },
        )
        if "filters" not in query2:
            msg = f"Expected filters in {query2}"
            raise AssertionError(msg)
        filters2 = query2["filters"]
        assert isinstance(filters2, list), f"Expected list, got {type(filters2)}"
        if len(filters2) != 4:
            msg = f"Expected 4, got {len(filters2)}"
            raise AssertionError(msg)

        # Empty query
        query3 = build_query_dict({})
        if "filters" not in query3:
            msg = f"Expected filters in {query3}"
            raise AssertionError(msg)
        filters3 = query3["filters"]
        assert isinstance(filters3, list), f"Expected list, got {type(filters3)}"
        if len(filters3) != 0:
            msg = f"Expected 0, got {len(filters3)}"
            raise AssertionError(msg)

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
    async def test_async_client_real_operations(self) -> None:
        """Test async client REAL operations without mocks - internal functionality."""
        # Create client with configuration - REAL CONFIG VALIDATION
        config = FlextApiClientConfig(
            base_url="https://api.example.com",
            timeout=30.0,
            headers={"User-Agent": "FlextApi/1.0"},
        )
        client = FlextApiClient(config)

        # Test REAL client lifecycle management
        await client.start()
        assert client.status == "running"

        try:
            # Test REAL storage operations
            storage = create_memory_storage()

            # REAL storage set operation
            set_result = await storage.set("test_key", {"data": "test_value"})
            assert set_result.success

            # REAL storage get operation
            get_result = await storage.get("test_key")
            assert get_result.success
            assert get_result.value == {"data": "test_value"}

            # Test REAL query building with actual validation
            query_builder = FlextApiQueryBuilder()
            query = (
                query_builder.equals("status", "active")
                .sort_desc("created_at")
                .page(1)
                .page_size(20)
                .build()
            )

            # REAL validation of query structure
            query_dict = query.to_dict()
            assert "filters" in query_dict
            assert isinstance(query_dict["filters"], list)
            assert len(query_dict["filters"]) == 1
            assert query_dict["filters"][0]["field"] == "status"
            assert query_dict["filters"][0]["value"] == "active"

            # Test REAL response building
            response_builder = FlextApiResponseBuilder()
            test_data = {"items": [1, 2, 3], "count": 3}
            response = (
                response_builder.success(test_data, "Data retrieved successfully")
                .with_metadata({"total": 3, "page": 1})
                .build()
            )

            # REAL validation of response structure
            assert response["success"] is True
            assert response["data"] == test_data
            assert response["message"] == "Data retrieved successfully"
            assert response["metadata"]["total"] == 3

        finally:
            # REAL client lifecycle - stop the client
            await client.stop()
            assert client.status == "stopped"

    def test_error_handling_examples(self) -> None:
        """Test error handling patterns."""
        # Test invalid configuration
        api = FlextApi()

        # Test with empty configuration using modern API
        result = api.create_client({})
        assert not result.success
        assert result.error is not None
        assert "base_url" in result.error.lower()

        # Test with invalid URL using modern API
        result = api.create_client({"base_url": "invalid-url"})
        assert not result.success
        assert result.error is not None
        assert "invalid" in result.error.lower()

    def test_builder_pattern_examples(self) -> None:
        """Test builder pattern usage."""
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
        assert isinstance(response.value, dict)
        assert response.value["id"] == 1
        assert response.message == "Resource created"
        assert isinstance(response.metadata, dict)
        assert response.metadata["request_id"] == "12345"

    def test_plugin_integration_examples(self) -> None:
        """Test plugin integration examples."""

        # Create a custom plugin
        class CustomPlugin(FlextApiPlugin):
            def __init__(self) -> None:
                super().__init__(name="custom-plugin")

            async def before_request(
                self,
                request: FlextApiClientRequest,
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
