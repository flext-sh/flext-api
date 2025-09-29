"""Tests for FlextApiUtilities ConfigurationManager methods to improve coverage."""

from unittest.mock import Mock, patch

from flext_core.result import FlextResult

from flext_api import FlextApiUtilities


class TestFlextApiUtilitiesConfigurationManager:
    """Tests for FlextApiUtilities ConfigurationManager methods."""

    def test_configuration_manager_initialization(self) -> None:
        """Test ConfigurationManager initialization."""
        config_manager = FlextApiUtilities.ConfigurationManager()
        assert config_manager is not None

    def test_validate_configuration_success(self) -> None:
        """Test successful configuration validation."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Mock config object with valid base_url
        mock_config = Mock()
        mock_config.base_url = "https://api.example.com"

        with patch.object(
            FlextApiUtilities.HttpValidator, "validate_url"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[object].ok(None)

            result = config_manager.validate_configuration(mock_config)

            assert result.is_success
            mock_validate.assert_called_once_with("https://api.example.com")

    def test_validate_configuration_invalid_base_url(self) -> None:
        """Test configuration validation with invalid base URL."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Mock config object with invalid base_url
        mock_config = Mock()
        mock_config.base_url = "invalid-url"

        with patch.object(
            FlextApiUtilities.HttpValidator, "validate_url"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[object].fail("Invalid URL format")

            result = config_manager.validate_configuration(mock_config)

            assert result.is_failure
            assert result.error is not None and "Invalid base URL" in result.error

    def test_validate_configuration_non_string_base_url(self) -> None:
        """Test configuration validation with non-string base URL."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Mock config object with non-string base_url
        mock_config = Mock()
        mock_config.base_url = 123

        result = config_manager.validate_configuration(mock_config)

        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Base URL must be a string" in result.error

    def test_validate_configuration_no_base_url(self) -> None:
        """Test configuration validation without base URL."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Mock config object without base_url
        mock_config = Mock()
        del mock_config.base_url

        result = config_manager.validate_configuration(mock_config)

        assert result.is_success

    def test_validate_configuration_exception(self) -> None:
        """Test configuration validation with exception."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Mock config object that raises exception
        mock_config = Mock()
        mock_config.base_url = "https://api.example.com"
        mock_config.__getattribute__ = Mock(side_effect=Exception("Test exception"))

        result = config_manager.validate_configuration(mock_config)

        assert result.is_failure
        assert (
            result.error is not None
            and "Configuration validation failed" in result.error
        )

    def test_get_configuration_dict(self) -> None:
        """Test getting configuration dictionary."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        config_dict = config_manager.get_configuration_dict()

        assert isinstance(config_dict, dict)
        assert "base_url" in config_dict
        assert "timeout" in config_dict
        assert "max_retries" in config_dict
        assert "headers" in config_dict
        assert config_dict["base_url"] == "https://localhost:8000"
        assert config_dict["timeout"] == 30.0
        assert config_dict["max_retries"] == 3
        assert config_dict["headers"] == {}

    def test_headers_property(self) -> None:
        """Test headers property."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        headers = config_manager.headers

        assert isinstance(headers, dict)
        assert headers == {}

    def test_reset_to_defaults_success(self) -> None:
        """Test reset to defaults success."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Mock config type
        mock_config_type = Mock()
        mock_config_instance = Mock()
        mock_config_type.return_value = mock_config_instance

        result = config_manager.reset_to_defaults(mock_config_type)

        assert result.is_success
        assert result.data == mock_config_instance
        mock_config_type.assert_called_once()

    def test_reset_to_defaults_failure(self) -> None:
        """Test reset to defaults failure."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Mock config type that raises exception
        mock_config_type = Mock()
        mock_config_type.side_effect = Exception("Reset failed")

        result = config_manager.reset_to_defaults(mock_config_type)

        assert result.is_failure
        assert result.error is not None and "Configuration reset failed" in result.error

    def test_configuration_manager_methods_exist(self) -> None:
        """Test that ConfigurationManager has expected methods."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        assert hasattr(config_manager, "validate_configuration")
        assert hasattr(config_manager, "get_configuration_dict")
        assert hasattr(config_manager, "headers")
        assert hasattr(config_manager, "reset_to_defaults")

        # Test method types
        assert callable(config_manager.validate_configuration)
        assert callable(config_manager.get_configuration_dict)
        assert callable(getattr(config_manager, "headers"))
        assert callable(config_manager.reset_to_defaults)

    def test_configuration_manager_with_different_config_types(self) -> None:
        """Test ConfigurationManager with different config types."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Test with different mock config types
        config_types = [Mock(), Mock(), Mock()]

        for config_type in config_types:
            mock_instance = Mock()
            config_type.return_value = mock_instance

            result = config_manager.reset_to_defaults(config_type)

            assert result.is_success
            assert result.data == mock_instance
            config_type.assert_called_once()

    def test_configuration_manager_error_scenarios(self) -> None:
        """Test ConfigurationManager error scenarios."""
        config_manager = FlextApiUtilities.ConfigurationManager()

        # Test with None config
        result = config_manager.validate_configuration(None)
        assert result.is_success  # Should succeed if no base_url attribute

        # Test with config that has base_url but validation fails
        mock_config = Mock()
        mock_config.base_url = "http://invalid"

        with patch.object(
            FlextApiUtilities.HttpValidator, "validate_url"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[object].fail("Invalid protocol")

            result = config_manager.validate_configuration(mock_config)

            assert result.is_failure
            assert result.error is not None and "Invalid base URL" in result.error
