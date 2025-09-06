"""Simple tests for models.py missing coverage - REAL tests without mocks.

Focus on testing actual functionality that works rather than assumed interfaces.
"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_api.models import FlextApiModels


class TestFlextApiModelsReal:
    """Test FlextApiModels using REAL functionality."""

    def test_client_config_creation(self) -> None:
        """Test ClientConfig creation with real validation."""
        # Valid creation
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=30.0,
            max_retries=3
        )
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3

        # validation works with urlparse
        parsed = urlparse(config.base_url)
        assert parsed.scheme == "https"
        assert parsed.hostname == "api.example.com"

    def test_api_request_creation(self) -> None:
        """Test creation with real functionality."""
        request = FlextApiModels.ApiRequest(
            id="req_123",
            method=FlextApiModels.HttpMethod.GET,
            url="https://api.example.com/data",
            headers={"Content-Type": "application/json"},
        )

        assert request.id == "req_123"
        assert request.method == FlextApiModels.HttpMethod.GET
        assert request.url == "https://api.example.com/data"

    def test_http_response_creation(self) -> None:
        """Test HttpResponse creation with real signature."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"message": "success"},
            url="https://api.example.com/data",
            method="GET"
        )

        assert response.status_code == 200
        assert response.headers == {"Content-Type": "application/json"}
        assert response.body == {"message": "success"}
        assert response.url == "https://api.example.com/data"
        assert response.method == "GET"

    def test_http_query_creation(self) -> None:
        """Test HttpQuery creation with validation."""
        query = FlextApiModels.HttpQuery(
            filter_conditions={"status": "active", "type": "user"},
            sort_fields=["name", "created_at"],
            page_number=2,
            page_size_value=50
        )

        assert query.filter_conditions == {"status": "active", "type": "user"}
        assert query.sort_fields == ["name", "created_at"]
        assert query.page_number == 2
        assert query.page_size_value == 50

    def test_api_response_creation(self) -> None:
        """Test ApiResponse entity creation."""
        response = FlextApiModels.ApiResponse(
            status_code=200,
            success=True,
            data={"id": 1, "name": "test"},
            message="Operation successful"
        )

        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"id": 1, "name": "test"}
        assert response.message == "Operation successful"

    def test_builder_creation(self) -> None:
        """Test Builder creation and usage."""
        # Builder is a response builder model
        builder = FlextApiModels.Builder()

        # Test the create method
        result = builder.create(status="success", data={"id": 1})
        assert result == {"status": "success", "data": {"id": 1}}

    def test_storage_config_creation(self) -> None:
        """Test StorageConfig creation."""
        # Valid storage config
        storage = FlextApiModels.StorageConfig(
            backend="redis",
            host="localhost",
            port=6379,
            db=0
        )
        assert storage.backend == "redis"
        assert storage.host == "localhost"
        assert storage.port == 6379
        assert storage.db == 0

    def test_http_method_enum(self) -> None:
        """Test HttpMethod enum values."""
        # Test enum values
        assert FlextApiModels.HttpMethod.GET == "GET"
        assert FlextApiModels.HttpMethod.POST == "POST"
        assert FlextApiModels.HttpMethod.PUT == "PUT"
        assert FlextApiModels.HttpMethod.DELETE == "DELETE"

    def test_http_status_enum(self) -> None:
        """Test HttpStatus enum values."""
        # Test enum values
        assert FlextApiModels.HttpStatus.SUCCESS == "success"
        assert FlextApiModels.HttpStatus.ERROR == "error"
        assert FlextApiModels.HttpStatus.PENDING == "pending"
        assert FlextApiModels.HttpStatus.TIMEOUT == "timeout"
