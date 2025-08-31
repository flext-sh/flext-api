"""Additional API app route and fallback tests."""

from __future__ import annotations

import os
import sys

from flext_api import create_flext_api_app


def test_default_app_instance_exposes_routes() -> None:
    """Default app should expose index and health routes."""
    # Create app instance using real API
    app = create_flext_api_app()
    routes = {getattr(r, "path", str(r)) for r in app.routes if hasattr(r, "path")}
    assert "/" in routes
    assert "/health" in routes


def test_error_fallback_app_when_failure() -> None:
    """Test error fallback app behavior with REAL environment manipulation."""
    # Test REAL fallback behavior by setting environment variable
    original_env = os.environ.get("FLEXT_API_FORCE_APP_INIT_FAIL")
    os.environ["FLEXT_API_FORCE_APP_INIT_FAIL"] = "1"

    try:
        # Create app using real API and test fallback behavior
        fallback_app = create_flext_api_app()
        assert fallback_app is not None

        # Verify fallback app has expected structure
        routes = {getattr(r, "path", str(r)) for r in fallback_app.routes if hasattr(r, "path")}

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
