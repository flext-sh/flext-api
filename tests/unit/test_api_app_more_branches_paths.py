"""Test more branches paths."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from flext_api.api_app import FlextApiAppConfig, create_flext_api_app

if TYPE_CHECKING:
    import pytest


def test_cors_origins_fallback_when_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force exception in get_cors_origins try block to return fallback list."""
    cfg = FlextApiAppConfig()
    monkeypatch.setattr("flext_api.api_app.FlextConstants", object())
    origins = cfg.get_cors_origins()
    assert any("localhost" in x for x in origins)


def test_root_and_info_paths() -> None:
    """Test root and info paths are available."""
    app = create_flext_api_app()
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200
    assert "name" in r.json()
    r2 = c.get("/info")
    assert r2.status_code == 200
    assert "api" in r2.json()
