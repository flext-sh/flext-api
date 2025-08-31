"""Tests for flext_api.config module - REAL classes only.

Tests using only REAL classes:
- FlextApiConfig

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApiConfig


class TestFlextApiConfig:
    """Test FlextApiConfig REAL class functionality."""

    def test_config_creation_defaults(self) -> None:
        """Test FlextApiConfig creation with defaults."""
        config = FlextApiConfig()

        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.api_port == 8000
        assert config.workers == 1
        assert config.debug is False
        assert config.default_timeout == 30.0
        assert config.max_retries == 3
        assert config.base_url == "http://localhost:8000"

    def test_config_creation_custom(self) -> None:
        """Test FlextApiConfig creation with custom values."""
        config = FlextApiConfig(
            host="0.0.0.0",
            port=9000,
            workers=4,
            debug=True,
            default_timeout=60.0,
            max_retries=5,
            base_url="https://api.example.com"
        )

        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.api_port == 9000  # should match port
        assert config.workers == 4
        assert config.debug is True
        assert config.default_timeout == 60.0
        assert config.max_retries == 5
        assert config.base_url == "https://api.example.com"

    def test_config_port_validation(self) -> None:
        """Test port validation in FlextApiConfig."""
        # Valid ports should work
        config = FlextApiConfig(port=8080)
        assert config.port == 8080

        # Invalid ports should fail
        with pytest.raises(ValueError):
            FlextApiConfig(port=0)

        with pytest.raises(ValueError):
            FlextApiConfig(port=99999)

    def test_config_host_validation(self) -> None:
        """Test host validation in FlextApiConfig."""
        # Valid hosts should work
        config = FlextApiConfig(host="localhost")
        assert config.host == "localhost"

        config = FlextApiConfig(host="192.168.1.100")
        assert config.host == "192.168.1.100"

        # Empty host should fail
        with pytest.raises(ValueError, match="Host cannot be empty"):
            FlextApiConfig(host="")

    def test_config_base_url_validation(self) -> None:
        """Test base URL validation in FlextApiConfig."""
        # Valid URLs should work
        config = FlextApiConfig(base_url="http://localhost:8000")
        assert config.base_url == "http://localhost:8000"

        config = FlextApiConfig(base_url="https://api.example.com")
        assert config.base_url == "https://api.example.com"

        # Invalid URLs should fail
        with pytest.raises(ValueError, match="Base URL cannot be empty"):
            FlextApiConfig(base_url="")

        with pytest.raises(ValueError, match="Base URL must start with http"):
            FlextApiConfig(base_url="ftp://example.com")

    def test_config_timeout_validation(self) -> None:
        """Test timeout validation in FlextApiConfig."""
        # Valid timeouts should work
        config = FlextApiConfig(default_timeout=45.0)
        assert config.default_timeout == 45.0

        # Invalid timeouts should fail
        with pytest.raises(ValueError):
            FlextApiConfig(default_timeout=0)

        with pytest.raises(ValueError):
            FlextApiConfig(default_timeout=-10)

    def test_config_retries_validation(self) -> None:
        """Test retries validation in FlextApiConfig."""
        # Valid retries should work
        config = FlextApiConfig(max_retries=5)
        assert config.max_retries == 5

        config = FlextApiConfig(max_retries=0)  # 0 is valid
        assert config.max_retries == 0

        # Invalid retries should fail
        with pytest.raises(ValueError):
            FlextApiConfig(max_retries=-1)

    def test_config_get_server_config(self) -> None:
        """Test get_server_config method."""
        config = FlextApiConfig(host="0.0.0.0", port=9000, workers=2, debug=True)

        result = config.get_server_config()
        assert result.success

        server_config = result.data
        assert server_config["host"] == "0.0.0.0"
        assert server_config["port"] == 9000
        assert server_config["workers"] == 2
        assert server_config["debug"] is True

    def test_config_get_client_config(self) -> None:
        """Test get_client_config method."""
        config = FlextApiConfig(
            base_url="https://api.example.com",
            default_timeout=45.0,
            max_retries=5
        )

        result = config.get_client_config()
        assert result.success

        client_config = result.data
        assert client_config["base_url"] == "https://api.example.com"
        assert client_config["timeout"] == 45.0
        assert client_config["max_retries"] == 5

    def test_config_get_cors_config(self) -> None:
        """Test get_cors_config method."""
        config = FlextApiConfig(
            cors_origins=["http://localhost:3000"],
            cors_methods=["GET", "POST"],
            cors_headers=["Content-Type"]
        )

        result = config.get_cors_config()
        assert result.success

        cors_config = result.data
        assert cors_config["allow_origins"] == ["http://localhost:3000"]
        assert cors_config["allow_methods"] == ["GET", "POST"]
        assert cors_config["allow_headers"] == ["Content-Type"]
        assert cors_config["allow_credentials"] is True

    def test_config_workers_validation(self) -> None:
        """Test workers validation in FlextApiConfig."""
        # Valid workers should work
        config = FlextApiConfig(workers=4)
        assert config.workers == 4

        # Invalid workers should fail
        with pytest.raises(ValueError):
            FlextApiConfig(workers=0)

        with pytest.raises(ValueError):
            FlextApiConfig(workers=-1)
