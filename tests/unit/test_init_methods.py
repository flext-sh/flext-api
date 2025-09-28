"""Tests for FlextApi __init__.py methods to improve coverage."""

from unittest.mock import Mock, patch

import pytest

from flext_api import FlextApi, FlextApiConstants


class TestFlextApiInitMethods:
    """Tests for FlextApi __init__.py methods to improve coverage."""

    def test_create_client_with_default_config(self) -> None:
        """Test create_client with default configuration."""
        base_url = "https://api.example.com"

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = FlextApi.create_client(base_url)

            assert client == mock_client
            mock_client_class.assert_called_once()

            # Check the call arguments
            call_args = mock_client_class.call_args
            assert call_args[1]["base_url"] == base_url
            assert call_args[1]["config"] is None

    def test_create_client_with_custom_parameters(self) -> None:
        """Test create_client with custom parameters."""
        base_url = "https://api.example.com"
        kwargs = {
            "timeout": 60,
            "max_retries": 5,
            "headers": {"Authorization": "Bearer token"},
            "verify_ssl": False,
        }

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = FlextApi.create_client(base_url, **kwargs)

            assert client == mock_client
            mock_client_class.assert_called_once()

            # Check the call arguments
            call_args = mock_client_class.call_args
            assert call_args[1]["base_url"] == base_url
            assert call_args[1]["timeout"] == 60
            assert call_args[1]["max_retries"] == 5
            assert call_args[1]["headers"] == {"Authorization": "Bearer token"}
            assert call_args[1]["verify_ssl"] is False

    def test_create_client_with_none_parameters(self) -> None:
        """Test create_client with None parameters."""
        base_url = "https://api.example.com"
        kwargs = {
            "timeout": None,
            "max_retries": None,
            "headers": None,
            "verify_ssl": True,
        }

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = FlextApi.create_client(base_url, **kwargs)

            assert client == mock_client
            mock_client_class.assert_called_once()

            # Check the call arguments
            call_args = mock_client_class.call_args
            assert call_args[1]["base_url"] == base_url
            assert call_args[1]["timeout"] is None
            assert call_args[1]["max_retries"] is None
            assert call_args[1]["headers"] is None
            assert call_args[1]["verify_ssl"] is True

    def test_create_client_with_default_verify_ssl(self) -> None:
        """Test create_client with default verify_ssl."""
        base_url = "https://api.example.com"

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = FlextApi.create_client(base_url)

            assert client == mock_client
            mock_client_class.assert_called_once()

            # Check the call arguments
            call_args = mock_client_class.call_args
            assert call_args[1]["verify_ssl"] is True  # Default value

    def test_create_config_with_kwargs(self) -> None:
        """Test create_config with kwargs."""
        kwargs = {
            "base_url": "https://api.example.com",
            "timeout": 30.0,
            "max_retries": 3,
        }

        with patch("flext_api.FlextApi.Config") as mock_config_class:
            mock_config_instance = Mock()
            mock_config_class.get_or_create_shared_instance.return_value = (
                mock_config_instance
            )

            config = FlextApi.create_config(**kwargs)

            assert config == mock_config_instance
            mock_config_class.get_or_create_shared_instance.assert_called_once_with(
                project_name="flext-api", **kwargs
            )

    def test_create_config_without_kwargs(self) -> None:
        """Test create_config without kwargs."""
        with patch("flext_api.FlextApi.Config") as mock_config_class:
            mock_config_instance = Mock()
            mock_config_class.get_or_create_shared_instance.return_value = (
                mock_config_instance
            )

            config = FlextApi.create_config()

            assert config == mock_config_instance
            mock_config_class.get_or_create_shared_instance.assert_called_once_with(
                project_name="flext-api"
            )

    def test_get_constants(self) -> None:
        """Test get_constants method."""
        constants = FlextApi.get_constants()

        assert constants == FlextApiConstants
        assert constants is not None

    def test_flext_api_class_methods_exist(self) -> None:
        """Test that FlextApi has expected class methods."""
        assert hasattr(FlextApi, "create_client")
        assert hasattr(FlextApi, "create_config")
        assert hasattr(FlextApi, "get_constants")

        # Test method types
        assert callable(FlextApi.create_client)
        assert callable(FlextApi.create_config)
        assert callable(FlextApi.get_constants)

    def test_create_client_with_various_base_urls(self) -> None:
        """Test create_client with various base URLs."""
        test_urls = [
            "https://api.example.com",
            "http://localhost:8000",
            "https://staging-api.example.com",
            "https://production-api.example.com",
        ]

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            for url in test_urls:
                client = FlextApi.create_client(url)

                assert client == mock_client

                # Verify the base_url was passed correctly
                call_args = mock_client_class.call_args
                assert call_args[1]["base_url"] == url

    def test_create_client_parameter_filtering(self) -> None:
        """Test create_client parameter filtering."""
        base_url = "https://api.example.com"
        kwargs = {
            "timeout": 60,
            "max_retries": 5,
            "headers": {"Authorization": "Bearer token"},
            "verify_ssl": False,
            "unknown_param": "should_be_ignored",
            "another_unknown": 123,
        }

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = FlextApi.create_client(base_url, **kwargs)

            assert client == mock_client
            mock_client_class.assert_called_once()

            # Check that only known parameters are passed
            call_args = mock_client_class.call_args
            call_kwargs = call_args[1]

            assert call_kwargs["base_url"] == base_url
            assert call_kwargs["timeout"] == 60
            assert call_kwargs["max_retries"] == 5
            assert call_kwargs["headers"] == {"Authorization": "Bearer token"}
            assert call_kwargs["verify_ssl"] is False

            # Unknown parameters should not be passed
            assert "unknown_param" not in call_kwargs
            assert "another_unknown" not in call_kwargs

    def test_create_config_with_complex_kwargs(self) -> None:
        """Test create_config with complex kwargs."""
        complex_kwargs = {
            "base_url": "https://api.example.com",
            "timeout": 30.0,
            "max_retries": 3,
            "headers": {"Content-Type": "application/json"},
            "verify_ssl": True,
            "custom_setting": "custom_value",
        }

        with patch("flext_api.FlextApi.Config") as mock_config_class:
            mock_config_instance = Mock()
            mock_config_class.get_or_create_shared_instance.return_value = (
                mock_config_instance
            )

            config = FlextApi.create_config(**complex_kwargs)

            assert config == mock_config_instance
            mock_config_class.get_or_create_shared_instance.assert_called_once_with(
                project_name="flext-api", **complex_kwargs
            )

    def test_flext_api_attributes_exist(self) -> None:
        """Test that FlextApi has expected attributes."""
        assert hasattr(FlextApi, "Client")
        assert hasattr(FlextApi, "Config")
        assert hasattr(FlextApi, "Constants")
        assert hasattr(FlextApi, "Storage")
        assert hasattr(FlextApi, "Utilities")
        assert hasattr(FlextApi, "Exceptions")
        assert hasattr(FlextApi, "Models")
        # Note: Types is not exposed in the main FlextApi class

    def test_create_client_error_handling(self) -> None:
        """Test create_client error handling."""
        base_url = "https://api.example.com"

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client_class.side_effect = Exception("Client creation failed")

            with pytest.raises(Exception, match="Client creation failed"):
                FlextApi.create_client(base_url)

    def test_create_config_error_handling(self) -> None:
        """Test create_config error handling."""
        with patch("flext_api.FlextApi.Config") as mock_config_class:
            mock_config_class.get_or_create_shared_instance.side_effect = Exception(
                "Config creation failed"
            )

            with pytest.raises(Exception, match="Config creation failed"):
                FlextApi.create_config()

    def test_flext_api_singleton_pattern(self) -> None:
        """Test FlextApi singleton pattern behavior."""
        # Test that get_constants returns the same instance
        constants1 = FlextApi.get_constants()
        constants2 = FlextApi.get_constants()

        assert constants1 is constants2
        assert constants1 == FlextApiConstants

    def test_create_client_with_minimal_parameters(self) -> None:
        """Test create_client with minimal parameters."""
        base_url = "https://api.example.com"

        with patch("flext_api.FlextApi.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = FlextApi.create_client(base_url)

            assert client == mock_client
            mock_client_class.assert_called_once()

            # Check default values
            call_args = mock_client_class.call_args
            assert call_args[1]["base_url"] == base_url
            assert call_args[1]["config"] is None
            assert call_args[1]["timeout"] is None
            assert call_args[1]["max_retries"] is None
            assert call_args[1]["headers"] is None
            assert call_args[1]["verify_ssl"] is True

    def test_get_models_method(self) -> None:
        """Test get_models method."""
        models = FlextApi.get_models()
        assert models is not None
        assert hasattr(models, "AppConfig")
        assert hasattr(models, "HttpResponse")

    def test_get_exceptions_method(self) -> None:
        """Test get_exceptions method."""
        exceptions = FlextApi.get_exceptions()
        assert exceptions is not None
        assert hasattr(exceptions, "AuthenticationError")
        assert hasattr(exceptions, "ValidationError")
        assert hasattr(exceptions, "NotFoundError")
