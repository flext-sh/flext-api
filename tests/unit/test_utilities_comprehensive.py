"""Comprehensive tests for utilities module to improve coverage."""

import time
from typing import cast

from flext_api import FlextApiUtilities


class TestFlextApiUtilitiesComprehensive:
    """Comprehensive tests for FlextApiUtilities to achieve high coverage."""

    def test_response_builder_error_response(self) -> None:
        """Test ResponseBuilder.build_error_response method."""
        result = FlextApiUtilities.ResponseBuilder.build_error_response("Test error")
        assert result.is_success  # This returns success with error data
        assert cast("dict", result.data)["success"] is False
        assert cast("dict", result.data)["message"] == "Test error"

    def test_response_builder_success_response(self) -> None:
        """Test ResponseBuilder.build_success_response method."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data={"id": 1, "name": "test"}
        )
        assert result.is_success
        assert cast("dict", result.data)["data"] == {"id": 1, "name": "test"}
        assert cast("dict", result.data)["success"] is True

    def test_validate_url(self) -> None:
        """Test validate_url method."""
        result = FlextApiUtilities.validate_url("https://api.example.com")
        assert result.is_success

        result = FlextApiUtilities.validate_url("not-a-url")
        assert result.is_failure

    def test_validate_config(self) -> None:
        """Test validate_config method."""
        config = {"base_url": "https://api.example.com", "timeout": 30}
        result = FlextApiUtilities.validate_config(config)
        assert result.is_success
        # The config gets additional metadata
        assert cast("dict", result.data)["base_url"] == "https://api.example.com"
        assert cast("dict", result.data)["timeout"] == 30

        result = FlextApiUtilities.validate_config("invalid")
        assert result.is_failure

    def test_generate_id(self) -> None:
        """Test generate_id method."""
        id1 = FlextApiUtilities.generate_id()
        id2 = FlextApiUtilities.generate_id()

        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2

    def test_generate_uuid(self) -> None:
        """Test generate_uuid method."""
        uuid1 = FlextApiUtilities.generate_uuid()
        uuid2 = FlextApiUtilities.generate_uuid()

        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert uuid1 != uuid2
        assert len(uuid1) == 36

    def test_generate_timestamp(self) -> None:
        """Test generate_timestamp method."""
        timestamp = FlextApiUtilities.generate_timestamp()

        assert isinstance(timestamp, float)
        assert timestamp > 0
        assert timestamp <= time.time()

    def test_generate_entity_id(self) -> None:
        """Test generate_entity_id method."""
        entity_id = FlextApiUtilities.generate_entity_id()

        assert isinstance(entity_id, str)
        assert len(entity_id) > 0
        # It generates a UUID, not necessarily starting with "entity_"

    def test_generate_correlation_id(self) -> None:
        """Test generate_correlation_id method."""
        corr_id = FlextApiUtilities.generate_correlation_id()

        assert isinstance(corr_id, str)
        assert len(corr_id) > 0
        assert corr_id.startswith("corr_")

    def test_generate_iso_timestamp(self) -> None:
        """Test generate_iso_timestamp method."""
        iso_timestamp = FlextApiUtilities.generate_iso_timestamp()

        assert isinstance(iso_timestamp, str)
        assert "T" in iso_timestamp

    def test_clean_text(self) -> None:
        """Test clean_text method."""
        result = FlextApiUtilities.clean_text("  Hello   World  ")
        assert result == "Hello World"

        result = FlextApiUtilities.clean_text("")
        assert not result

    def test_safe_bool_conversion(self) -> None:
        """Test safe_bool_conversion method."""
        assert FlextApiUtilities.safe_bool_conversion(True) is True
        assert FlextApiUtilities.safe_bool_conversion(1) is True
        assert FlextApiUtilities.safe_bool_conversion("true") is True
        assert FlextApiUtilities.safe_bool_conversion(False) is False
        assert FlextApiUtilities.safe_bool_conversion(0) is False
        assert FlextApiUtilities.safe_bool_conversion("false") is False

    def test_safe_json_parse(self) -> None:
        """Test safe_json_parse method."""
        result = FlextApiUtilities.safe_json_parse('{"key": "value"}')
        assert result.is_success
        assert result.data == {"key": "value"}

        result = FlextApiUtilities.safe_json_parse("invalid json")
        assert result.is_failure

    def test_safe_json_stringify(self) -> None:
        """Test safe_json_stringify method."""
        result = FlextApiUtilities.safe_json_stringify({"key": "value"})
        assert result.is_success
        assert result.data == '{"key": "value"}'

    def test_safe_int_conversion(self) -> None:
        """Test safe_int_conversion method."""
        assert FlextApiUtilities.safe_int_conversion("123") == 123
        assert FlextApiUtilities.safe_int_conversion(456) == 456
        assert FlextApiUtilities.safe_int_conversion("abc") is None

    def test_safe_int_conversion_with_default(self) -> None:
        """Test safe_int_conversion_with_default method."""
        assert FlextApiUtilities.safe_int_conversion_with_default("123", 0) == 123
        assert FlextApiUtilities.safe_int_conversion_with_default("abc", 999) == 999

    def test_is_non_empty_string(self) -> None:
        """Test is_non_empty_string method."""
        assert FlextApiUtilities.is_non_empty_string("hello") is True
        assert FlextApiUtilities.is_non_empty_string("") is False
        assert FlextApiUtilities.is_non_empty_string(None) is False

    def test_truncate(self) -> None:
        """Test truncate method."""
        result = FlextApiUtilities.truncate("Hello World", 5)
        assert result == "He..."  # Actual implementation truncates to 2 chars + "..."

        result = FlextApiUtilities.truncate("Hi", 10)
        assert result == "Hi"

    def test_format_duration(self) -> None:
        """Test format_duration method."""
        result = FlextApiUtilities.format_duration(45.5)
        assert "45.5s" in result

        result = FlextApiUtilities.format_duration(125.0)
        assert "2m" in result and "5.0s" in result  # Actual format includes decimal

    def test_get_elapsed_time(self) -> None:
        """Test get_elapsed_time method."""
        start_time = time.time() - 1.0

        elapsed = FlextApiUtilities.get_elapsed_time(start_time)
        assert isinstance(elapsed, float)
        assert elapsed >= 1.0

    def test_get_performance_metrics(self) -> None:
        """Test get_performance_metrics method."""
        start_time = time.time() - 1.0

        metrics = FlextApiUtilities.get_performance_metrics(start_time)

        assert isinstance(metrics, dict)
        assert "elapsed_time" in metrics
        assert "formatted_duration" in metrics

    def test_batch_process(self) -> None:
        """Test batch_process method."""
        items = list(range(25))

        batches = FlextApiUtilities.batch_process(items, batch_size=10)

        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5
