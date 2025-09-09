"""REAL tests for FLEXT API configuration using actual API.

Tests configuration functionality using REAL classes and methods.
Uses flext_tests and our base test utilities for comprehensive testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

# MAXIMUM usage of flext_tests - ACESSO DIRETO - NO ALIASES
from flext_tests import FlextTestsDomains

from flext_api.config import FlextApiConfig


class TestFlextApiConfigReal:
    """Test FlextApiConfig using REAL functionality."""

    def test_api_config_creation(self) -> None:
        """Test FlextApiConfig creation with real functionality."""
        config = FlextApiConfig()

        # Test that config object is created with defaults
        assert config is not None
        assert isinstance(config, FlextApiConfig)
        assert config.host == "127.0.0.1"
        assert config.port == 8000

    def test_client_config_creation(self) -> None:
        """Test FlextApiConfig creation with custom client values."""
        config = FlextApiConfig(
            base_url="https://api.example.com", default_timeout=30.0, max_retries=3
        )

        assert config.base_url == "https://api.example.com"
        assert config.default_timeout == 30.0
        assert config.max_retries == 3

    def test_server_config_creation(self) -> None:
        """Test FlextApiConfig creation with custom server values."""
        config = FlextApiConfig(host="127.0.0.1", port=8080, workers=4)

        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.workers == 4

    def test_security_config_creation(self) -> None:
        """Test security configuration with FlextApiConfig."""
        # Test config with debug mode (closest to security settings available)
        config = FlextApiConfig(
            host="127.0.0.1",
            port=8080,
            base_url="https://api.example.com",
            debug=False,  # Security-relevant setting
        )

        assert config.debug is False
        assert config.base_url.startswith("https://")  # HTTPS for security

    def test_env_config_creation(self) -> None:
        """Test FlextApiConfig creation with environment-style values."""
        config = FlextApiConfig(
            host="127.0.0.1",
            port=8080,
            base_url="https://api.example.com",
        )

        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.base_url == "https://api.example.com"

    def test_main_config_creation(self) -> None:
        """Test main FlextApiConfig creation with multiple parameters."""
        config = FlextApiConfig(
            host="127.0.0.1",
            port=8080,
            base_url="https://api.example.com",
            debug=True,
        )

        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.base_url == "https://api.example.com"
        assert config.debug is True

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        # Valid config
        config = FlextApiConfig(port=8080)
        assert config.port == 8080

        # Invalid port should raise error
        with pytest.raises(ValueError):
            FlextApiConfig(port=99999)  # Port > 65535

    def test_config_serialization(self) -> None:
        """Test config serialization capabilities."""
        config = FlextApiConfig(
            base_url="https://test.example.com", default_timeout=45.0
        )

        # Should be serializable as dict
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["base_url"] == "https://test.example.com"
        assert config_dict["default_timeout"] == 45.0

    def test_config_negative_timeout(self) -> None:
        """Test config validation with invalid values."""
        # Test that validation works
        with pytest.raises((ValueError, TypeError)):
            FlextApiConfig(
                base_url="https://api.example.com",
                default_timeout=-1.0,  # Invalid negative timeout
            )

    def test_config_defaults(self) -> None:
        """Test config default values."""
        # Create config with minimal fields
        config = FlextApiConfig()

        # Should have sensible defaults
        assert config.base_url == "http://localhost:8000"
        assert isinstance(config.default_timeout, (int, float))
        assert config.default_timeout > 0
        assert config.max_retries == 3

    def test_config_with_factory_data(
        self, sample_configuration_data: dict[str, object]
    ) -> None:
        """Test FlextApiConfig creation with factory data."""
        # Use configuration data from FlextTestsDomains
        config_data = FlextTestsDomains.create_configuration()

        # Create config with some values from factory data
        config = FlextApiConfig(
            host=str(config_data.get("host", "127.0.0.1")),
            port=int(config_data.get("port", 8000)),
            base_url="https://api.example.com",
        )

        assert config is not None
        assert isinstance(config, FlextApiConfig)

        # Verify serialization includes expected structure
        config_dict = config.model_dump()
        required_keys = ["host", "port", "base_url", "default_timeout"]

        for key in required_keys:
            assert key in config_dict, f"Missing key {key} in config"
