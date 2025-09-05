"""Simple tests for models.py missing coverage - REAL tests without mocks.

Focus on testing actual functionality that works rather than assumed interfaces.
"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_api.models import FlextApiModels


class TestFlextApiModelsReal:
    """Test FlextApiModels using REAL functionality."""

    def test_http_url_creation(self) -> None:
        """Test HttpUrl creation with real validation."""
        # Valid creation
        valid_url = FlextApiModels.HttpUrl("https://api.example.com")
        assert valid_url.root == "https://api.example.com"

        # validation works with urlparse
        parsed = urlparse(valid_url.root)
        assert parsed.scheme == "https"
        assert parsed.hostname == "api.example.com"

    def test_api_request_creation(self) -> None:
        """Test creation with real functionality."""
        request = FlextApiModels.ApiRequest(
            id="req_123",
            method="GET",
            url="https://api.example.com/data",
            headers={"Content-Type": "application/json"},
        )

        assert request.id == "req_123"
        assert request.method == "GET"
        assert request.url == "https://api.example.com/data"

    def test_http_response_creation(self) -> None:
        """Test HttpResponse creation with real signature."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"message": "success"},
            url="https://api.example.com/data",
            method="GET",
            elapsed_time=0.123,
        )

        assert response.status_code == 200
        assert response.headers == {"Content-Type": "application/json"}
        assert response.body == {"message": "success"}
        assert response.elapsed_time == 0.123

    def test_client_config_creation(self) -> None:
        """Test ClientConfig creation with validation."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com", timeout=30.0, max_retries=3
        )

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_http_session_creation(self) -> None:
        """Test HttpSession entity creation."""
        session = FlextApiModels.HttpSession(
            session_id="session_abc",
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"},
        )

        assert session.session_id == "session_abc"
        assert session.base_url == "https://api.example.com"

    def test_api_endpoint_creation(self) -> None:
        """Test ApiEndpoint entity creation."""
        endpoint = FlextApiModels.ApiEndpoint(
            endpoint_path="/api/v1/users",
            method="GET",
            base_url="https://api.example.com",
        )

        assert endpoint.endpoint_path == "/api/v1/users"
        assert endpoint.method == "GET"
        assert endpoint.base_url == "https://api.example.com"

    def test_status_code_validation(self) -> None:
        """Test StatusCode validation."""
        # Valid status code
        status = FlextApiModels.StatusCode(200)
        assert status.root == 200

        # Valid error status code
        error_status = FlextApiModels.StatusCode(404)
        assert error_status.root == 404

    def test_timeout_validation(self) -> None:
        """Test Timeout validation."""
        # Valid timeout
        timeout = FlextApiModels.Timeout(30.5)
        assert timeout.root == 30.5

        # Another valid timeout
        quick_timeout = FlextApiModels.Timeout(5.0)
        assert quick_timeout.root == 5.0

    def test_http_port_validation(self) -> None:
        """Test HttpPort validation."""
        # Valid HTTP port
        port = FlextApiModels.HttpPort(8080)
        assert port.root == 8080

        # Valid HTTPS port
        https_port = FlextApiModels.HttpPort(443)
        assert https_port.root == 443

    def test_cache_config_creation(self) -> None:
        """Test CacheConfig creation."""
        cache_config = FlextApiModels.CacheConfig(ttl=300, max_size=1000)

        assert cache_config.ttl == 300
        assert cache_config.max_size == 1000

    def test_retry_config_creation(self) -> None:
        """Test RetryConfig creation."""
        retry_config = FlextApiModels.RetryConfig(max_retries=3, backoff_factor=2.0)

        assert retry_config.max_retries == 3
        assert retry_config.backoff_factor == 2.0
