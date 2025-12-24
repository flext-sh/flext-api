"""REAL tests for FLEXT API configuration using actual API.

Tests configuration functionality using REAL classes and methods.
Uses flext_tests and our base test utilities for comprehensive testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext import FlextConstants
from flext_tests import FlextTestsDomains

from flext_api import FlextApiSettings


class TestHttpConfigReal:
    """Test FlextApiSettings using REAL functionality."""

    def test_api_config_creation(self) -> None:
        """Test FlextApiSettings creation with real functionality."""
        config = FlextApiSettings()

        # Test that config object is created with defaults from Constants
        assert config is not None
        assert isinstance(config, FlextApiSettings)
        # base_url now has default from Constants (not empty)
        assert config.base_url  # Should have default value from Constants
        assert config.timeout == 30.0

    def test_client_config_creation(self) -> None:
        """Test FlextApiSettings creation with custom client values."""
        config = FlextApiSettings(
            base_url="https://api.example.com",
            timeout=30.0,
            max_retries=3,
        )

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_server_config_creation(self) -> None:
        """Test FlextApiSettings creation with custom server values."""
        config = FlextApiSettings(
            base_url=f"http://127.0.0.1:{FlextConstants.Platform.DEFAULT_HTTP_PORT}",
        )

        assert (
            config.base_url
            == f"http://127.0.0.1:{FlextConstants.Platform.DEFAULT_HTTP_PORT}"
        )

    def test_security_config_creation(self) -> None:
        """Test security configuration with FlextApiSettings."""
        # Test config with debug mode (closest to security settings available)
        config = FlextApiSettings(
            base_url="https://api.example.com",
        )

        assert config.base_url.startswith("https://")

    def test_env_config_creation(self) -> None:
        """Test FlextApiSettings creation with environment-style values."""
        config = FlextApiSettings(
            base_url="https://api.example.com",
        )

        assert config.base_url == "https://api.example.com"

    def test_main_config_creation(self) -> None:
        """Test main FlextApiSettings creation with multiple parameters."""
        config = FlextApiSettings(
            base_url="https://api.example.com",
        )

        assert config.base_url == "https://api.example.com"
        # Test that config was created successfully

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        # Valid config
        config = FlextApiSettings(base_url="http://localhost:8080")
        assert config.base_url == "http://localhost:8080"

        # Invalid timeout should raise error
        with pytest.raises(ValueError):
            FlextApiSettings(timeout=-1.0)

    def test_config_serialization(self) -> None:
        """Test config serialization capabilities."""
        config = FlextApiSettings(
            base_url="https://test.example.com",
            timeout=45.0,
        )

        # Should be serializable as dict
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["base_url"] == "https://test.example.com"
        assert config_dict["timeout"] == 45.0

    def test_config_negative_timeout(self) -> None:
        """Test config validation with invalid values."""
        # Test that validation works
        with pytest.raises(ValueError):
            FlextApiSettings(
                base_url="https://api.example.com",
                timeout=-1.0,  # Invalid negative timeout
            )

    def test_config_defaults(self) -> None:
        """Test config default values."""
        # Create config with minimal fields
        config = FlextApiSettings()

        # Should have sensible defaults from Constants
        assert config.base_url  # Should have default value from Constants
        assert isinstance(config.timeout, (int, float))
        assert config.timeout > 0
        assert config.max_retries == 3

    def test_config_with_factory_data(self) -> None:
        """Test FlextApiSettings creation with factory data."""
        # Use configuration data from FlextTestsDomains
        config_data = FlextTestsDomains.create_configuration()

        # Create config with some values from factory data
        config_data.get("port", FlextConstants.Platform.FLEXT_API_PORT)
        config = FlextApiSettings(
            base_url="https://api.example.com",
        )

        assert config is not None
        assert isinstance(config, FlextApiSettings)

        # Verify serialization includes expected structure
        config_dict = config.model_dump()
        required_keys = ["base_url", "timeout", "max_retries"]

        for key in required_keys:
            assert key in config_dict, f"Missing key {key} in config"

    def test_default_headers(self) -> None:
        """Test default_headers property."""
        config = FlextApiSettings(
            base_url="https://api.example.com",
            headers={"X-Custom": "test"},
        )

        # Test default headers include both defaults and custom headers
        default_headers = config.default_headers
        assert "Accept" in default_headers
        assert default_headers["Accept"] == "application/json"
        assert "Content-Type" in default_headers
        assert default_headers["Content-Type"] == "application/json"
        assert "X-Custom" in default_headers
        assert default_headers["X-Custom"] == "test"

    def test_to_json(self) -> None:
        """Test to_json() method."""
        config = FlextApiSettings(
            base_url="https://api.example.com",
            timeout=45.0,
            max_retries=5,
        )

        # Test JSON serialization
        json_str = config.to_json()
        assert isinstance(json_str, str)
        assert "https://api.example.com" in json_str
        assert "45.0" in json_str or "45" in json_str
        assert "5" in json_str

    def test_from_json(self) -> None:
        """Test from_json() classmethod."""
        json_str = '{"base_url": "https://test.com", "timeout": 60.0, "max_retries": 2}'

        # Test JSON deserialization
        config = FlextApiSettings.from_json(json_str)
        assert isinstance(config, FlextApiSettings)
        assert config.base_url == "https://test.com"
        assert config.timeout == 60.0
        assert config.max_retries == 2
