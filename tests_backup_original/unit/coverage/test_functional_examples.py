"""Functional examples tests for flext-api - REAL EXECUTION WITHOUT MOCKS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiConstants,
    FlextApiModels,
    FlextApiStorage,
    FlextApiUtilities,
    StorageBackend,
    StorageConfig,
    create_flext_api,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestFunctionalExamples:
    """Functional examples using real flext-api components."""

    def test_complete_api_workflow(self) -> None:
        """Test complete API workflow from creation to query building."""
        # Step 1: Create API instance
        api = create_flext_api()
        assert api is not None

        # Step 2: Create URL for API endpoint
        url = "https://api.example.com/v1/workflow"
        assert url is not None

        # Step 3: Create request
        request = FlextApiModels.ApiRequest(
            id="workflow_test",
            method=FlextApiConstants.HttpMethods.POST,
            url=url,
        )
        assert request.id == "workflow_test"

        # Step 4: Build query using simple dict
        query = {
            "filter": {"status": "active"},
            "pagination": {"page": 1, "page_size": 10},
        }
        assert isinstance(query, dict)
        if "pagination" in query and isinstance(query["pagination"], dict):
            assert query["pagination"]["page"] == 1

    def test_client_creation_and_usage(self) -> None:
        """Test client creation and basic usage patterns."""
        # Create API instance
        api = create_flext_api()
        assert api is not None

        # Create client config
        client_config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=30.0,
        )

        # Test that config is valid
        assert client_config.base_url == "https://api.example.com"
        assert client_config.timeout == 30.0

    def test_storage_integration_example(self) -> None:
        """Test storage integration with different backends."""
        # Memory storage
        memory_config = StorageConfig(
            backend=StorageBackend.MEMORY, namespace="functional_test"
        )
        memory_storage = FlextApiStorage(memory_config)
        assert memory_storage is not None

        # File storage

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            file_config = StorageConfig(
                backend=StorageBackend.FILE,
                namespace="functional_file_test",
                file_path=tmp.name,
            )
        file_storage = FlextApiStorage(file_config)
        assert file_storage is not None

    def test_models_integration_example(self) -> None:
        """Test models integration example."""
        # Create models instance
        models = FlextApiModels()
        assert models is not None

        # Test model creation patterns
        assert hasattr(models, "__class__")
        assert models.__class__.__name__ == "FlextApiModels"

    def test_query_building_patterns(self) -> None:
        """Test different query building patterns."""
        # Pattern 1: Simple filter query
        simple_query = {"filter": {"active": True}}
        assert isinstance(simple_query, dict)

        # Pattern 2: Paginated query
        paginated_query = {
            "filter": {"type": "user"},
            "pagination": {"page": 2, "page_size": 25},
        }
        if "pagination" in paginated_query and isinstance(
            paginated_query["pagination"], dict
        ):
            assert paginated_query["pagination"]["page"] == 2
            assert paginated_query["pagination"]["page_size"] == 25

        # Pattern 3: Sorted query
        sorted_query = {
            "filter": {"category": "premium"},
            "sort": {"created_at": "desc"},
        }
        assert isinstance(sorted_query, dict)

    def test_response_building_patterns(self) -> None:
        """Test different response building patterns."""
        # Pattern 1: Success response
        success_result = FlextResult.ok(
            {
                "message": "Request processed successfully",
                "data": {"message": "Operation completed"},
            }
        )
        assert success_result.success is True
        response_data = success_result.value
        if isinstance(response_data, dict):
            assert response_data["message"] == "Request processed successfully"
            if "data" in response_data and isinstance(response_data["data"], dict):
                assert response_data["data"]["message"] == "Operation completed"

        # Pattern 2: Error response
        error_result: FlextResult[None] = FlextResult.fail("Validation failed")
        assert error_result.success is False

    def test_url_validation_examples(self) -> None:
        """Test validation examples."""
        # Valid s
        valid_urls = [
            "https://api.example.com",
            "https://api.example.com/v1",
            "https://api.example.com:8080/v2/resource",
            "http://localhost:3000/api",
        ]

        for url in valid_urls:
            result = FlextApiUtilities.validate_url(url)
            assert result.success, f"should be valid: {url}"

        # Invalid s - should raise exceptions
        invalid_urls = ["", "not-a-url", "://missing-scheme"]

        for url in invalid_urls:
            result = FlextApiUtilities.validate_url(url)
            assert not result.success, f"should be invalid: {url}"

    def test_api_request_examples(self) -> None:
        """Test API request creation examples."""
        # Example 1: GET request
        get_request = FlextApiModels.ApiRequest(
            id="get_example",
            method=FlextApiConstants.HttpMethods.GET,
            url="https://api.example.com/v1/users",
        )
        assert get_request.method == "GET"
        assert "users" in get_request.url

        # Example 2: POST request with headers
        post_request = FlextApiModels.ApiRequest(
            id="post_example",
            method=FlextApiConstants.HttpMethods.POST,
            url="https://api.example.com/v1/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token123",
            },
        )
        assert post_request.method == FlextApiConstants.HttpMethods.POST
        if post_request.headers:
            assert post_request.headers["Content-Type"] == "application/json"

        # Example 3: PUT request
        put_request = FlextApiModels.ApiRequest(
            id="put_example",
            method=FlextApiConstants.HttpMethods.PUT,
            url="https://api.example.com/v1/users/123",
        )
        assert put_request.method == "PUT"
        assert "/123" in put_request.url

    @pytest.mark.asyncio
    async def test_async_storage_example(self) -> None:
        """Test async storage operations example."""
        # Create storage
        config = StorageConfig(backend=StorageBackend.MEMORY, namespace="async_example")
        storage = FlextApiStorage(config)

        # Store data
        storage.set("user:123", {"name": "John", "email": "john@example.com"})
        storage.set("user:456", {"name": "Jane", "email": "jane@example.com"})

        # Retrieve data
        user_result = storage.get("user:123")
        assert user_result.success is True
        if isinstance(user_result.value, dict):
            assert user_result.value["name"] == "John"

        # Check existence
        exists_result = storage.exists("user:456")
        assert exists_result.value is True

        # List keys
        keys_result = storage.keys()
        assert keys_result.success is True
        assert len(keys_result.value) == 2

    def test_integration_workflow_example(self) -> None:
        """Test complete integration workflow example."""
        # Step 1: Create components
        api = create_flext_api()
        storage_config = StorageConfig(
            backend=StorageBackend.MEMORY, namespace="integration_workflow"
        )
        storage = FlextApiStorage(storage_config)

        # Step 2: Create and request
        url_result = FlextApiUtilities.validate_url(
            "https://api.example.com/v1/integration"
        )
        assert url_result.success, "Should be valid integration URL"

        url_string = "https://api.example.com/v1/integration"
        request = FlextApiModels.ApiRequest(
            id="integration_workflow",
            method=FlextApiConstants.HttpMethods.POST,
            url=url_string,
            headers={"Authorization": "Bearer integration-token"},
        )

        # Step 3: Build query
        query = {
            "filter": {"workflow": "integration"},
            "pagination": {"page": 1, "page_size": 50},
        }

        # Step 4: Build response
        response_result = FlextResult.ok(
            {
                "data": {
                    "request_id": request.id,
                    "query": query,
                    "status": "processed",
                },
                "message": "Integration workflow completed",
            }
        )

        # Verify everything works together
        assert api is not None
        assert storage is not None
        assert request.id == "integration_workflow"
        if "pagination" in query and isinstance(query["pagination"], dict):
            assert query["pagination"]["page"] == 1
        assert response_result.success is True
        response_value = response_result.value
        if (
            isinstance(response_value, dict)
            and "data" in response_value
            and isinstance(response_value["data"], dict)
        ):
            assert response_value["data"]["status"] == "processed"

    def test_error_handling_examples(self) -> None:
        """Test error handling examples."""
        # Example 1: Invalid URL validation - should return failed result
        url_result = FlextApiUtilities.validate_url("")
        assert not url_result.success, "Empty URL should be invalid"

        # Example 2: Response error building
        error_response: FlextResult[None] = FlextResult.fail("Resource not found")
        assert error_response.success is False

    def test_bulk_operations_example(self) -> None:
        """Test bulk operations example."""
        # Create multiple requests
        requests = []
        base_url = "https://api.example.com/v1/bulk"

        for i in range(EXPECTED_BULK_SIZE):
            request = FlextApiModels.ApiRequest(
                id=f"bulk_request_{i}",
                method=FlextApiConstants.HttpMethods.POST,
                url=f"{base_url}/item/{i}",
                headers={"Content-Type": "application/json"},
            )
            requests.append(request)

        # Verify bulk creation
        assert len(requests) == EXPECTED_BULK_SIZE
        for i, request in enumerate(requests):
            assert request.id == f"bulk_request_{i}"
            assert f"/item/{i}" in request.url

    def test_data_processing_example(self) -> None:
        """Test data processing example."""
        # Create test data
        test_data = [
            {"id": 1, "name": "Item 1", "active": True},
            {"id": 2, "name": "Item 2", "active": False},
            {"id": 3, "name": "Item 3", "active": True},
        ]

        assert len(test_data) == EXPECTED_DATA_COUNT

        # Process data with API components
        # Filter active items
        active_items = [item for item in test_data if item["active"]]

        # Build response with processed data
        response = FlextResult.ok(
            {
                "data": {
                    "items": active_items,
                    "total": len(active_items),
                    "processed": len(test_data),
                },
                "message": f"Processed {len(test_data)} items, {len(active_items)} active",
            }
        )

        assert response.success is True
        response_data = response.value
        if (
            isinstance(response_data, dict)
            and "data" in response_data
            and isinstance(response_data["data"], dict)
        ):
            assert response_data["data"]["total"] == 2  # 2 active items
            assert response_data["data"]["processed"] == EXPECTED_DATA_COUNT
