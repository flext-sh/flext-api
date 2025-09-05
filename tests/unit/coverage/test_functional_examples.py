"""Functional examples tests for flext-api - REAL EXECUTION WITHOUT MOCKS.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile

import pytest

from flext_api import (
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
            method=FlextApiModels.HttpMethod.POST,
            url=url,
        )
        assert request.id == "workflow_test"

        # Step 4: Build query using API builder
        builder = api.get_builder()
        query = (
            builder.for_query().equals("status", "active").page(1).page_size(10).build()
        )
        assert isinstance(query, dict)
        assert query["pagination"]["page"] == 1

    def test_client_creation_and_usage(self) -> None:
        """Test client creation and basic usage patterns."""
        # Create API instance
        api = create_flext_api()

        # Create client
        client_result = api.create_client(
            {"base_url": "https://api.example.com", "timeout": 30}
        )

        assert client_result.success is True
        client = client_result.value
        assert client is not None
        assert hasattr(client, "base_url")

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
        api = create_flext_api()
        builder = api.get_builder()

        # Pattern 1: Simple filter query
        simple_query = builder.for_query().equals("active", True).build()
        assert isinstance(simple_query, dict)

        # Pattern 2: Paginated query
        paginated_query = (
            builder.for_query().equals("type", "user").page(2).page_size(25).build()
        )
        assert paginated_query["pagination"]["page"] == 2
        assert paginated_query["pagination"]["page_size"] == 25

        # Pattern 3: Sorted query
        sorted_query = (
            builder.for_query()
            .equals("category", "premium")
            .sort_desc("created_at")
            .build()
        )
        assert isinstance(sorted_query, dict)

    def test_response_building_patterns(self) -> None:
        """Test different response building patterns."""
        api = create_flext_api()
        builder = api.get_builder()

        # Pattern 1: Success response
        success_result = builder.for_response().success(
            data={"message": "Operation completed"},
            message="Request processed successfully",
        )
        assert success_result.success is True
        response_data = success_result.value
        assert response_data["message"] == "Request processed successfully"
        assert response_data["data"]["message"] == "Operation completed"

        # Pattern 2: Error response
        error_result = builder.for_response().error("Validation failed", 400)
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
        get_request = FlextApiModels.FlextApiModels(
            id="get_example", method="GET", url="https://api.example.com/v1/users"
        )
        assert get_request.method == "GET"
        assert "users" in get_request.url

        # Example 2: POST request with headers
        post_request = FlextApiModels.FlextApiModels(
            id="post_example",
            method="POST",
            url="https://api.example.com/v1/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token123",
            },
        )
        assert post_request.method == "POST"
        assert post_request.headers["Content-Type"] == "application/json"

        # Example 3: PUT request
        put_request = FlextApiModels.FlextApiModels(
            id="put_example", method="PUT", url="https://api.example.com/v1/users/123"
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
        await storage.set("user:123", {"name": "John", "email": "john@example.com"})
        await storage.set("user:456", {"name": "Jane", "email": "jane@example.com"})

        # Retrieve data
        user_result = await storage.get("user:123")
        assert user_result.success is True
        assert user_result.value["name"] == "John"

        # Check existence
        exists_result = await storage.exists("user:456")
        assert exists_result.value is True

        # List keys
        keys_result = await storage.keys()
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
        url_result = FlextApiUtilities.validate_url("https://api.example.com/v1/integration")
        assert url_result.success, "Should be valid integration URL"

        url_string = "https://api.example.com/v1/integration"
        request = FlextApiModels.FlextApiModels(
            id="integration_workflow",
            method="POST",
            url=url_string,
            headers={"Authorization": "Bearer integration-token"},
        )

        # Step 3: Build query
        builder = api.get_builder()
        query = (
            builder.for_query()
            .equals("workflow", "integration")
            .page(1)
            .page_size(50)
            .build()
        )

        # Step 4: Build response
        response_result = builder.for_response().success(
            data={"request_id": request.id, "query": query, "status": "processed"},
            message="Integration workflow completed",
        )

        # Verify everything works together
        assert api is not None
        assert storage is not None
        assert request.id == "integration_workflow"
        assert query["pagination"]["page"] == 1
        assert response_result.success is True
        assert response_result.value["data"]["status"] == "processed"

    def test_error_handling_examples(self) -> None:
        """Test error handling examples."""
        # Example 1: Invalid URL validation - should return failed result
        url_result = FlextApiUtilities.validate_url("")
        assert not url_result.success, "Empty URL should be invalid"

        # Example 2: Response error building
        api = create_flext_api()
        builder = api.get_builder()

        error_response = builder.for_response().error("Resource not found", 404)
        assert error_response.success is False

    def test_bulk_operations_example(self) -> None:
        """Test bulk operations example."""
        # Create multiple requests
        requests = []
        base_url = "https://api.example.com/v1/bulk"

        for i in range(EXPECTED_BULK_SIZE):
            request = FlextApiModels.FlextApiModels(
                id=f"bulk_request_{i}",
                method="POST",
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
        api = create_flext_api()
        builder = api.get_builder()

        # Filter active items
        active_items = [item for item in test_data if item["active"]]

        # Build response with processed data
        response = builder.for_response().success(
            data={
                "items": active_items,
                "total": len(active_items),
                "processed": len(test_data),
            },
            message=f"Processed {len(test_data)} items, {len(active_items)} active",
        )

        assert response.success is True
        response_data = response.value
        assert response_data["data"]["total"] == 2  # 2 active items
        assert response_data["data"]["processed"] == EXPECTED_DATA_COUNT
