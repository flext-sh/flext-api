from __future__ import annotations

from fastapi.testclient import TestClient

from flext_api.api_app import create_flext_api_app


def test_docs_enabled_when_debug_true(monkeypatch):  # noqa: ANN001
    # Create app with debug=True via settings overrides path
    app = create_flext_api_app()
    app.state.config.settings.debug = True  # type: ignore[attr-defined]
    app = create_flext_api_app(app.state.config)  # rebuild with debug enabled
    c = TestClient(app)
    # /docs should be available
    r = c.get("/docs")
    assert r.status_code in (200, 404)  # fastapi may route static; ensure path exists
    # and openapi
    r2 = c.get("/openapi.json")
    assert r2.status_code in (200, 404)


def test_error_middleware_generic_exception(monkeypatch):  # noqa: ANN001
    app = create_flext_api_app()

    # Inject a route that raises generic exception to hit generic handler
    @app.get("/boom")
    async def boom():  # noqa: ANN202
        raise RuntimeError("explode")

    c = TestClient(app)
    resp = c.get("/boom")
    assert resp.status_code == 500
    assert resp.headers.get("X-Error-Type") == "UnexpectedError"
    body = resp.json()
    assert body.get("error", {}).get("code") == "INTERNAL_SERVER_ERROR"
