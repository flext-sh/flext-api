"""REAL tests for FLEXT API configuration using actual API.

Tests configuration functionality using REAL classes and methods.
"""

from __future__ import annotations

import pytest

from flext_api.config import FlextApiConfig


class TestFlextApiConfigReal:
    """Test FlextApiConfig using REAL functionality."""

    def test_api_settings_creation(self) -> None:
        """Test ApiSettings creation with real functionality."""
        settings = FlextApiConfig.ApiSettings()

        # Test that settings object is created
        assert settings is not None
        assert isinstance(settings, FlextApiConfig.ApiSettings)

    def test_client_config_creation(self) -> None:
        """Test ClientConfig creation."""
        client_config = FlextApiConfig.ClientConfig(
            base_url="https://api.example.com", timeout=30.0, max_retries=3
        )

        assert client_config.base_url == "https://api.example.com"
        assert client_config.timeout == 30.0
        assert client_config.max_retries == 3

    def test_server_config_creation(self) -> None:
        """Test ServerConfig creation."""
        server_config = FlextApiConfig.ServerConfig(
            host="127.0.0.1", port=8080, workers=4
        )

        assert server_config.host == "127.0.0.1"
        assert server_config.port == 8080
        assert server_config.workers == 4

    def test_security_config_creation(self) -> None:
        """Test security configuration through MainConfig."""
        # SecurityConfig is not directly available, use MainConfig with nested structure
        main_config = FlextApiConfig.MainConfig(
            server={"host": "127.0.0.1", "port": 8080},
            client={"base_url": "https://api.example.com"},
            security={"enable_https": True, "api_key_required": True},
        )

        assert main_config.security["enable_https"] is True
        assert main_config.security["api_key_required"] is True

    def test_env_config_creation(self) -> None:
        """Test EnvConfig creation."""
        env_config = FlextApiConfig.EnvConfig(
            server_host="127.0.0.1",
            server_port=8080,
            base_url="https://api.example.com",
        )

        assert env_config.server_host == "127.0.0.1"
        assert env_config.server_port == 8080
        assert env_config.base_url == "https://api.example.com"

    def test_main_config_creation(self) -> None:
        """Test MainConfig creation."""
        main_config = FlextApiConfig.MainConfig(
            server={"host": "127.0.0.1", "port": 8080},
            client={"base_url": "https://api.example.com"},
            security={"enable_https": True},
        )

        assert main_config.server["host"] == "127.0.0.1"
        assert main_config.server["port"] == 8080

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
            base_url="https://test.example.com",
            default_timeout=45.0
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
                default_timeout=-1.0  # Invalid negative timeout
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
