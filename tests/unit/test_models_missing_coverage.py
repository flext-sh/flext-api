"""Tests for missing coverage in models.py module."""

import pytest

from flext_api import FlextApiModels


class TestFlextApiModelsMissingCoverage:
    """Tests for missing coverage in FlextApiModels."""

    def test_http_query_url_validation_error_handling(self) -> None:
        """Test URL validation error handling in HttpQuery."""
        # Test with invalid URL that triggers specific error messages
        with pytest.raises(ValueError, match="Invalid URL"):
            FlextApiModels.HttpQuery(base_url="invalid-url", endpoint="/test")

    def test_http_query_url_validation_empty_url(self) -> None:
        """Test URL validation with empty URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            FlextApiModels.HttpQuery(base_url="", endpoint="/test")

    def test_http_query_url_validation_hostname_error(self) -> None:
        """Test URL validation with hostname error."""
        with pytest.raises(ValueError, match="Invalid URL"):
            FlextApiModels.HttpQuery(base_url="http://", endpoint="/test")

    def test_url_model_validate_business_rules_empty_url(self) -> None:
        """Test URL model business rules validation with empty URL."""
        url_model = FlextApiModels.UrlModel(
            raw_url="", scheme="http", hostname="example.com", port=80, path="/test"
        )
        result = url_model.validate_business_rules()
        assert result.is_failure
        assert result.error is not None and "URL cannot be empty" in result.error

    def test_url_model_validate_business_rules_valid_url(self) -> None:
        """Test URL model business rules validation with valid URL."""
        url_model = FlextApiModels.UrlModel(
            raw_url="http://example.com/test",
            scheme="http",
            hostname="example.com",
            port=80,
            path="/test",
        )
        result = url_model.validate_business_rules()
        assert result.is_success
