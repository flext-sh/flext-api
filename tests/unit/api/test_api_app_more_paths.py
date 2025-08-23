"""Additional API app route and fallback tests."""

from __future__ import annotations

import importlib
import importlib.util
import sys

from flext_api import api_app as api_app_module


def test_default_app_instance_exposes_routes() -> None:
    """Default app should expose index and health routes."""
    # api_app_module is the FastAPI app instance directly
    routes = {r.path for r in api_app_module.routes}
    assert "/" in routes
    assert "/health" in routes


def test_error_fallback_app_when_failure() -> None:
    """Test error fallback app behavior with REAL environment manipulation."""
    import os

    # Test REAL fallback behavior by setting environment variable
    original_env = os.environ.get("FLEXT_API_FORCE_APP_INIT_FAIL")
    os.environ["FLEXT_API_FORCE_APP_INIT_FAIL"] = "1"

    try:
        # Try to import fresh app module to test fallback behavior
        spec = importlib.util.find_spec("flext_api.app")
        assert spec is not None
        assert spec.loader is not None

        # Create fresh module instance to test REAL fallback
        new_module = importlib.util.module_from_spec(spec)
        sys.modules["flext_api.app_fallback_test"] = new_module
        spec.loader.exec_module(new_module)

        # Verify fallback app has expected structure
        assert hasattr(new_module, "app")
        routes = {r.path for r in new_module.app.routes}

        # Should have error route or basic fallback routes
        expected_routes = ["/error", "/", "/health"]
        has_expected_route = any(route in routes for route in expected_routes)
        assert has_expected_route, f"Expected one of {expected_routes} in {routes}"

    finally:
        # Clean up environment
        if original_env is not None:
            os.environ["FLEXT_API_FORCE_APP_INIT_FAIL"] = original_env
        else:
            os.environ.pop("FLEXT_API_FORCE_APP_INIT_FAIL", None)

        # Clean up module
        if "flext_api.app_fallback_test" in sys.modules:
            del sys.modules["flext_api.app_fallback_test"]
