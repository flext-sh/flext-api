"""Core functionality tests for FlextConfig to increase coverage."""

import pytest
from flext_core import FlextConfig

from flext_api.config import FlextApiConfig


class TestFlextApiConfig:
    """Test FlextApiConfig comprehensive functionality."""

    def setup_method(self) -> None:
        """Clear config before each test."""
        FlextConfig.clear_global_instance()

    def teardown_method(self) -> None:
        """Clear config after each test."""
        FlextConfig.clear_global_instance()

    def test_config_creation_defaults(self) -> None:
        """Test config creation with default values."""
        config = FlextConfig.get_global_instance()

        # Test defaults exist and are accessible
        assert hasattr(config, "app_name")
        assert hasattr(config, "environment")
        assert hasattr(config, "debug")
        assert hasattr(config, "max_workers")
        assert hasattr(config, "timeout_seconds")

        # Test default types
        assert isinstance(config.app_name, str)
        assert isinstance(config.environment, str)
        assert isinstance(config.debug, bool)
        assert isinstance(config.max_workers, int)
        assert isinstance(config.timeout_seconds, int)

    def test_config_field_info(self) -> None:
        """Test config field information and constraints."""
        config = FlextConfig.get_global_instance()

        # Test that config has reasonable defaults
        assert config.max_workers > 0, "max_workers should be positive"
        assert config.timeout_seconds > 0, "timeout_seconds should be positive"
        assert len(config.app_name) > 0, "app_name should not be empty"
        assert len(config.environment) > 0, "environment should not be empty"

    def test_config_timeout_validation(self) -> None:
        """Test timeout validation scenarios."""
        config = FlextConfig.get_global_instance()

        # Test accessing timeout field - should work without errors
        timeout_value = config.timeout_seconds
        assert isinstance(timeout_value, int)
        assert timeout_value >= 0

    def test_config_base_url_validation(self) -> None:
        """Test base URL validation if present."""
        config = FlextConfig.get_global_instance()

        # Test that config can be accessed - basic functionality
        if hasattr(config, "base_url"):
            base_url = config.base_url
            assert isinstance(base_url, str)

    def test_config_validation_error_details(self) -> None:
        """Test validation error scenarios for comprehensive coverage."""
        # Test configuration validation with invalid values
        with pytest.raises(Exception, match=r"(port|validation)"):
            FlextApiConfig(port=99999)  # Invalid port
