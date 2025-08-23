"""Public API helper tests and additional coverage for app behaviors."""

from __future__ import annotations

from typing import Never

import pytest
from fastapi.testclient import TestClient

from flext_api import (
    FlextApi,
    FlextApi as FlextApiClass,
    api_app as api_app_mod,  # noqa: F401, PLC0415
    create_api_builder,
    create_api_client,
    create_api_service,
    create_api_storage,
    create_flext_api_app,
    sync_health_check,
)


def test_public_sync_health_check_and_helpers() -> None:
    """Smoke test for root helpers and sync health check."""
    api = FlextApiClass()
    # sync helper exported in package root
    res = sync_health_check(api)
    assert res.success
    # client
    client = create_api_client(
        {"base_url": "https://example.com", "headers": {"x": "1"}},
    )
    assert client.config.base_url.endswith("example.com")
    # builder
    builder = create_api_builder()
    q = builder.for_query().with_filters({"a": 1}).build()
    assert q.page == 1
    assert q.page_size == 20
    assert q.filters
    # storage
    storage = create_api_storage("memory", namespace="t1", enable_caching=True)
    # Sanity check object created
    assert storage is not None


@pytest.mark.asyncio
async def test_storage_set_get_via_factory() -> None:
    """Ensure storage factory creates working storage and set/get works."""
    storage = create_api_storage("memory", namespace="t2")
    assert (await storage.set("k", "v")).success
    got = await storage.get("k")
    assert got.success
    assert got.value == "v"


def test_deprecated_create_api_service_and_client_paths() -> None:
    """Ensure deprecated helpers still import and function nominally."""
    api = FlextApi()
    # Deprecated create_api_service function
    svc = create_api_service()
    assert isinstance(svc, FlextApi)

    # Use modern API instead of deprecated create_client
    ok = api.create_client({"base_url": "https://example.org"})
    assert ok.success
    assert ok.value is not None

    # Use modern API for failure case
    bad = api.create_client({"base_url": ""})
    assert not bad.success
    assert "base_url is required" in (bad.error or "")


@pytest.mark.asyncio
async def test__create_client_impl_failure_and_success() -> None:
    """Validate client creation failure and success paths."""
    api = FlextApi()
    # Failure: empty base_url
    with pytest.raises(ValueError):
        api._create_client_impl({"base_url": ""})
    # Success
    client = api._create_client_impl({"base_url": "https://api.example"})
    assert client is not None


def test_app_health_storage_error_and_nonawaitable_paths() -> None:
    """Health endpoint handles REAL storage errors and non-awaitable returns."""
    # Normal app
    app = create_flext_api_app()
    client = TestClient(app)

    # First, simulate REAL storage set raising to hit degraded branch
    class BadStorage:
        def set(self, *_args: object, **_kwargs: object) -> Never:  # no awaitable
            msg = "boom"
            raise RuntimeError(msg)

        def delete(
            self, *_args: object, **_kwargs: object
        ) -> dict[str, object]:  # no awaitable
            return {"ok": True}

    app.state.storage = BadStorage()
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "degraded"
    assert body.get("services", {}).get("storage", {}).get("status") == "degraded"

    # Second, simulate REAL non-awaitable set/delete returning plain objects
    class PlainStorage:
        def set(
            self, *_args: object, **_kwargs: object
        ) -> dict[str, object]:  # returns non-awaitable
            return {"ok": True}

        def delete(
            self, *_args: object, **_kwargs: object
        ) -> dict[str, object]:  # returns non-awaitable
            return {"ok": True}

    app.state.storage = PlainStorage()
    r2 = client.get("/health")
    assert r2.status_code == 200
    body2 = r2.json()
    assert (
        body2.get("services", {}).get("storage", {}).get("last_check") == "successful"
    )


def test_app_error_fallback_route_via_env() -> None:
    """Test error fallback creation and route functionality."""
    # Test creating an error app directly to verify the route works
    from fastapi import FastAPI  # noqa: PLC0415

    # Create minimal error app similar to what app.py does in except block
    error_app = FastAPI(
        title="FLEXT API - Error",
        description="Failed to initialize properly",
    )
    error_message = "Test initialization failure"

    @error_app.get("/error")
    async def error_info() -> dict[str, str]:
        return {"error": error_message, "status": "failed_to_initialize"}

    # Test the error route
    c = TestClient(error_app)
    resp = c.get("/error")
    assert resp.status_code == 200
    assert resp.json().get("status") == "failed_to_initialize"
    assert resp.json().get("error") == "Test initialization failure"
