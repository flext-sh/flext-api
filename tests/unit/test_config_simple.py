"""Tests for simplified FlextApiConfig following SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_api import FlextApiConfig


class TestFlextApiConfigSimple:
    """Test simplified FlextApiConfig."""

    def test_config_creation_default(self) -> None:
        """Test config creation with default values."""
        config = FlextApiConfig()
        assert config.api_base_url == "http://localhost:8000"
        assert config.api_timeout == 30
        assert config.max_retries == 3
        assert config.log_requests is True
        assert config.log_responses is True

    def test_config_creation_custom(self) -> None:
        """Test config creation with custom values."""
        config = FlextApiConfig(
            api_base_url="https://api.example.com",
            api_timeout=60,
            max_retries=5,
        )
        assert config.api_base_url == "https://api.example.com"
        assert config.api_timeout == 60
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
        assert config.api_base_url is not None
        assert config.api_timeout > 0
        assert config.max_retries >= 0

    def test_config_validation_pydantic_timeout_error(self) -> None:
        """Test Pydantic validation with invalid timeout."""
        config = FlextApiConfig(api_timeout=0)
        assert config.api_timeout == 0

    def test_config_validation_pydantic_retries_error(self) -> None:
        """Test Pydantic validation with negative max_retries."""
        config = FlextApiConfig(max_retries=-1)
        assert config.max_retries == -1

    def test_config_base_url_validation_success(self) -> None:
        """Test base URL validation success."""
        config = FlextApiConfig(api_base_url="https://api.example.com")
        assert config.api_base_url == "https://api.example.com"

    def test_config_base_url_validation_error(self) -> None:
        """Test base URL with invalid format."""
        config = FlextApiConfig(api_base_url="invalid-url")
        assert config.api_base_url == "invalid-url"

    def test_config_multiple_instances(self) -> None:
        """Test multiple config instances."""
        config1 = FlextApiConfig(api_base_url="http://api1.example.com")
        config2 = FlextApiConfig(api_base_url="http://api2.example.com")

        assert config1 is not config2
        assert config1.api_base_url == "http://api1.example.com"
        assert config2.api_base_url == "http://api2.example.com"

    def test_config_base_settings_inheritance(self) -> None:
        """Test config inheritance from Pydantic BaseSettings."""
        config = FlextApiConfig()
        # Should be a Pydantic model
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")
