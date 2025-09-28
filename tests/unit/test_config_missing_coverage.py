"""Tests for missing coverage in config.py module."""

from flext_api import FlextApiConfig


class TestFlextApiConfigMissingCoverage:
    """Tests for missing coverage in FlextApiConfig."""

    def test_api_url_property(self) -> None:
        """Test api_url computed field."""
        config = FlextApiConfig(base_url="https://example.com", api_version="v1")
        assert config.api_url == "https://example.com/api/v1"

    def test_get_client_config_method(self) -> None:
        """Test get_client_config method."""
        config = FlextApiConfig(base_url="https://example.com", api_version="v1")
        client_config = config.get_client_config()
        assert isinstance(client_config, dict)
        assert client_config["base_url"] == "https://example.com"
        assert client_config["api_version"] == "v1"

    def test_get_default_headers_method(self) -> None:
        """Test get_default_headers method."""
        config = FlextApiConfig(api_version="v2")
        headers = config.get_default_headers()
        assert isinstance(headers, dict)
        assert headers["User-Agent"] == "flext-api/v2"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_to_dict_method(self) -> None:
        """Test to_dict method."""
        config = FlextApiConfig(base_url="https://test.com", api_version="v3")
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["base_url"] == "https://test.com"
        assert config_dict["api_version"] == "v3"

    def test_create_for_environment_method(self) -> None:
        """Test create_for_environment class method."""
        config = FlextApiConfig.create_for_environment(
            "test", base_url="https://test.com"
        )
        assert isinstance(config, FlextApiConfig)
        assert config.base_url == "https://test.com"

    def test_create_default_method(self) -> None:
        """Test create_default class method."""
        config = FlextApiConfig.create_default()
        assert isinstance(config, FlextApiConfig)
        assert hasattr(config, "base_url")
        assert hasattr(config, "api_version")

    def test_get_global_instance_method(self) -> None:
        """Test get_global_instance class method."""
        config = FlextApiConfig.get_global_instance()
        assert isinstance(config, FlextApiConfig)
        assert hasattr(config, "base_url")
        assert hasattr(config, "api_version")

    def test_reset_global_instance_method(self) -> None:
        """Test reset_global_instance class method."""
        # This should not raise an exception
        FlextApiConfig.reset_global_instance()
        # Verify we can still create a new instance
        config = FlextApiConfig.create_default()
        assert isinstance(config, FlextApiConfig)
