"""Tests for missing coverage in models.py module."""

import pytest

from flext_api import FlextApiModels


class TestFlextApiModelsMissingCoverage:
    """Tests for missing coverage in FlextApiModels."""

    def test_http_query_validation_empty_sort_field(self) -> None:
        """Test validation error with empty sort field."""
        # Test with empty sort field - should raise ValueError
        with pytest.raises(ValueError, match="Sort field names cannot be empty"):
            FlextApiModels.HttpQuery(sort_fields=[""])

    def test_http_query_validation_excessive_page_size(self) -> None:
        """Test validation error with excessive page size."""
        # Test with page size too large - Pydantic field validation raises ValidationError
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="less than or equal to"):
            FlextApiModels.HttpQuery(page_size=100000)

    def test_http_query_add_filter_empty_key(self) -> None:
        """Test add_filter with empty key."""
        query = FlextApiModels.HttpQuery()
        result = query.add_filter("", "value")
        assert result.is_failure
        assert "Filter key cannot be empty" in result.error

    def test_url_model_validate_business_rules_empty_url(self) -> None:
        """Test URL model business rules validation with empty URL."""
        # UrlModel has min_length=1 validation on raw_url, so empty string will fail during creation
        with pytest.raises(ValueError):
            FlextApiModels.UrlModel(raw_url="")

    def test_url_model_validate_business_rules_valid_url(self) -> None:
        """Test URL model business rules validation with valid URL."""
        url_model = FlextApiModels.UrlModel(
            raw_url="http://example.com/test",
            scheme="http",
            host="example.com",
            port=80,
            path="/test",
        )
        result = url_model.validate_business_rules()
        assert result.is_success
