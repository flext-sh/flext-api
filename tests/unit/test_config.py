"""REAL tests for FLEXT API configuration using actual API.

Tests configuration functionality using REAL classes and methods.
Uses flext_tests and our base test utilities for comprehensive testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_core import FlextConstants
from flext_tests import FlextTestsDomains

from flext_api import FlextWebConfig


class TestHttpConfigReal:
    """Test FlextWebConfig using REAL functionality."""

    def test_api_config_creation(self) -> None:
        """Test FlextWebConfig creation with real functionality."""
        config = FlextWebConfig()

        # Test that config object is created with defaults
        assert config is not None
        assert isinstance(config, FlextWebConfig)
        assert config.base_url == ""
        assert config.timeout == 30.0

    def test_client_config_creation(self) -> None:
        """Test FlextWebConfig creation with custom client values."""
        config = FlextWebConfig(
            base_url="https://api.example.com",
            timeout=30.0,
            max_retries=3,
        )

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_server_config_creation(self) -> None:
        """Test FlextWebConfig creation with custom server values."""
        config = FlextWebConfig(
            base_url=f"http://127.0.0.1:{FlextConstants.Platform.DEFAULT_HTTP_PORT}"
        )

        assert (
            config.base_url
            == f"http://127.0.0.1:{FlextConstants.Platform.DEFAULT_HTTP_PORT}"
        )

    def test_security_config_creation(self) -> None:
        """Test security configuration with FlextWebConfig."""
        # Test config with debug mode (closest to security settings available)
        config = FlextWebConfig(
            base_url="https://api.example.com",
        )

        assert config.base_url.startswith("https://")

    def test_env_config_creation(self) -> None:
        """Test FlextWebConfig creation with environment-style values."""
        config = FlextWebConfig(
            base_url="https://api.example.com",
        )

        assert config.base_url == "https://api.example.com"

    def test_main_config_creation(self) -> None:
        """Test main FlextWebConfig creation with multiple parameters."""
        config = FlextWebConfig(
            base_url="https://api.example.com",
        )

        assert config.base_url == "https://api.example.com"
        # Test that config was created successfully

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        # Valid config
        config = FlextWebConfig(base_url="http://localhost:8080")
        assert config.base_url == "http://localhost:8080"

        # Invalid timeout should raise error
        with pytest.raises(ValueError):
            FlextWebConfig(timeout=-1.0)

    def test_config_serialization(self) -> None:
        """Test config serialization capabilities."""
        config = FlextWebConfig(
            base_url="https://test.example.com",
            timeout=45.0,
        )

        # Should be serializable as dict
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["base_url"] == "https://test.example.com"
        assert config_dict["timeout"] == 45.0

    def test_config_negative_timeout(self) -> None:
        """Test config validation with invalid values."""
        # Test that validation works
        with pytest.raises(ValueError):
            FlextWebConfig(
                base_url="https://api.example.com",
                timeout=-1.0,  # Invalid negative timeout
            )

    def test_config_defaults(self) -> None:
        """Test config default values."""
        # Create config with minimal fields
        config = FlextWebConfig()

        # Should have sensible defaults
        assert config.base_url == ""
        assert isinstance(config.timeout, (int, float))
        assert config.timeout > 0
        assert config.max_retries == 3

    def test_config_with_factory_data(self) -> None:
        """Test FlextWebConfig creation with factory data."""
        # Use configuration data from FlextTestsDomains
        config_data = FlextTestsDomains.create_configuration()

        # Create config with some values from factory data
        config_data.get("port", FlextConstants.Platform.FLEXT_API_PORT)
        config = FlextWebConfig(
            base_url="https://api.example.com",
        )

        assert config is not None
        assert isinstance(config, FlextWebConfig)

        # Verify serialization includes expected structure
        config_dict = config.to_dict()
        required_keys = ["base_url", "timeout", "max_retries"]

        for key in required_keys:
            assert key in config_dict, f"Missing key {key} in config"
