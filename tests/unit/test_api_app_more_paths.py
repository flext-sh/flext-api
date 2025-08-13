from __future__ import annotations

import pytest

from flext_api import api_app as api_app_module


def test_default_app_instance_exposes_routes() -> None:
    app = api_app_module.app
    routes = {r.path for r in app.routes}
    assert "/" in routes and "/health" in routes


def test_error_fallback_app_when_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force create_flext_api_app to raise to exercise fallback path
    def boom(*_a, **_k):  # noqa: ANN001
        raise RuntimeError("init error")

    monkeypatch.setattr(api_app_module, "create_flext_api_app", boom)
    # Re-import the module under a fresh name to execute top-level try/except
    import importlib

    mod = importlib.reload(api_app_module)
    assert hasattr(mod, "app")
    # fallback app should have /error route
    routes = {r.path for r in mod.app.routes}
    assert "/error" in routes
