"""REAL tests for FlextApiUtilities - using ACTUAL methods that exist.

Testing genuine functionality with REAL method calls, no mocks, no fake methods.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextResult

from flext_api import FlextApiUtilities
from flext_api.utilities import HttpRequestConfig


class TestFlextApiUtilitiesReal:
    """Test FlextApiUtilities using ONLY methods that actually exist."""

    def test_generate_uuid(self) -> None:
        """Test real UUID generation."""
        uuid1 = FlextApiUtilities.generate_uuid()
        uuid2 = FlextApiUtilities.generate_uuid()

        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert len(uuid1) == 36
        assert len(uuid2) == 36
        assert uuid1 != uuid2
        assert "-" in uuid1

    def test_generate_id(self) -> None:
        """Test real ID generation."""
        id1 = FlextApiUtilities.generate_id()
        id2 = FlextApiUtilities.generate_id()

        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert len(id1) > 0
        assert len(id2) > 0
        assert id1 != id2

    def test_generate_entity_id(self) -> None:
        """Test real entity ID generation."""
        entity_id = FlextApiUtilities.generate_entity_id()

        assert isinstance(entity_id, str)
        assert len(entity_id) > 0
        assert entity_id.startswith("entity_")

    def test_generate_correlation_id(self) -> None:
        """Test real correlation ID generation."""
        corr_id = FlextApiUtilities.generate_correlation_id()

        assert isinstance(corr_id, str)
        assert len(corr_id) > 0

    def test_generate_timestamp(self) -> None:
        """Test real timestamp generation."""
        timestamp1 = FlextApiUtilities.generate_timestamp()
        timestamp2 = FlextApiUtilities.generate_timestamp()

        assert isinstance(timestamp1, str)
        assert isinstance(timestamp2, str)
        assert timestamp1 != timestamp2

        # Should be parseable as datetime
        parsed = datetime.fromisoformat(timestamp1)
        assert isinstance(parsed, datetime)

    def test_generate_iso_timestamp(self) -> None:
        """Test real ISO timestamp generation."""
        iso_ts = FlextApiUtilities.generate_iso_timestamp()

        assert isinstance(iso_ts, str)
        assert "T" in iso_ts
        assert iso_ts.endswith(("+00:00", "Z"))

    def test_parse_iso_timestamp(self) -> None:
        """Test real ISO timestamp parsing."""
        iso_ts = FlextApiUtilities.generate_iso_timestamp()
        parsed = FlextApiUtilities.parse_iso_timestamp(iso_ts)

        assert isinstance(parsed, datetime)
        assert parsed.tzinfo is not None

    def test_safe_int_conversion(self) -> None:
        """Test real safe integer conversion."""
        # Valid conversions
        assert FlextApiUtilities.safe_int_conversion("42") == 42
        assert FlextApiUtilities.safe_int_conversion("0") == 0
        assert FlextApiUtilities.safe_int_conversion("-10") == -10

        # Invalid conversions return None by default
        assert FlextApiUtilities.safe_int_conversion("not_a_number") is None
        assert FlextApiUtilities.safe_int_conversion("") is None
        assert FlextApiUtilities.safe_int_conversion("12.34") is None

    def test_safe_int_conversion_with_default(self) -> None:
        """Test real safe integer conversion with default value."""
        assert FlextApiUtilities.safe_int_conversion_with_default("42", 0) == 42
        assert FlextApiUtilities.safe_int_conversion_with_default("invalid", 999) == 999
        assert FlextApiUtilities.safe_int_conversion_with_default("", -1) == -1

    def test_safe_bool_conversion(self) -> None:
        """Test real boolean conversion."""
        # Truthy values
        assert FlextApiUtilities.safe_bool_conversion("true") is True
        assert FlextApiUtilities.safe_bool_conversion("TRUE") is True
        assert FlextApiUtilities.safe_bool_conversion("1") is True
        assert FlextApiUtilities.safe_bool_conversion("yes") is True

        # Falsy values
        assert FlextApiUtilities.safe_bool_conversion("false") is False
        assert FlextApiUtilities.safe_bool_conversion("FALSE") is False
        assert FlextApiUtilities.safe_bool_conversion("0") is False
        assert FlextApiUtilities.safe_bool_conversion("no") is False

    def test_safe_json_parse(self) -> None:
        """Test real JSON parsing."""
        # Valid JSON
        valid_result = FlextApiUtilities.safe_json_parse('{"key": "value"}')
        assert isinstance(valid_result, dict)
        assert valid_result == {"key": "value"}

        # Invalid JSON - returns default dict
        invalid_result = FlextApiUtilities.safe_json_parse('{"invalid": json}', {})
        assert isinstance(invalid_result, dict)

    def test_safe_json_stringify(self) -> None:
        """Test real JSON stringification."""
        test_data = {"key": "value", "number": 42}

        result = FlextApiUtilities.safe_json_stringify(test_data)
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result

    def test_is_non_empty_string(self) -> None:
        """Test real string validation."""
        assert FlextApiUtilities.is_non_empty_string("hello") is True
        assert FlextApiUtilities.is_non_empty_string("test with spaces") is True
        assert FlextApiUtilities.is_non_empty_string("") is False
        assert FlextApiUtilities.is_non_empty_string("   ") is False
        assert FlextApiUtilities.is_non_empty_string(None) is False

    def test_clean_text(self) -> None:
        """Test real text cleaning."""
        dirty_text = "  Hello, World!  \n\t"
        clean = FlextApiUtilities.clean_text(dirty_text)

        assert isinstance(clean, str)
        assert clean == "Hello, World!"

    def test_truncate(self) -> None:
        """Test real text truncation."""
        long_text = "This is a very long text that should be truncated"
        truncated = FlextApiUtilities.truncate(long_text, 20)

        assert len(truncated) <= 20
        assert isinstance(truncated, str)

    def test_format_duration(self) -> None:
        """Test real duration formatting."""
        duration_ms = 1500.5
        formatted = FlextApiUtilities.format_duration(duration_ms)

        assert isinstance(formatted, str)
        # Duration of 1500.5 ms = 25 minutes should be formatted as "25.0m"
        assert "25" in formatted
        assert "m" in formatted

    def test_validate_config_real(self) -> None:
        """Test real config validation."""
        valid_config = HttpRequestConfig(
            url="https://api.example.com", method="GET", timeout=30.0
        )

        result = FlextApiUtilities.validate_config(valid_config)
        assert result.success
        assert isinstance(result.value, dict)

    def test_performance_tracking(self) -> None:
        """Test real performance tracking."""
        # Start tracking with current time
        start_time = datetime.now(UTC)
        elapsed = FlextApiUtilities.get_elapsed_time(start_time)
        assert isinstance(elapsed, float)

        # Get performance metrics
        metrics = FlextApiUtilities.get_performance_metrics()
        assert isinstance(metrics, dict)

    def test_http_validator_real(self) -> None:
        """Test real HTTP validation methods."""
        # validation
        url_result = FlextApiUtilities.HttpValidator.validate_url(
            "https://api.example.com"
        )
        assert url_result.success

        invalid_url_result = FlextApiUtilities.HttpValidator.validate_url("not-a-url")
        assert not invalid_url_result.success

        # HTTP method validation
        method_result = FlextApiUtilities.HttpValidator.validate_http_method("GET")
        assert method_result.success

        invalid_method_result = FlextApiUtilities.HttpValidator.validate_http_method(
            "INVALID_METHOD"
        )
        assert not invalid_method_result.success

    def test_response_builder_real(self) -> None:
        """Test real response builder."""
        builder_instance = FlextApiUtilities.ResponseBuilder()
        assert builder_instance is not None

    def test_pagination_builder_real(self) -> None:
        """Test real pagination builder."""
        builder_instance = FlextApiUtilities.PaginationBuilder()
        assert builder_instance is not None

    def test_batch_process_real(self) -> None:
        """Test real batch processing availability."""
        # Test if batch_process method exists
        assert hasattr(FlextApiUtilities, "batch_process")

        def process_item(item: int) -> FlextResult[int]:
            return FlextResult[int].ok(item * 2)

        items = [1, 2, 3, 4, 5]

        # Try to call the method
        results = FlextApiUtilities.batch_process(items, process_item)
        assert results is not None

    def test_constants_integration(self) -> None:
        """Test real constants are available."""
        assert hasattr(FlextApiUtilities, "MIN_PORT")
        assert hasattr(FlextApiUtilities, "MAX_PORT")
        assert isinstance(FlextApiUtilities.MIN_PORT, int)
        assert isinstance(FlextApiUtilities.MAX_PORT, int)
        assert FlextApiUtilities.MIN_PORT > 0
        assert FlextApiUtilities.MAX_PORT > FlextApiUtilities.MIN_PORT
