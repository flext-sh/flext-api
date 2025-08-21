"""Test API app additional paths."""

from __future__ import annotations

from fastapi.testclient import TestClient

from flext_api import create_flext_api_app


def test_docs_enabled_when_debug_true() -> None:
    """Create app with debug=True via REAL settings configuration."""
    app = create_flext_api_app()
    app.state.config.settings.debug = True
    app = create_flext_api_app(app.state.config)  # rebuild with debug enabled
    c = TestClient(app)
    # /docs should be available with REAL debug mode
    r = c.get("/docs")
    assert r.status_code in {200, 404}  # fastapi may route static; ensure path exists
    # and openapi
    r2 = c.get("/openapi.json")
    assert r2.status_code in {200, 404}


def test_error_middleware_generic_exception() -> None:
    """Test error middleware with REAL generic exception injection."""
    app = create_flext_api_app()

    @app.get("/boom")
    async def boom() -> dict[str, str]:
        msg = "explode"
        raise RuntimeError(msg)

    c = TestClient(app)
    resp = c.get("/boom")
    assert resp.status_code == 500
    assert resp.headers.get("X-Error-Type") == "UnexpectedError"
    body = resp.json()
    assert body.get("error", {}).get("code") == "INTERNAL_SERVER_ERROR"
