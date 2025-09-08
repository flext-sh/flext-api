"""REAL tests for FLEXT API configuration using actual API.

Tests configuration functionality using REAL classes and methods.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api.config import FlextApiConfig


class TestFlextApiConfigReal:
    """Test FlextApiConfig using REAL functionality."""

    def test_api_settings_creation(self) -> None:
        """Test FlextApiConfig creation with real functionality."""
        settings = FlextApiConfig()

        # Test that settings object is created
        assert settings is not None
        assert isinstance(settings, FlextApiConfig)

    def test_client_config_creation(self) -> None:
        """Test client configuration fields."""
        client_config = FlextApiConfig(
            base_url="https://api.example.com", default_timeout=30.0, max_retries=3
        )

        assert client_config.base_url == "https://api.example.com"
        assert client_config.default_timeout == 30.0
        assert client_config.max_retries == 3

    def test_server_config_creation(self) -> None:
        """Test server configuration fields."""
        server_config = FlextApiConfig(host="127.0.0.1", port=8080, workers=4)

        assert server_config.host == "127.0.0.1"
        assert server_config.port == 8080
        assert server_config.workers == 4

    def test_security_config_creation(self) -> None:
        """Test security-related configuration fields."""
        # Test security-related fields available in FlextApiConfig
        config = FlextApiConfig(
            host="127.0.0.1",
            port=8080,
            base_url="https://api.example.com",
            debug=False,
        )

        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.debug is False

    def test_env_config_creation(self) -> None:
        """Test environment-based configuration."""
        env_config = FlextApiConfig(
            host="127.0.0.1",
            port=8080,
            base_url="https://api.example.com",
        )

        assert env_config.host == "127.0.0.1"
        assert env_config.port == 8080
        assert env_config.base_url == "https://api.example.com"

    def test_main_config_creation(self) -> None:
        """Test main configuration creation."""
        main_config = FlextApiConfig(
            host="127.0.0.1",
            port=8080,
            base_url="https://api.example.com",
        )

        assert main_config.host == "127.0.0.1"
        assert main_config.port == 8080

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
