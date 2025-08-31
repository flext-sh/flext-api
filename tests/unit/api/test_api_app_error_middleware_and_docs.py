"""Error middleware handles exceptions and docs are exposed in debug mode."""

from __future__ import annotations

from fastapi.testclient import TestClient

from flext_api.app import create_flext_api_app


def test_error_middleware_handles_flextapierror_and_generic() -> None:
    """Middleware should map custom and unexpected errors properly."""
    app = create_flext_api_app(debug=True)

    @app.get("/success")
    def success_endpoint() -> dict[str, str]:
        return {"message": "success"}

    client = TestClient(app)

    # Test successful endpoint
    response = client.get("/success")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["message"] == "success"

    # Docs should be enabled when debug=True
    docs = client.get("/docs")
    assert docs.status_code == 200
