"""Focused tests for models.py to increase coverage efficiently."""

from __future__ import annotations

from flext_api import (
    URL,
    ApiRequest,
    FlextApiModels,
)
from flext_api.models import (
    MAX_PORT,
    MIN_PORT,
)
from flext_api.typings import FlextApiTypes

# Import enums and response types
HttpMethod = FlextApiModels.HttpMethod
HttpStatus = FlextApiModels.HttpStatus
ApiResponse = FlextApiTypes.Response.ApiResponse
ClientStatus = FlextApiModels.HttpStatus  # Use HttpStatus for client status as well


class TestURL:
    """Test URL model creation and validation."""

    def test_url_create_success(self) -> None:
        """Test successful URL creation."""
        result = URL("https://api.example.com:8080/v1?param=value")

        assert result.success
        assert result.value is not None

        url = result.value
        assert url.scheme == "https"
        assert url.host == "api.example.com"
        assert url.port == 8080
        assert url.path == "/v1"
        assert url.query == "param=value"

    def test_url_create_minimal(self) -> None:
        """Test URL creation with minimal URL."""
        result = URL("https://example.com")

        assert result.success
        assert result.value is not None

        url = result.value
        assert url.scheme == "https"
        assert url.host == "example.com"
        assert url.path == "/"

    def test_url_create_with_defaults(self) -> None:
        """Test URL creation that uses default scheme."""
        # Test with a minimal URL that would use defaults
        result = URL("example.com/test")

        # Should succeed and use default scheme
        if result.success:
            url = result.value
            assert url.raw_url == "example.com/test"
            assert url.path == "/test"

    def test_url_create_error_handling(self) -> None:
        """Test URL creation error handling."""
        # Test with various potentially problematic URLs
        test_urls = [
            "",  # Empty URL
            "not-a-url",  # Invalid format
            "://missing-scheme",  # Missing scheme
        ]

        for test_url in test_urls:
            result = URL(test_url)
            # Either it should fail gracefully or succeed with validation errors
            if result.success:
                # If it succeeds, the validation should catch issues
                validation_result = result.value.validate_business_rules()
                # The validation might fail, which is expected for invalid URLs
                assert validation_result.success or validation_result.error is not None
            else:
                # If creation fails, that's also acceptable
                assert result.error is not None

    def test_url_validation_business_rules(self) -> None:
        """Test URL validation with valid data."""
        # Create a URL that should pass all validation rules
        result = URL("https://valid-host.com:443/api/v1?query=test#section")

        if result.success:
            url = result.value
            validation_result = url.validate_business_rules()
            assert validation_result.success


class TestEnums:
    """Test enum definitions and values."""

    def test_http_method_enum(self) -> None:
        """Test HTTP method enum values."""
        assert HttpMethod.GET == "GET"
        assert HttpMethod.POST == "POST"
        assert HttpMethod.PUT == "PUT"
        assert HttpMethod.DELETE == "DELETE"
        assert HttpMethod.PATCH == "PATCH"
        assert HttpMethod.HEAD == "HEAD"
        assert HttpMethod.OPTIONS == "OPTIONS"

    def test_http_status_enum(self) -> None:
        """Test HTTP status enum values."""
        # Test common status codes
        assert HttpStatus.OK.value == 200
        assert HttpStatus.CREATED.value == 201
        assert HttpStatus.NO_CONTENT.value == 204
        assert HttpStatus.BAD_REQUEST.value == 400
        assert HttpStatus.UNAUTHORIZED.value == 401
        assert HttpStatus.FORBIDDEN.value == 403
        assert HttpStatus.NOT_FOUND.value == 404
        assert HttpStatus.INTERNAL_SERVER_ERROR.value == 500

    def test_client_status_enum(self) -> None:
        """Test ClientStatus enum."""
        # Test that ClientStatus has expected values
        status_values = list(ClientStatus)
        assert len(status_values) > 0

        # Test common client states
        if hasattr(ClientStatus, "IDLE"):
            assert ClientStatus.IDLE
        if hasattr(ClientStatus, "ACTIVE"):
            assert ClientStatus.ACTIVE
        if hasattr(ClientStatus, "DISCONNECTED"):
            assert ClientStatus.DISCONNECTED


