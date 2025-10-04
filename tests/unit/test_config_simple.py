"""Tests for simplified FlextApiConfig following SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import pytest
from flext_core import FlextConstants
from pydantic import ValidationError

from flext_api import FlextApiConfig


class TestFlextApiConfigSimple:
    """Test simplified FlextApiConfig."""

    def test_config_creation_default(self) -> None:
        """Test config creation with default values."""
        config = FlextApiConfig()
        assert (
            config.api_base_url
            == f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
        )
        assert config.api_timeout == FlextConstants.Network.DEFAULT_TIMEOUT
        assert config.max_retries == FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
        assert config.log_requests is True
        assert config.log_responses is True

    def test_config_creation_custom(self) -> None:
        """Test config creation with custom values."""
        config = FlextApiConfig(
            base_url="https://api.example.com",
            timeout=60,
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
        # CORS settings are instance fields, not class variables
        config = FlextApiConfig(
            cors_origins=["https://example.com"],
            cors_methods=["GET", "POST"],
            cors_headers=["Content-Type"],
        )

        # Test custom CORS values
        assert config.cors_origins == ["https://example.com"]
        assert config.cors_methods == ["GET", "POST"]
        assert config.cors_headers == ["Content-Type"]

    def test_config_validation_success(self) -> None:
        """Test config validation success."""
        config = FlextApiConfig()
        assert config.api_base_url is not None
        assert config.api_timeout > 0
        assert config.max_retries >= 0

    def test_config_validation_pydantic_timeout_error(self) -> None:
        """Test Pydantic validation with invalid timeout."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(timeout=0)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

    def test_config_validation_pydantic_retries_error(self) -> None:
        """Test Pydantic validation with negative max_retries."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(max_retries=-1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

    def test_config_base_url_validation_success(self) -> None:
        """Test base URL validation success."""
        config = FlextApiConfig(base_url="https://api.example.com")
        assert config.api_base_url == "https://api.example.com"

    def test_config_base_url_validation_error(self) -> None:
        """Test base URL with invalid format."""
        config = FlextApiConfig(base_url="invalid-url")
        assert config.api_base_url == "invalid-url"

    def test_config_multiple_instances(self) -> None:
        """Test multiple config instances."""
        config1 = FlextApiConfig(base_url="http://api1.example.com")
        config2 = FlextApiConfig(base_url="http://api2.example.com")

        assert config1 is not config2
        assert config1.api_base_url == "http://api1.example.com"
        assert config2.api_base_url == "http://api2.example.com"

    def test_config_base_settings_inheritance(self) -> None:
        """Test config inheritance from Pydantic BaseSettings."""
        config = FlextApiConfig()
        # Should be a Pydantic model
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")
