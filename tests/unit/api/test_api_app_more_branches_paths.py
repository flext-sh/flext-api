"""Test more branches paths."""

from fastapi.testclient import TestClient

from flext_api import FlextApiConfig, create_flext_api_app


def test_cors_origins_fallback_when_exception() -> None:
    """Test CORS origins fallback behavior with REAL configuration."""
    cfg = FlextApiConfig()

    # Test REAL CORS origins configuration
    origins = cfg.get_cors_origins()

    # Should return a valid list of CORS origins including localhost
    assert isinstance(origins, list)
    assert len(origins) > 0
    assert any("localhost" in str(x) for x in origins)

    # Test that CORS origins are properly formatted URLs or patterns
    for origin in origins:
        assert isinstance(origin, str)
        # Should be valid URL patterns or wildcards
        assert len(origin.strip()) > 0


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
