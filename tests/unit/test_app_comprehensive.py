"""Comprehensive tests for FlextApiApp to achieve high coverage."""

import inspect
from unittest.mock import Mock, patch

import pytest

from flext_api import app
from flext_api.app import FlextApiApp
from flext_api.models import FlextApiModels
from flext_core import FlextService


class TestFlextApiAppComprehensive:
    """Comprehensive tests for FlextApiApp to achieve high coverage."""

    def test_create_fastapi_instance_with_defaults(self) -> None:
        """Test FlextApiApp._Factory.create_instance with default parameters."""
        app = FlextApiApp._Factory.create_instance()

        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")
        assert hasattr(app, "description")

    def test_create_fastapi_instance_with_custom_params(self) -> None:
        """Test FlextApiApp._Factory.create_instance with custom parameters."""
        custom_title = "Custom API"
        custom_version = "2.0.0"
        custom_description = "Custom description"
        custom_docs_url = "/custom-docs"
        custom_redoc_url = "/custom-redoc"
        custom_openapi_url = "/custom-openapi.json"

        app = FlextApiApp._Factory.create_instance(
            title=custom_title,
            version=custom_version,
            description=custom_description,
            docs_url=custom_docs_url,
            redoc_url=custom_redoc_url,
            openapi_url=custom_openapi_url,
        )

        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")
        assert hasattr(app, "description")

    def test_create_fastapi_instance_with_none_values(self) -> None:
        """Test FlextApiApp._Factory.create_instance with None values."""
        app = FlextApiApp._Factory.create_instance(
            title=None,
            version=None,
            description=None,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
        )

        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")
        assert hasattr(app, "description")

    def test_create_fastapi_instance_import_error(self) -> None:
        """Test FlextApiApp._Factory.create_instance with ImportError."""
        with patch("flext_api.app.FastAPI") as mock_fastapi:
            mock_fastapi.side_effect = ImportError("FastAPI not available")

            with pytest.raises(
                ImportError,
                match="FastAPI is required for FlextAPI application creation",
            ):
                FlextApiApp._Factory.create_instance()

    def test_flext_api_app_create_fastapi_app_with_config(self) -> None:
        """Test FlextApiApp.create_fastapi_app with configuration."""
        config = FlextApiModels.AppConfig(title="Test API", app_version="1.0.0")

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")

    def test_flext_api_app_create_fastapi_app_with_description(self) -> None:
        """Test FlextApiApp.create_fastapi_app with description attribute."""
        config = FlextApiModels.AppConfig(
            title="Test API", app_version="1.0.0", description="Custom description"
        )

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert hasattr(app, "description")

    def test_flext_api_app_create_fastapi_app_with_docs_url(self) -> None:
        """Test FlextApiApp.create_fastapi_app with docs_url attribute."""
        config = FlextApiModels.AppConfig(
            title="Test API", app_version="1.0.0", docs_url="/custom-docs"
        )

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert hasattr(app, "title")

    def test_flext_api_app_create_fastapi_app_with_redoc_url(self) -> None:
        """Test FlextApiApp.create_fastapi_app with redoc_url attribute."""
        config = FlextApiModels.AppConfig(
            title="Test API", app_version="1.0.0", redoc_url="/custom-redoc"
        )

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert hasattr(app, "title")

    def test_flext_api_app_create_fastapi_app_with_openapi_url(self) -> None:
        """Test FlextApiApp.create_fastapi_app with openapi_url attribute."""
        config = FlextApiModels.AppConfig(
            title="Test API", app_version="1.0.0", openapi_url="/custom-openapi.json"
        )

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert hasattr(app, "title")

    def test_flext_api_app_create_fastapi_app_with_health_check(self) -> None:
        """Test FlextApiApp.create_fastapi_app with health check endpoint."""
        config = FlextApiModels.AppConfig(title="Test API", app_version="1.0.0")

        # Mock the app to have the required methods
        with patch("flext_api.app.FlextApiApp._Factory.create_instance") as mock_create:
            mock_app = Mock()
            mock_app.get = Mock()
            mock_app.add_api_route = Mock()
            mock_create.return_value = mock_app

            app = FlextApiApp.create_fastapi_app(config)

            assert app is not None
            # Verify that add_api_route was called for health check
            mock_app.add_api_route.assert_called_once()

    def test_flext_api_app_create_fastapi_app_without_health_check_methods(
        self,
    ) -> None:
        """Test FlextApiApp.create_fastapi_app when app doesn't have required methods."""
        config = FlextApiModels.AppConfig(title="Test API", app_version="1.0.0")

        # Mock the app to not have the required methods
        with patch("flext_api.app.FlextApiApp._Factory.create_instance") as mock_create:
            mock_app = Mock()
            # Remove the required methods
            del mock_app.get
            del mock_app.add_api_route
            mock_create.return_value = mock_app

            app = FlextApiApp.create_fastapi_app(config)

            assert app is not None
            assert app == mock_app

    def test_flext_api_app_create_fastapi_app_health_check_function(self) -> None:
        """Test the health check function created in create_fastapi_app."""
        config = FlextApiModels.AppConfig(title="Test API", app_version="1.0.0")

        # Mock the app to have the required methods
        with patch("flext_api.app.FlextApiApp._Factory.create_instance") as mock_create:
            mock_app = Mock()
            mock_app.get = Mock()
            mock_app.add_api_route = Mock()
            mock_create.return_value = mock_app

            FlextApiApp.create_fastapi_app(config)

            # Get the health check function that was passed to add_api_route
            call_args = mock_app.add_api_route.call_args
            health_check_func = call_args[0][1]  # Second argument is the function

            # Test the health check function
            result = health_check_func()

            assert isinstance(result, dict)
            assert result["status"] == "healthy"
            assert result["service"] == "flext-api"

    def test_flext_api_app_create_fastapi_app_with_all_attributes(self) -> None:
        """Test FlextApiApp.create_fastapi_app with all optional attributes."""
        config = FlextApiModels.AppConfig(
            title="Test API",
            app_version="1.0.0",
            description="Custom description",
            docs_url="/custom-docs",
            redoc_url="/custom-redoc",
            openapi_url="/custom-openapi.json",
        )

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")

    def test_flext_api_app_inheritance(self) -> None:
        """Test that FlextApiApp inherits from FlextService."""
        assert issubclass(FlextApiApp, FlextService)

    def test_flext_api_app_static_method(self) -> None:
        """Test that create_fastapi_app is a static method."""
        assert inspect.isfunction(FlextApiApp.create_fastapi_app)

    def test_create_fastapi_instance_edge_cases(self) -> None:
        """Test FlextApiApp._Factory.create_instance with edge case values."""
        # Test with empty strings
        app = FlextApiApp._Factory.create_instance(title="", version="", description="")

        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")
        assert hasattr(app, "description")

    def test_flext_api_app_with_mock_config_attributes(self) -> None:
        """Test FlextApiApp.create_fastapi_app with mock config attributes."""
        config = Mock()
        config.title = "Mock API"
        config.app_version = "1.0.0"
        config.description = "Mock description"
        config.docs_url = "/mock-docs"
        config.redoc_url = "/mock-redoc"
        config.openapi_url = "/mock-openapi.json"

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert hasattr(app, "title")

    def test_flext_api_app_error_handling(self) -> None:
        """Test FlextApiApp.create_fastapi_app error handling."""
        # Test with invalid config
        with pytest.raises(AttributeError):
            FlextApiApp.create_fastapi_app(None)

    def test_app_module_all_exports(self) -> None:
        """Test that app module exports are correct."""
        assert hasattr(app, "FlextApiApp")
        # create_fastapi_instance was refactored to FlextApiApp._Factory.create_instance
