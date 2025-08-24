"""Comprehensive tests for FLEXT API configuration.

Tests all configuration functionality with 100% coverage including:
- FlextApiSettings creation and validation
- Field validators and constraints
- Factory function error handling
- Environment variable integration
- Configuration serialization and validation

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_core import FlextConstants, FlextResult, FlextSettings
from pydantic import ValidationError

from flext_api import FlextApiSettings, create_api_settings


class TestFlextApiSettings:
    """Test FlextApiSettings class with all field validation."""

    def test_settings_creation_defaults(self) -> None:
        """Test settings creation with default values."""
        settings = FlextApiSettings()

        assert settings.api_host == "localhost"
        assert settings.api_port == FlextConstants.Platform.FLEXT_API_PORT
        assert settings.api_workers == 1
        assert settings.default_timeout == 30
        assert settings.max_retries == 3
        assert settings.enable_caching is True
        assert settings.cache_ttl == 300

    def test_settings_creation_with_values(self) -> None:
        """Test settings creation with custom values."""
        settings = FlextApiSettings.model_validate({
            "api_host": "api.example.com",
            "api_port": 8080,
            "api_workers": 4,
            "default_timeout": 60,
            "max_retries": 5,
            "enable_caching": False,
            "cache_ttl": 600,
        })

        assert settings.api_host == "api.example.com"
        assert settings.api_port == 8080
        assert settings.api_workers == 4
        assert settings.default_timeout == 60
        assert settings.max_retries == 5
        assert settings.enable_caching is False
        assert settings.cache_ttl == 600

    def test_port_validation_valid_port(self) -> None:
        """Test port validation with valid ports."""
        # Test minimum valid port
        settings = FlextApiSettings.model_validate({"api_port": 1})
        assert settings.api_port == 1

        # Test maximum valid port
        max_port = FlextConstants.Platform.MAX_PORT_NUMBER
        settings = FlextApiSettings.model_validate({"api_port": max_port})
        assert settings.api_port == max_port

        # Test common valid port
        settings = FlextApiSettings.model_validate({"api_port": 8080})
        assert settings.api_port == 8080

    def test_port_validation_invalid_port_zero(self) -> None:
        """Test port validation fails with port 0."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiSettings.model_validate({"api_port": 0})

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "greater_than_equal"

    def test_port_validation_invalid_port_negative(self) -> None:
        """Test port validation fails with negative port."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiSettings.model_validate({"api_port": -1})

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "greater_than_equal"

    def test_port_validation_invalid_port_too_high(self) -> None:
        """Test port validation fails with port too high."""
        invalid_port = FlextConstants.Platform.MAX_PORT_NUMBER + 1
        with pytest.raises(ValidationError) as exc_info:
            FlextApiSettings.model_validate({"api_port": invalid_port})

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "less_than_equal"

    def test_port_validator_method_directly(self) -> None:
        """Test port validator method directly."""
        # Valid port
        result = FlextApiSettings.validate_port(8080)
        assert result == 8080

        # Invalid port - should raise ValueError
        with pytest.raises(ValueError, match="Port must be between") as exc_info:
            FlextApiSettings.validate_port(0)

        error_message = str(exc_info.value)
        expected_message = (
            f"Port must be between 1 and {FlextConstants.Platform.MAX_PORT_NUMBER}"
        )
        assert error_message == expected_message

    def test_api_workers_validation(self) -> None:
        """Test api_workers field validation."""
        # Valid values
        settings = FlextApiSettings.model_validate({"api_workers": 1})
        assert settings.api_workers == 1

        settings = FlextApiSettings.model_validate({"api_workers": 8})
        assert settings.api_workers == 8

        # Invalid value - zero or negative
        with pytest.raises(ValidationError):
            FlextApiSettings.model_validate({"api_workers": 0})

        with pytest.raises(ValidationError):
            FlextApiSettings.model_validate({"api_workers": -1})

    def test_default_timeout_validation(self) -> None:
        """Test default_timeout field validation."""
        # Valid values
        settings = FlextApiSettings.model_validate({"default_timeout": 1})
        assert settings.default_timeout == 1

        settings = FlextApiSettings.model_validate({"default_timeout": 300})
        assert settings.default_timeout == 300

        # Invalid value - zero or negative
        with pytest.raises(ValidationError):
            FlextApiSettings.model_validate({"default_timeout": 0})

        with pytest.raises(ValidationError):
            FlextApiSettings.model_validate({"default_timeout": -1})

    def test_max_retries_validation(self) -> None:
        """Test max_retries field validation."""
        # Valid values including zero
        settings = FlextApiSettings.model_validate({"max_retries": 0})
        assert settings.max_retries == 0

        settings = FlextApiSettings.model_validate({"max_retries": 5})
        assert settings.max_retries == 5

        # Invalid value - negative
        with pytest.raises(ValidationError):
            FlextApiSettings.model_validate({"max_retries": -1})

    def test_cache_ttl_validation(self) -> None:
        """Test cache_ttl field validation."""
        # Valid values including zero
        settings = FlextApiSettings.model_validate({"cache_ttl": 0})
        assert settings.cache_ttl == 0

        settings = FlextApiSettings.model_validate({"cache_ttl": 3600})
        assert settings.cache_ttl == 3600

        # Invalid value - negative
        with pytest.raises(ValidationError):
            FlextApiSettings.model_validate({"cache_ttl": -1})

    def test_real_configuration_creation_with_overrides(self) -> None:
        """Test REAL configuration creation with explicit overrides - NO MOCKS."""
        # Test REAL configuration with explicit parameters
        config_overrides = {
            "api_host": "prod.api.com",
            "api_port": 9000,
            "api_workers": 8,
            "default_timeout": 120,
            "max_retries": 10,
            "enable_caching": False,
            "cache_ttl": 1800,
        }

        # Create REAL settings with overrides
        settings = FlextApiSettings.model_validate({**config_overrides})

        # Validate REAL configuration values
        assert settings.api_host == "prod.api.com"
        assert settings.api_port == 9000
        assert settings.api_workers == 8
        assert settings.default_timeout == 120
        assert settings.max_retries == 10
        assert settings.enable_caching is False
        assert settings.cache_ttl == 1800

        # Test REAL business rules validation
        validation_result = settings.validate_business_rules()
        assert validation_result.success

    def test_settings_serialization(self) -> None:
        """Test settings can be serialized and deserialized."""
        original_settings = FlextApiSettings.model_validate({
            "api_host": "test.com",
            "api_port": 8080,
            "api_workers": 2,
        })

        # Test model_dump (Pydantic v2)
        data = original_settings.model_dump()
        assert isinstance(data, dict)
        assert data["api_host"] == "test.com"
        assert data["api_port"] == 8080

        # Test reconstruction from dict
        new_settings = FlextApiSettings.model_validate({**data})
        assert new_settings.api_host == original_settings.api_host
        assert new_settings.api_port == original_settings.api_port
        assert new_settings.api_workers == original_settings.api_workers


class TestCreateApiSettingsFactory:
    """Test create_api_settings factory function."""

    def test_create_api_settings_no_overrides(self) -> None:
        """Test factory function with no overrides."""
        result = create_api_settings()

        assert isinstance(result, FlextResult)
        assert result.success
        assert isinstance(result.value, FlextApiSettings)

        settings = result.value
        assert settings.api_host == "localhost"
        assert settings.api_port == FlextConstants.Platform.FLEXT_API_PORT

    def test_create_api_settings_with_valid_overrides(self) -> None:
        """Test factory function with valid overrides."""
        result = create_api_settings(
            api_host="custom.host.com",
            api_port=9999,
            api_workers=6,
        )

        assert result.success
        settings = result.value
        assert settings.api_host == "custom.host.com"
        assert settings.api_port == 9999
        assert settings.api_workers == 6

    def test_create_api_settings_with_invalid_overrides(self) -> None:
        """Test factory function with invalid overrides."""
        result = create_api_settings(api_port=-1)

        assert result.is_failure
        assert result.error is not None
        assert "Failed to create settings" in result.error
        assert isinstance(result.error, str)

    def test_create_api_settings_with_invalid_port_validation(self) -> None:
        """Test factory function with port that fails custom validation."""
        invalid_port = FlextConstants.Platform.MAX_PORT_NUMBER + 1000
        result = create_api_settings(api_port=invalid_port)

        assert result.is_failure
        assert result.error is not None
        assert result.error is not None
        assert "Failed to create settings" in result.error

    def test_create_api_settings_mixed_valid_invalid(self) -> None:
        """Test factory function with mix of valid and invalid settings."""
        result = create_api_settings(
            api_host="valid.host.com",  # Valid
            api_port=-100,  # Invalid
        )

        assert result.is_failure
        assert result.error is not None
        assert "Failed to create settings" in result.error

    def test_create_api_settings_empty_dict_override(self) -> None:
        """Test factory function handles empty overrides correctly."""
        result = create_api_settings()

        assert result.success
        settings = result.value
        # Should have all default values
        assert settings.api_host == "localhost"
        assert settings.api_port == FlextConstants.Platform.FLEXT_API_PORT

    def test_create_api_settings_type_conversion(self) -> None:
        """Test factory function handles type conversion correctly."""
        result = create_api_settings(
            api_port="8080",  # String that should convert to int
            api_workers="4",  # String that should convert to int
            enable_caching="true",  # String that should convert to bool
        )

        assert result.success
        settings = result.value
        assert settings.api_port == 8080
        assert settings.api_workers == 4
        assert settings.enable_caching is True

    def test_create_api_settings_return_type_verification(self) -> None:
        """Test factory function returns correct FlextResult type."""
        result = create_api_settings()

        # Test FlextResult interface
        assert hasattr(result, "success")
        assert hasattr(result, "is_failure")
        assert hasattr(result, "value")
        assert hasattr(result, "error")

        # Test success case
        assert result.success is True
        assert result.is_failure is False
        assert result.value is not None
        assert result.error is None

        # Test failure case
        failed_result = create_api_settings(api_port="invalid")
        assert failed_result.success is False
        assert failed_result.is_failure is True
        assert failed_result.error is not None
        # Cannot access .value on failed result - this would raise TypeError


class TestFlextApiSettingsIntegration:
    """Integration tests for FlextApiSettings with flext-core patterns."""

    def test_flext_base_settings_inheritance(self) -> None:
        """Test FlextApiSettings properly inherits from FlextSettings."""
        settings = FlextApiSettings()
        assert isinstance(settings, FlextSettings)

    def test_create_with_validation_method(self) -> None:
        """Test inherited create_with_validation method works correctly."""
        # Test success case
        result = FlextApiSettings.create_with_validation(
            {
                "api_host": "test.com",
                "api_port": 8080,
            },
        )

        assert result.success
        assert isinstance(result.value, FlextApiSettings)
        assert result.value.api_host == "test.com"
        assert result.value.api_port == 8080

    def test_create_with_validation_failure(self) -> None:
        """Test create_with_validation handles failures correctly."""
        result = FlextApiSettings.create_with_validation(
            {
                "api_port": -1,  # Invalid port
            },
        )

        assert result.is_failure
        assert result.error is not None
        assert "Failed to create settings" in result.error

    def test_config_env_prefix(self) -> None:
        """Test Config class env_prefix is set correctly."""
        assert FlextApiSettings.model_config["env_prefix"] == "FLEXT_API_"

    def test_field_descriptions(self) -> None:
        """Test all fields have proper descriptions."""
        fields = FlextApiSettings.model_fields

        assert fields["api_host"].description == "API server host"
        assert fields["api_port"].description == "API server port"
        assert fields["api_workers"].description == "Number of worker processes"
        assert fields["default_timeout"].description == "Default HTTP timeout"
        assert fields["max_retries"].description == "Maximum retry attempts"
        assert fields["enable_caching"].description == "Enable response caching"
        assert fields["cache_ttl"].description == "Cache TTL in seconds"
