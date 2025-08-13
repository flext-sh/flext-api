"""Error middleware handles exceptions and docs are exposed in debug mode."""

from __future__ import annotations

from fastapi.testclient import TestClient

from flext_api import api_app as api_app_module
from flext_api.api_exceptions import FlextApiError


def test_error_middleware_handles_flextapierror_and_generic() -> None:
    """Middleware should map custom and unexpected errors properly."""
    app = api_app_module.create_flext_api_app_with_settings(debug=True)

    @app.get("/boom-api")
    def boom_api() -> None:  # type: ignore[return-type]
        msg = "broken"
        raise FlextApiError(msg, status_code=418)

    @app.get("/boom")
    def boom() -> None:  # type: ignore[return-type]
        msg = "kaboom"
        raise RuntimeError(msg)

    client = TestClient(app)

    r1 = client.get("/boom-api")
    assert r1.status_code == 418
    assert r1.headers.get("X-Error-Type") == "FlextApiError"

    r2 = client.get("/boom")
    assert r2.status_code == 500
    assert r2.headers.get("X-Error-Type") == "UnexpectedError"

    # Docs should be enabled when debug=True
    docs = client.get("/docs")
    assert docs.status_code == 200
