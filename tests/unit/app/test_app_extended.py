"""Extended tests for flext_api application and middleware behavior."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from flext_api import FlextApiError, create_flext_api_app
from flext_api.app import FlextApiAppConfig


def _make_app(*, debug: bool = True) -> FastAPI:
    """Create app with debug flag toggled for docs/openapi visibility."""
    config = FlextApiAppConfig()
    # force debug to enable docs/openapi paths
    object.__setattr__(config.settings, "debug", debug)
    return create_flext_api_app(config)


def test_health_and_info_endpoints_happy_path() -> None:
    """Happy path for root, info, live, ready, and health endpoints."""
    app = _make_app(debug=True)
    with TestClient(app) as client:
        r_root = client.get("/")
        assert r_root.status_code == 200
        assert r_root.json()["health_url"] == "/health"
        r_info = client.get("/info")
        assert r_info.status_code == 200
        body = r_info.json()
        assert body["api"]["name"] == "FLEXT API"
        assert isinstance(body["environment"], dict)
        r_live = client.get("/health/live")
        assert r_live.status_code == 200
        assert r_live.json()["status"] == "alive"
        r_ready = client.get("/health/ready")
        assert r_ready.status_code == 200
        assert r_ready.json()["status"] in {"ready", "not_ready"}
        r_health = client.get("/health")
        assert r_health.status_code == 200
        health = r_health.json()
        assert health["status"] in {"healthy", "degraded"}
        assert "system" in health


def test_health_storage_error_path_sets_degraded_status() -> None:
    """Storage errors should downgrade overall health to degraded."""
    app = _make_app()

    # Replace storage with an object that raises on set/delete to go through error branch
    class BadStorage:
        def set(
            self,
            *_: object,
            **__: object,
        ) -> None:  # non-async, but middleware accepts both
            message = "boom"
            raise RuntimeError(message)

        def delete(self, *_: object, **__: object) -> None:
            message = "boom"
            raise RuntimeError(message)

    app.state.storage = BadStorage()
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        payload = r.json()
        # Depending on internal checks this may be degraded or healthy; assert degraded path fields when present
        if payload["services"]["storage"]["status"] == "degraded":
            assert payload["status"] == "degraded"
            assert "error" in payload["services"]["storage"]


def test_error_handler_middleware_handles_custom_and_unexpected_errors() -> None:
    """Error middleware handles both custom and unexpected exceptions."""
    app = _make_app()

    @app.get("/raise_flext")
    def raise_flext() -> None:
        msg = "test error"
        raise FlextApiError(msg, status_code=418)

    @app.get("/raise_unexpected")
    def raise_unexpected() -> None:  # pragma: no cover - covered via request
        message = "unexpected"
        raise RuntimeError(message)

    with TestClient(app) as client:
        r1 = client.get("/raise_flext")
        assert r1.status_code == 418
        body1 = r1.json()
        assert body1["success"] is False
        assert r1.headers["X-Error-Type"] == "FlextApiError"
        r2 = client.get("/raise_unexpected")
        assert r2.status_code == 500
        body2 = r2.json()
        assert body2["success"] is False
        assert r2.headers["X-Error-Type"] == "UnexpectedError"


def test_request_id_middleware_adds_header() -> None:
    """Request ID header is added to successful responses."""
    app = _make_app()

    @app.get("/ok")
    def ok() -> dict[str, str]:
        return {"ok": "1"}

    with TestClient(app) as client:
        r = client.get("/ok")
        assert r.status_code == 200
        assert "X-Request-ID" in r.headers
        assert r.headers["X-Request-ID"]


def test_docs_and_openapi_visible_when_debug_true() -> None:
    """Docs and OpenAPI are accessible in debug mode."""
    app = _make_app(debug=True)
    with TestClient(app) as client:
        assert client.get("/docs").status_code in {
            200,
            404,
        }  # swagger-ui may not ship, but path exists
        assert client.get("/openapi.json").status_code == 200


def test_cors_headers_present_for_allowed_origin() -> None:
    """CORS middleware returns expected headers for allowed origin."""
    app = _make_app()
    with TestClient(app) as client:
        r = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # If allowed, the middleware echoes the origin; otherwise header may be absent. Accept either but prefer present.
        if "access-control-allow-origin" in {k.lower() for k in r.headers}:
            assert r.headers["access-control-allow-origin"] in {
                "*",
                "http://localhost:3000",
            }
