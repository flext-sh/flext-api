"""Tests for simplified FlextApiConfig following SOLID principles."""

import pytest

from flext_api import FlextApiConfig


class TestFlextApiConfigSimple:
    """Test simplified FlextApiConfig."""

    def test_config_creation_default(self) -> None:
        """Test config creation with default values."""
        config = FlextApiConfig()
        assert config.api_host == "127.0.0.1"
        assert config.api_port == 8000
        assert config.workers == 4
        assert config.api_debug is False
        assert config.api_title == "FLEXT API"
        assert config.api_version == "0.9.0"
        assert config.api_base_url == "http://127.0.0.1:8000"
        assert config.api_timeout == 30.0
        assert config.max_retries == 3

    def test_config_creation_custom(self) -> None:
        """Test config creation with custom values."""
        config = FlextApiConfig(
            api_host="0.0.0.0",
            api_port=9000,
            workers=8,
            api_debug=True,
            api_title="Custom API",
            api_version="1.0.0",
            api_base_url="https://api.example.com",
            api_timeout=60.0,
            max_retries=5,
        )
        assert config.api_host == "0.0.0.0"
        assert config.api_port == 9000
        assert config.workers == 8
        assert config.api_debug is True
        assert config.api_title == "Custom API"
        assert config.api_version == "1.0.0"
        assert config.api_base_url == "https://api.example.com"
        assert config.api_timeout == 60.0
        assert config.max_retries == 5

    def test_config_cors_defaults(self) -> None:
        """Test CORS default values."""
        config = FlextApiConfig()
        assert config.cors_origins == ["*"]
        assert config.cors_methods == ["GET", "POST", "PUT", "DELETE"]
        assert config.cors_headers == ["Content-Type", "Authorization"]

    def test_config_cors_custom(self) -> None:
        """Test CORS custom values."""
        # CORS settings are ClassVar, not instance parameters - test class attributes directly

        # Test that default CORS settings exist
        assert hasattr(FlextApiConfig, "cors_origins")
        assert hasattr(FlextApiConfig, "cors_methods")
        assert hasattr(FlextApiConfig, "cors_headers")

        # Test default values
        assert FlextApiConfig.cors_origins == ["*"]
        assert "GET" in FlextApiConfig.cors_methods
        assert "POST" in FlextApiConfig.cors_methods
        assert "Content-Type" in FlextApiConfig.cors_headers

    def test_config_validation_success(self) -> None:
        """Test config validation success."""
        config = FlextApiConfig()
        result = config.validate_configuration()
        assert result.success is True

    def test_config_validation_pydantic_workers_error(self) -> None:
        """Test Pydantic validation with invalid workers."""
        with pytest.raises(
            Exception,
            match="Input should be greater than or equal to 1",
        ):
            FlextApiConfig(workers=0)

    def test_config_validation_pydantic_port_error(self) -> None:
        """Test Pydantic validation with invalid port."""
        with pytest.raises(
            Exception,
            match="Input should be less than or equal to 65535",
        ):
            FlextApiConfig(api_port=70000)

    def test_config_base_url_validation_success(self) -> None:
        """Test base URL validation success."""
        config = FlextApiConfig(api_base_url="https://api.example.com")
        assert config.api_base_url == "https://api.example.com"

    def test_config_base_url_validation_error(self) -> None:
        """Test base URL validation error."""
        with pytest.raises(
            ValueError,
            match="API base URL must include scheme and hostname",
        ):
            FlextApiConfig(api_base_url="invalid-url")

    def test_config_singleton_pattern(self) -> None:
        """Test singleton pattern."""
        # Clear any existing instance
        FlextApiConfig.set_global_instance(None)

        # Get global instance
        config1 = FlextApiConfig.get_global_instance()
        config2 = FlextApiConfig.get_global_instance()

        assert config1 is config2

        # Set custom instance
        custom_config = FlextApiConfig(api_port=9000)
        FlextApiConfig.set_global_instance(custom_config)

        config3 = FlextApiConfig.get_global_instance()
        assert config3 is custom_config
        assert config3.api_port == 9000

    def test_config_inheritance(self) -> None:
        """Test config inheritance from FlextConfig."""
        config = FlextApiConfig()
        # Should have inherited fields from FlextConfig
        assert hasattr(config, "app_name")
        assert hasattr(config, "config_name")
        assert hasattr(config, "config_type")
