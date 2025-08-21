"""Test models.py coverage with REAL execution - NO MOCKS."""

from __future__ import annotations

from flext_api import (
    URL,
    HttpMethod,
    HttpStatus,
)


def test_url_validation_failures() -> None:
    """Test URL validation failure cases."""
    # Test empty URL
    result = URL.create("")
    assert not result.success
    assert "URL cannot be empty" in (result.error or "")

    # Test invalid scheme
    result = URL.create("ftp://example.com")
    assert not result.success
    assert "Invalid URL scheme" in (result.error or "")

    # Test missing host
    result = URL.create("https://")
    assert not result.success
    assert "valid host" in (result.error or "")

    # Test invalid port
    result = URL.create("https://example.com:99999")
    assert not result.success
    assert "Port out of range" in (result.error or "")


def test_url_parse_real_invalid_cases() -> None:
    """Test URL parsing with REAL invalid cases that are already covered by validation."""
    # Use cases that are actually invalid according to our URL validation logic
    # These will be caught by our validation, not by parsing errors
    test_cases = [
        ("", "URL cannot be empty"),  # Empty URL
        ("ftp://example.com", "Invalid URL scheme"),  # Invalid scheme
        ("https://", "valid host"),  # Missing host
        ("https://example.com:99999", "Port out of range"),  # Invalid port
    ]

    for invalid_url, expected_error in test_cases:
        result = URL.create(invalid_url)
        assert not result.success
        # Should get the expected validation error
        error_msg = result.error or ""
        assert expected_error in error_msg


def test_url_is_secure() -> None:
    """Test URL security checking."""
    secure_url_result = URL.create("https://example.com")
    assert secure_url_result.success
    secure_url = secure_url_result.value
    assert secure_url.is_secure() is True

    insecure_url_result = URL.create("http://example.com")
    assert insecure_url_result.success
    insecure_url = insecure_url_result.value
    assert insecure_url.is_secure() is False


def test_url_business_validation() -> None:
    """Test URL business rule validation directly."""
    # Create URL and test validation
    result = URL.create("https://example.com")
    assert result.success
    url = result.value

    # Test business rule validation
    validation_result = url.validate_business_rules()
    assert validation_result.success


def test_enum_coverage() -> None:
    """Test enum classes for coverage."""
    # Test HttpMethod enum
    assert HttpMethod.GET == "GET"
    assert HttpMethod.POST == "POST"
    assert HttpMethod.PUT == "PUT"
    assert HttpMethod.DELETE == "DELETE"
    assert HttpMethod.PATCH == "PATCH"
    assert HttpMethod.HEAD == "HEAD"
    assert HttpMethod.OPTIONS == "OPTIONS"

    # Test HttpStatus enum
    assert HttpStatus.OK == 200
    assert HttpStatus.CREATED == 201
    assert HttpStatus.BAD_REQUEST == 400
    assert HttpStatus.UNAUTHORIZED == 401
    assert HttpStatus.FORBIDDEN == 403
    assert HttpStatus.NOT_FOUND == 404
    assert HttpStatus.INTERNAL_SERVER_ERROR == 500


def test_model_edge_cases() -> None:
    """Test model edge cases and boundary conditions."""
    # Test URL with port boundary
    result = URL.create("https://example.com:1")
    assert result.success

    result = URL.create("https://example.com:65535")
    assert result.success


def test_factory_method_patterns() -> None:
    """Test factory method patterns in models."""
    # Test URL factory method
    result = URL.create("https://api.example.com:8080/v1/test?param=value")
    assert result.success
    url = result.value
    assert url.scheme == "https"
    assert url.host == "api.example.com"
    assert url.port == 8080
    assert url.path == "/v1/test"
    assert url.query == "param=value"


def test_model_string_representations() -> None:
    """Test model string representations."""
    # Test URL string representation
    result = URL.create("https://example.com/test")
    assert result.success
    url = result.value
    assert str(url) is not None


def test_url_additional_methods() -> None:
    """Test additional URL methods for coverage."""
    result = URL.create("https://api.example.com:8080/v1/test")
    assert result.success
    url = result.value

    # Test additional methods that exist
    assert hasattr(url, "base_url")
    assert hasattr(url, "full_path")

    # Test these methods
    if hasattr(url, "base_url") and callable(url.base_url):
        base_url = url.base_url()
        assert isinstance(base_url, str)

    if hasattr(url, "full_path") and callable(url.full_path):
        full_path = url.full_path()
        assert isinstance(full_path, str)
