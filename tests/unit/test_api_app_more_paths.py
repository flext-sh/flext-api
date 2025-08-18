"""Additional API app route and fallback tests."""

from __future__ import annotations

import importlib
import importlib.util
import sys

import pytest

from flext_api import api_app as api_app_module


def test_default_app_instance_exposes_routes() -> None:
    """Default app should expose index and health routes."""
    app = api_app_module.app
    routes = {r.path for r in app.routes}
    assert "/" in routes
    assert "/health" in routes


def test_error_fallback_app_when_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """When app init fails, fallback app should expose /error route."""
    # Force failure using env knob and reload module
    monkeypatch.setenv("FLEXT_API_FORCE_APP_INIT_FAIL", "1")
    spec = importlib.util.find_spec("flext_api.api_app")
    assert spec is not None
    assert spec.loader is not None
    new_module = importlib.util.module_from_spec(spec)
    sys.modules["flext_api.api_app_reloaded"] = new_module
    spec.loader.exec_module(new_module)
    assert hasattr(new_module, "app")
    routes = {r.path for r in new_module.app.routes}
    assert "/error" in routes