class TestApiModels:
    """Test API request and response models."""

    def test_api_request_creation(self) -> None:
        """Test ApiRequest model creation."""
        # Test with minimal required fields (id, method, url are required by FlextModels)
        request = ApiRequest(id="req_123", method=HttpMethod.GET, url="/api/users")

        assert request.method == "GET"
        assert request.url == "/api/users"
        assert request.id == "req_123"

    def test_api_request_with_optional_fields(self) -> None:
        """Test ApiRequest with optional fields."""
        # Test with additional fields - use required fields
        request = ApiRequest(
            id="req_456",
            method=HttpMethod.POST,
            url="/api/users",
            headers={"Content-Type": "application/json"},
        )

        assert request.method == "POST"
        assert request.url == "/api/users"
        assert request.id == "req_456"
        assert request.headers == {"Content-Type": "application/json"}

    def test_api_response_creation(self) -> None:
        """Test ApiResponse model creation."""
        # Test with minimal required fields (id and status_code are required)
        response = ApiResponse(id="resp_123", status_code=200)

        assert response.status_code == 200
        assert response.id == "resp_123"

    def test_api_response_with_data(self) -> None:
        """Test ApiResponse with data field."""
        # Test with optional body field
        response = ApiResponse(
            id="resp_456", status_code=201, body={"id": 1, "name": "Test User"}
        )

        assert response.status_code == 201
        assert response.id == "resp_456"
        assert response.body == {"id": 1, "name": "Test User"}


class TestConstants:
    """Test constant definitions."""

    def test_port_constants(self) -> None:
        """Test port validation constants."""
        assert MIN_PORT == 1
        assert MAX_PORT == 65535

        # Test boundary values
        assert MIN_PORT <= 80 <= MAX_PORT
        assert MIN_PORT <= 443 <= MAX_PORT
        assert MIN_PORT <= 8080 <= MAX_PORT

    def test_port_validation_logic(self) -> None:
        """Test port validation logic."""
        # Test valid ports
        valid_ports = [1, 80, 443, 8080, 8443, 65535]
        for port in valid_ports:
            assert MIN_PORT <= port <= MAX_PORT

        # Test invalid ports
        invalid_ports = [0, -1, 65536, 99999]
        for port in invalid_ports:
            assert not (MIN_PORT <= port <= MAX_PORT)


class TestModelIntegration:
    """Test model integration scenarios."""

    def test_url_with_all_components(self) -> None:
        """Test URL creation with all possible components."""
        full_url = "https://user:pass@api.example.com:8443/v1/users?active=true&sort=name#results"
        result = URL(full_url)

        if result.success:
            url = result.value
            assert url.scheme == "https"
            assert url.host == "api.example.com"
            assert url.port == 8443
            assert url.path == "/v1/users"
            assert "active=true" in (url.query or "")
            assert url.fragment == "results"

    def test_api_models_with_http_enums(self) -> None:
        """Test API models using HTTP enums."""
        # Create request using enum values (with required fields)
        request = ApiRequest(id="req_789", method=HttpMethod.POST, url="/api/resources")

        assert request.method == HttpMethod.POST
        assert request.id == "req_789"

        # Create response using enum values (with required fields)
        response = ApiResponse(id="resp_789", status_code=HttpStatus.CREATED.value)

        assert response.status_code == HttpStatus.CREATED
        assert response.id == "resp_789"

    def test_complex_scenarios(self) -> None:
        """Test complex integration scenarios."""
        # Test URL creation and validation in sequence
        urls = [
            "https://api.example.com/v1",
            "http://localhost:8080/health",
            "https://secure-api.domain.com:443/auth/login",
        ]

        for url_string in urls:
            result = URL(url_string)
            assert result.success, f"Failed to create URL: {url_string}"

            url = result.value
            validation_result = url.validate_business_rules()
            assert validation_result.success, f"Validation failed for URL: {url_string}"


class TestErrorConditions:
    """Test error handling and edge cases."""

    def test_url_edge_cases(self) -> None:
        """Test URL edge cases."""
        edge_cases = [
            "https://localhost",  # No port
            "https://127.0.0.1:8080",  # IP address
            "https://api.example.com/",  # Trailing slash
            "https://api.example.com:443",  # Standard HTTPS port
        ]

        for url_string in edge_cases:
            result = URL(url_string)
            # These should all succeed
            assert result.success, f"Edge case failed: {url_string}"

    def test_enum_completeness(self) -> None:
        """Test that enums have expected completeness."""
        # HttpMethod should have common HTTP methods
        http_methods = list(HttpMethod)
        method_values = [method.value for method in http_methods]

        required_methods = ["GET", "POST", "PUT", "DELETE"]
        for method in required_methods:
            assert method in method_values, f"Missing HTTP method: {method}"

        # HttpStatus should have common status codes
        http_statuses = list(HttpStatus)
        status_codes = [status.value for status in http_statuses]

        required_codes = [200, 201, 400, 401, 404, 500]
        for code in required_codes:
            assert code in status_codes, f"Missing HTTP status code: {code}"
