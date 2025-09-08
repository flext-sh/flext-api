"""Tests for flext_api.config module - REAL classes only.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_api import FlextApiConfig
from tests.conftest import assert_flext_result_success


class TestFlextApiConfig:
    """Test FlextApiConfig REAL class functionality."""

    def test_config_creation_defaults(self) -> None:
        """Test config creation with default values."""
        config = FlextApiConfig()

        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.api_port == 8000
        assert config.workers == 1
        assert config.debug is False
        assert config.default_timeout == 30.0
        assert config.max_retries == 3
        assert config.base_url == "http://localhost:8000"
        assert config.cors_origins == ["*"]
        assert config.cors_methods == ["*"]
        assert config.cors_headers == ["*"]

    def test_config_creation_custom_values(self) -> None:
        """Test config creation with custom values."""
        config = FlextApiConfig(
            host="0.0.0.0",
            port=8080,
            api_port=9000,
            workers=4,
            debug=True,
            default_timeout=60.0,
            max_retries=5,
            base_url="https://api.example.com",
            cors_origins=["https://example.com"],
            cors_methods=["GET", "POST"],
            cors_headers=["Authorization", "Content-Type"],
        )

        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.api_port == 9000
        assert config.workers == 4
        assert config.debug is True
        assert config.default_timeout == 60.0
        assert config.max_retries == 5
        assert config.base_url == "https://api.example.com"
        assert config.cors_origins == ["https://example.com"]
        assert config.cors_methods == ["GET", "POST"]
        assert config.cors_headers == ["Authorization", "Content-Type"]

    def test_config_port_validation(self) -> None:
        """Test port validation."""
        # Valid port
        config = FlextApiConfig(port=8080)
        assert config.port == 8080

        # Invalid ports should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(port=0)
        assert "greater than or equal to 1" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(port=70000)
        assert "less than or equal to 65535" in str(exc_info.value)

    def test_config_workers_validation(self) -> None:
        """Test workers validation."""
        # Valid workers
        config = FlextApiConfig(workers=4)
        assert config.workers == 4

        # Invalid workers should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(workers=0)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_config_timeout_validation(self) -> None:
        """Test timeout validation."""
        # Valid timeout
        config = FlextApiConfig(default_timeout=45.0)
        assert config.default_timeout == 45.0

        # Invalid timeout should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(default_timeout=0.0)
        assert "greater than 0" in str(exc_info.value)

    def test_config_retries_validation(self) -> None:
        """Test max_retries validation."""
        # Valid retries
        config = FlextApiConfig(max_retries=10)
        assert config.max_retries == 10

        # Zero retries is valid
        config = FlextApiConfig(max_retries=0)
        assert config.max_retries == 0

        # Negative retries should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(max_retries=-1)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_config_host_validation(self) -> None:
        """Test host validation."""
        # Valid host
        config = FlextApiConfig(host="192.168.1.100")
        assert config.host == "192.168.1.100"

        # Empty host should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(host="")
        assert "Host cannot be empty" in str(exc_info.value)

    def test_config_base_url_validation(self) -> None:
        """Test base_url validation."""
        # Valid s
        for url in [
            "http://localhost:8000",
            "https://api.example.com",
            "https://test.com:443",
        ]:
            config = FlextApiConfig(base_url=url)
            assert config.base_url == url

        # Empty base_url should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(base_url="")
        assert "Base cannot be empty" in str(exc_info.value)

        # Invalid protocol should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiConfig(base_url="ftp://example.com")
        assert "Base must start with http:// or https://" in str(exc_info.value)

    def test_get_server_config(self) -> None:
        """Test getting server configuration."""
        config = FlextApiConfig(host="0.0.0.0", port=8080, workers=2, debug=True)

        result = config.get_server_config()
        assert_flext_result_success(result)

        server_config = result.value
        assert isinstance(server_config, dict)
        assert server_config["host"] == "0.0.0.0"
        assert server_config["port"] == 8080
        assert server_config["workers"] == 2
        assert server_config["debug"] is True

    def test_get_client_config(self) -> None:
        """Test getting client configuration."""
        config = FlextApiConfig(
            base_url="https://api.test.com", default_timeout=45.0, max_retries=5
        )

        result = config.get_client_config()
        assert_flext_result_success(result)

        client_config = result.value
        assert isinstance(client_config, dict)
        assert client_config["base_url"] == "https://api.test.com"
        assert client_config["timeout"] == 45.0
        assert client_config["max_retries"] == 5

    def test_get_cors_config(self) -> None:
        """Test getting CORS configuration."""
        config = FlextApiConfig(
            cors_origins=["https://example.com", "https://test.com"],
            cors_methods=["GET", "POST", "PUT"],
            cors_headers=["Authorization", "Content-Type"],
        )

        result = config.get_cors_config()
        assert_flext_result_success(result)

        cors_config = result.value
        assert isinstance(cors_config, dict)
        assert cors_config["allow_origins"] == [
            "https://example.com",
            "https://test.com",
        ]
        assert cors_config["allow_methods"] == ["GET", "POST", "PUT"]
        assert cors_config["allow_headers"] == ["Authorization", "Content-Type"]
        assert cors_config["allow_credentials"] is True

    def test_config_inheritance(self) -> None:
        """Test config properly inherits from FlextConfig.BaseModel."""
        config = FlextApiConfig()

        # Should inherit from BaseModel functionality
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")

        # Should be able to serialize
        data = config.model_dump()
        assert isinstance(data, dict)
        assert "host" in data
        assert "port" in data

    def test_config_json_serialization(self) -> None:
        """Test config JSON serialization."""
        config = FlextApiConfig(host="test.com", port=9000)

        # Should serialize to JSON
        json_str = config.model_dump_json()
        assert isinstance(json_str, str)
        assert "test.com" in json_str
        assert "9000" in json_str

    def test_config_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "host": "api.example.com",
            "port": 9000,
            "debug": True,
            "default_timeout": 120.0,
        }

        config = FlextApiConfig(**data)
        assert config.host == "api.example.com"
        assert config.port == 9000
        assert config.debug is True
        assert config.default_timeout == 120.0

    def test_config_copy_and_update(self) -> None:
        """Test copying config with updates."""
        original = FlextApiConfig(host="original.com", port=8000)

        # Create copy with updates
        updated = original.model_copy(update={"host": "updated.com", "port": 9000})

        assert original.host == "original.com"
        assert original.port == 8000
        assert updated.host == "updated.com"
        assert updated.port == 9000

    def test_config_field_info(self) -> None:
        """Test config field information is accessible."""
        config = FlextApiConfig()

        # Should have field info
        fields = config.model_fields
        assert "host" in fields
        assert "port" in fields
        assert "default_timeout" in fields

        # Check field descriptions
        assert "Server host address" in str(fields["host"].description)
        assert "Server port" in str(fields["port"].description)

    def test_config_validation_error_details(self) -> None:
        """Test validation error provides detailed information."""
        try:
            FlextApiConfig(port=-1, default_timeout=-5.0)
            pytest.fail("Should have raised ValidationError")
        except ValidationError as e:
            error_str = str(e)
            assert "port" in error_str
            assert "default_timeout" in error_str

    def test_config_multiple_instances_independence(self) -> None:
        """Test multiple config instances are independent."""
        config1 = FlextApiConfig(host="config1.com", port=8001)
        config2 = FlextApiConfig(host="config2.com", port=8002)

        assert config1 is not config2
        assert config1.host != config2.host
        assert config1.port != config2.port

    def test_config_type_validation(self) -> None:
        """Test config is proper type."""
        config = FlextApiConfig()

        # Should be instance of FlextApiConfig
        assert isinstance(config, FlextApiConfig)

        # Should have expected type name
        assert type(config).__name__ == "FlextApiConfig"
