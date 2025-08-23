"""Tests for CLI entrypoints and server runners in flext_api.api_app - REAL execution."""

from __future__ import annotations

import inspect

# Import functions directly from the app module
from flext_api.app import (
    create_flext_api_app_with_settings,
    main,
    run_development_server,
    run_production_server,
)


def test_run_development_server_function_exists() -> None:
    """Test that development server function exists and can be called - REAL function validation."""
    # Test that the function exists and is callable
    assert callable(run_development_server)

    # Test the function signature by inspecting it
    sig = inspect.signature(run_development_server)

    # Verify expected parameters exist
    assert "host" in sig.parameters
    assert "port" in sig.parameters
    assert "reload" in sig.parameters
    assert "log_level" in sig.parameters

    # Test default values
    assert sig.parameters["host"].default == "127.0.0.1"
    assert sig.parameters["reload"].default is True
    assert sig.parameters["log_level"].default == "info"


def test_run_production_server_function_exists() -> None:
    """Test that production server function exists and can be called - REAL function validation."""
    # Test that the function exists and is callable
    assert callable(run_production_server)

    # Test the function signature
    sig = inspect.signature(run_production_server)

    # Verify expected parameters exist
    assert "host" in sig.parameters
    assert "port" in sig.parameters

    # Both should default to None (will use settings)
    assert sig.parameters["host"].default is None
    assert sig.parameters["port"].default is None

    # Return type should be None (either None object or string "None" from annotation)
    assert (
        sig.return_annotation is None
        or sig.return_annotation is type(None)
        or str(sig.return_annotation) == "None"
    )


def test_create_flext_api_app_with_settings_success() -> None:
    """App factory with debug flag returns app with state config."""
    app = create_flext_api_app_with_settings(debug=True)
    assert hasattr(app.state, "config")


def test_create_flext_api_app_with_settings_validation() -> None:
    """Test REAL settings validation and app creation - NO MOCKS."""
    # Test that the function exists and is callable
    assert callable(create_flext_api_app_with_settings)

    # Test function signature
    sig = inspect.signature(create_flext_api_app_with_settings)

    # Should accept **kwargs for settings overrides
    assert "settings_overrides" in sig.parameters
    param = sig.parameters["settings_overrides"]
    assert param.kind == inspect.Parameter.VAR_KEYWORD  # **kwargs

    # Test REAL app creation with various settings
    # Test with debug=True
    app_debug = create_flext_api_app_with_settings(debug=True)

    # Validate real app structure
    assert app_debug is not None
    assert hasattr(app_debug, "state"), "App should have state attribute"

    # Test with debug=False
    app_prod = create_flext_api_app_with_settings(debug=False)
    assert app_prod is not None
    assert hasattr(app_prod, "state")

    # Test with environment setting
    app_env = create_flext_api_app_with_settings(environment="test")
    assert app_env is not None

    # Apps should be different instances
    assert app_debug is not app_prod
    assert app_prod is not app_env


def test_main_entrypoint_function_exists() -> None:
    """Test that main entrypoint function exists and is properly structured - REAL validation."""
    # Test that main function exists
    assert callable(main)

    # Test the function signature
    sig = inspect.signature(main)

    # Main should typically accept no required arguments
    required_params = [p for p in sig.parameters.values() if p.default == p.empty]
    assert len(required_params) == 0, "main() should not require parameters"

    # Test that we can import the module where main is defined
    # This validates that all dependencies are properly available
    assert main.__module__ is not None
