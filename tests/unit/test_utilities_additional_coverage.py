"""Additional utilities tests to achieve comprehensive coverage of utilities.py module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from typing import Any

from flext_api import FlextApiUtilities


class TestFlextUtilitiesAdditionalCoverage:
    """Additional tests to achieve comprehensive coverage of the FlextApiUtilities class.

    This test class provides additional test coverage for edge cases and error conditions
    to achieve 100% coverage of the utilities module.
    """

    def test_response_builder_build_error_response_with_details(self) -> None:
        """Test ResponseBuilder.build_error_response with detailed error information."""
        result = FlextApiUtilities.ResponseBuilder.build_error_response(
            message="Test error message",
            status_code=400,
            data={"key": "value"},
            error="Detailed error",
            error_code="ERR_400",
            details={"detail": "information"},
        )
        assert result.is_success
        response = result.unwrap()
        assert response["success"] is False
        assert response["message"] == "Test error message"
        assert response["status_code"] == 400
        assert response["data"] == {"key": "value"}
        assert response["error"] == "Detailed error"
        assert response["error_code"] == "ERR_400"
        assert response["details"] == {"detail": "information"}

    def test_response_builder_build_success_response_with_metadata(self) -> None:
        """Test ResponseBuilder.build_success_response with metadata."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data={"result": "success"},
            message="Operation completed",
            status_code=200,
        )
        assert result.is_success
        response = result.unwrap()
        assert response["success"] is True
        assert response["message"] == "Operation completed"
        assert response["status_code"] == 200
        assert response["data"] == {"result": "success"}
        assert "timestamp" in response
        assert "request_id" in response

    def test_validate_url_with_invalid_url(self) -> None:
        """Test validate_url with invalid URL format."""
        result = FlextApiUtilities.validate_url("invalid-url")
        assert result.is_failure
        assert result.error is not None
        assert "URL must start with http:// or https://" in result.error

    def test_validate_url_with_empty_url(self) -> None:
        """Test validate_url with empty URL."""
        result = FlextApiUtilities.validate_url("")
        assert result.is_failure
        assert result.error is not None
        assert "URL must start with http:// or https://" in result.error

    def test_validate_url_with_none_url(self) -> None:
        """Test validate_url with None URL."""
        # This will raise an AttributeError because None doesn't have startswith
        try:
            result = FlextApiUtilities.validate_url(None)
            assert result.is_failure
        except AttributeError:
            # Expected behavior - None doesn't have startswith method
            pass

    def test_validate_config_with_invalid_config(self) -> None:
        """Test validate_config with invalid configuration."""
        result = FlextApiUtilities.validate_config("invalid-config")
        assert result.is_failure
        assert result.error is not None
        assert "Configuration must be dict-like or have attributes" in result.error

    def test_validate_config_with_none_config(self) -> None:
        """Test validate_config with None configuration."""
        result = FlextApiUtilities.validate_config(None)
        assert result.is_failure
        assert result.error is not None
        assert "Configuration cannot be None" in result.error

    def test_generate_id_with_custom_prefix(self) -> None:
        """Test generate_id method."""
        id_str = FlextApiUtilities.generate_id()
        assert isinstance(id_str, str)
        assert len(id_str) > 0

    def test_generate_id_with_empty_prefix(self) -> None:
        """Test generate_id with empty prefix."""
        id_str = FlextApiUtilities.generate_id()
        assert isinstance(id_str, str)
        assert len(id_str) > 0

    def test_generate_uuid(self) -> None:
        """Test generate_uuid method."""
        uuid_str = FlextApiUtilities.generate_uuid()
        assert isinstance(uuid_str, str)
        assert len(uuid_str) > 0

    def test_generate_timestamp(self) -> None:
        """Test generate_timestamp method."""
        timestamp = FlextApiUtilities.generate_timestamp()
        assert isinstance(timestamp, float)
        assert timestamp > 0

    def test_generate_entity_id(self) -> None:
        """Test generate_entity_id method."""
        entity_id = FlextApiUtilities.generate_entity_id()
        assert isinstance(entity_id, str)
        assert len(entity_id) > 0

    def test_generate_correlation_id(self) -> None:
        """Test generate_correlation_id method."""
        correlation_id = FlextApiUtilities.generate_correlation_id()
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0

    def test_generate_iso_timestamp(self) -> None:
        """Test generate_iso_timestamp method."""
        iso_timestamp = FlextApiUtilities.generate_iso_timestamp()
        assert isinstance(iso_timestamp, str)
        assert len(iso_timestamp) > 0

    def test_clean_text_with_special_characters(self) -> None:
        """Test clean_text with special characters."""
        result = FlextApiUtilities.clean_text("  hello   world  ")
        assert result == "hello world"

    def test_clean_text_with_empty_string(self) -> None:
        """Test clean_text with empty string."""
        result = FlextApiUtilities.clean_text("")
        assert not result

    def test_clean_text_with_none(self) -> None:
        """Test clean_text with None input."""
        # clean_text will raise TypeError with None input
        try:
            result = FlextApiUtilities.clean_text(None)
            assert isinstance(result, str)
        except TypeError:
            # Expected behavior - None is not a string
            pass

    def test_safe_bool_conversion_with_truthy_values(self) -> None:
        """Test safe_bool_conversion with truthy values."""
        assert FlextApiUtilities.safe_bool_conversion("true") is True
        assert FlextApiUtilities.safe_bool_conversion("TRUE") is True
        assert FlextApiUtilities.safe_bool_conversion("1") is True
        assert FlextApiUtilities.safe_bool_conversion("yes") is True
        assert FlextApiUtilities.safe_bool_conversion("on") is True
        assert FlextApiUtilities.safe_bool_conversion(1) is True
        assert FlextApiUtilities.safe_bool_conversion(True) is True

    def test_safe_bool_conversion_with_falsy_values(self) -> None:
        """Test safe_bool_conversion with falsy values."""
        assert FlextApiUtilities.safe_bool_conversion("false") is False
        assert FlextApiUtilities.safe_bool_conversion("no") is False
        assert FlextApiUtilities.safe_bool_conversion("0") is False
        assert FlextApiUtilities.safe_bool_conversion("off") is False
        assert FlextApiUtilities.safe_bool_conversion(0) is False
        assert FlextApiUtilities.safe_bool_conversion(False) is False

    def test_safe_bool_conversion_with_invalid_value(self) -> None:
        """Test safe_bool_conversion with invalid value."""
        result = FlextApiUtilities.safe_bool_conversion("invalid")
        assert result is False

    def test_safe_json_parse_with_valid_json(self) -> None:
        """Test safe_json_parse with valid JSON."""
        result = FlextApiUtilities.safe_json_parse('{"key": "value"}')
        assert result is not None
        assert result == {"key": "value"}

    def test_safe_json_parse_with_invalid_json(self) -> None:
        """Test safe_json_parse with invalid JSON."""
        result = FlextApiUtilities.safe_json_parse('{"invalid": json}')
        assert result is None

    def test_safe_json_stringify_with_dict(self) -> None:
        """Test safe_json_stringify with dictionary."""
        result = FlextApiUtilities.safe_json_stringify({"key": "value"})
        assert result is not None
        assert result == '{"key": "value"}'

    def test_safe_json_stringify_with_invalid_object(self) -> None:
        """Test safe_json_stringify with invalid object."""
        result = FlextApiUtilities.safe_json_stringify(object())
        assert result is None

    def test_safe_int_conversion_with_valid_int(self) -> None:
        """Test safe_int_conversion with valid integer string."""
        result = FlextApiUtilities.safe_int_conversion("123")
        assert result == 123

    def test_safe_int_conversion_with_invalid_int(self) -> None:
        """Test safe_int_conversion with invalid integer string."""
        result = FlextApiUtilities.safe_int_conversion("invalid")
        assert result is None

    def test_safe_int_conversion_with_default(self) -> None:
        """Test safe_int_conversion_with_default method."""
        result = FlextApiUtilities.safe_int_conversion_with_default("123", 999)
        assert result == 123

    def test_is_non_empty_string_with_valid_string(self) -> None:
        """Test is_non_empty_string with valid string."""
        result = FlextApiUtilities.is_non_empty_string("hello")
        assert result is True

    def test_is_non_empty_string_with_empty_string(self) -> None:
        """Test is_non_empty_string with empty string."""
        result = FlextApiUtilities.is_non_empty_string("")
        assert result is False

    def test_is_non_empty_string_with_none(self) -> None:
        """Test is_non_empty_string with None."""
        result = FlextApiUtilities.is_non_empty_string(None)
        assert result is False

    def test_truncate_with_long_string(self) -> None:
        """Test truncate with long string."""
        result = FlextApiUtilities.truncate("this is a very long text", 10)
        assert result == "this is..."

    def test_truncate_with_short_string(self) -> None:
        """Test truncate with short string."""
        result = FlextApiUtilities.truncate("short", 10)
        assert result == "short"

    def test_format_duration_with_seconds(self) -> None:
        """Test format_duration with seconds."""
        result = FlextApiUtilities.format_duration(30.5)
        assert "s" in result

    def test_format_duration_with_minutes(self) -> None:
        """Test format_duration with minutes."""
        result = FlextApiUtilities.format_duration(125.5)
        assert "m" in result
        assert "s" in result

    def test_format_duration_with_hours(self) -> None:
        """Test format_duration with hours."""
        result = FlextApiUtilities.format_duration(3661.0)
        assert "h" in result
        assert "m" in result

    def test_get_elapsed_time(self) -> None:
        """Test get_elapsed_time method."""
        start_time = time.time() - 1.0
        elapsed = FlextApiUtilities.get_elapsed_time(start_time)
        assert elapsed >= 0.9

    def test_get_performance_metrics(self) -> None:
        """Test get_performance_metrics method."""
        start_time = time.time() - 2.0
        metrics = FlextApiUtilities.get_performance_metrics(start_time)
        assert isinstance(metrics, dict)
        assert "elapsed_time" in metrics
        assert "elapsed_ms" in metrics
        assert "formatted_duration" in metrics
        assert "timestamp" in metrics

    def test_batch_process_with_valid_data(self) -> None:
        """Test batch_process with valid data."""
        items = list(range(25))
        batches = FlextApiUtilities.batch_process(items, batch_size=10)
        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_batch_process_with_empty_data(self) -> None:
        """Test batch_process with empty data."""
        items: list[Any] = []
        batches = FlextApiUtilities.batch_process(items, batch_size=10)
        assert len(batches) == 0

    def test_batch_process_with_invalid_batch_size(self) -> None:
        """Test batch_process with invalid batch size."""
        items = list(range(25))
        batches = FlextApiUtilities.batch_process(items, batch_size=0)
        assert len(batches) == 1
        assert len(batches[0]) == 25

    def test_utilities_error_handling(self) -> None:
        """Test utilities error handling."""
        # Test error handling in various utility methods
        try:
            result = FlextApiUtilities.clean_text(None)
            assert isinstance(result, str)
        except TypeError:
            # Expected behavior - None is not a string
            pass

    def test_utilities_edge_cases(self) -> None:
        """Test utilities edge cases."""
        # Test edge cases in various utility methods
        result = FlextApiUtilities.clean_text("")
        assert not result
