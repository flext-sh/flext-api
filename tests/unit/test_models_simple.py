"""Tests for simplified FlextApiModels following SOLID principles."""

import pytest
from pydantic import ValidationError

from flext_api import FlextApiModels


class TestFlextApiModelsSimple:
    """Test simplified FlextApiModels."""

    def test_client_config_creation_default(self) -> None:
        """Test ClientConfig creation with default values."""
        config = FlextApiModels.ClientConfig()
        assert config.base_url == "http://127.0.0.1:8000"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_client_config_creation_custom(self) -> None:
        """Test ClientConfig creation with custom values."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=60.0,
            max_retries=5,
        )
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 60.0
        assert config.max_retries == 5

    def test_client_config_validation_base_url(self) -> None:
        """Test ClientConfig base URL validation."""
        # Valid URL
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert config.base_url == "https://api.example.com"

        # Invalid URL
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            FlextApiModels.ClientConfig(base_url="invalid-url")

    def test_client_config_validation_timeout(self) -> None:
        """Test ClientConfig timeout validation."""
        # Valid timeout
        config = FlextApiModels.ClientConfig(timeout=60.0)
        assert config.timeout == 60.0

        # Invalid timeout - Pydantic validation
        with pytest.raises(ValidationError, match=r"greater than 0"):
            FlextApiModels.ClientConfig(timeout=0.0)

    def test_client_config_validation_max_retries(self) -> None:
        """Test ClientConfig max retries validation."""
        # Valid max retries
        config = FlextApiModels.ClientConfig(max_retries=5)
        assert config.max_retries == 5

        # Invalid max retries - Pydantic validation
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            FlextApiModels.ClientConfig(max_retries=-1)

    def test_http_request_creation(self) -> None:
        """Test HttpRequest creation."""
        request = FlextApiModels.HttpRequest(
            url="https://api.example.com/users",
            method="GET",
            headers={"Content-Type": "application/json"},
            body='{"name": "test"}',
        )
        assert request.url == "https://api.example.com/users"
        assert request.method == "GET"
        assert request.headers == {"Content-Type": "application/json"}
        assert request.body == '{"name": "test"}'

    def test_http_request_defaults(self) -> None:
        """Test HttpRequest default values."""
        request = FlextApiModels.HttpRequest(url="https://api.example.com/users")
        assert request.url == "https://api.example.com/users"
        assert request.method == "GET"
        assert request.headers == {}
        assert request.body is None

    def test_http_request_validation(self) -> None:
        """Test HttpRequest validation."""
        # Valid URL
        request = FlextApiModels.HttpRequest(url="https://api.example.com/users")
        assert request.url == "https://api.example.com/users"

        # Invalid URL
        with pytest.raises(ValueError, match="Invalid URL format"):
            FlextApiModels.HttpRequest(url="invalid-url")

    def test_http_response_creation(self) -> None:
        """Test HttpResponse creation."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            body='{"success": true}',
            headers={"Content-Type": "application/json"},
            url="https://api.example.com/users",
            method="GET",
        )
        assert response.status_code == 200
        assert response.body == '{"success": true}'
        assert response.headers == {"Content-Type": "application/json"}
        assert response.url == "https://api.example.com/users"
        assert response.method == "GET"

    def test_http_response_is_success(self) -> None:
        """Test HttpResponse is_success property."""
        # Success response
        response = FlextApiModels.HttpResponse(
            status_code=200,
            body="success",
            url="https://api.example.com/users",
            method="GET",
        )
        assert response.is_success is True

        # Error response
        response = FlextApiModels.HttpResponse(
            status_code=404,
            body="not found",
            url="https://api.example.com/users",
            method="GET",
        )
        assert response.is_success is False

    def test_http_response_validation(self) -> None:
        """Test HttpResponse validation."""
        # Valid status code
        response = FlextApiModels.HttpResponse(
            status_code=200,
            url="https://api.example.com/users",
            method="GET",
        )
        assert response.status_code == 200

        # Invalid status code - Pydantic validation
        with pytest.raises(ValidationError, match="less than or equal to 599"):
            FlextApiModels.HttpResponse(
                status_code=600,
                url="https://api.example.com/users",
                method="GET",
            )

    def test_pagination_config_creation_default(self) -> None:
        """Test PaginationConfig creation with default values."""
        config = FlextApiModels.PaginationConfig()
        assert config.page == 1
        assert config.page_size == 20
        assert config.total == 0

    def test_pagination_config_creation_custom(self) -> None:
        """Test PaginationConfig creation with custom values."""
        config = FlextApiModels.PaginationConfig(
            page=2,
            page_size=50,
            total=100,
        )
        assert config.page == 2
        assert config.page_size == 50
        assert config.total == 100

    def test_pagination_config_validation_page(self) -> None:
        """Test PaginationConfig page validation."""
        # Valid page
        config = FlextApiModels.PaginationConfig(page=5)
        assert config.page == 5

        # Invalid page - Pydantic validation
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            FlextApiModels.PaginationConfig(page=0)

    def test_pagination_config_validation_page_size(self) -> None:
        """Test PaginationConfig page size validation."""
        # Valid page size
        config = FlextApiModels.PaginationConfig(page_size=50)
        assert config.page_size == 50

        # Invalid page size - Pydantic validation
        with pytest.raises(ValidationError, match="greater than 0"):
            FlextApiModels.PaginationConfig(page_size=0)

    def test_models_inheritance(self) -> None:
        """Test models inheritance from FlextModels."""
        # Main class should inherit from FlextModels
        assert issubclass(FlextApiModels, type(FlextApiModels).__bases__[0])

        # Nested models should have BaseModel functionality
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")
