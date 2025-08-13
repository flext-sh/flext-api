from __future__ import annotations

import os
from typing import Never

import pytest
from fastapi.testclient import TestClient

from flext_api import (
    FlextApi,
    create_api_builder,
    create_api_client,
    create_api_storage,
    create_flext_api_app,
    sync_health_check,
)
from flext_api.api import FlextApi as FlextApiClass


def test_public_sync_health_check_and_helpers() -> None:
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
    storage = create_api_storage("memory", namespace="t2")
    assert (await storage.set("k", "v")).success
    got = await storage.get("k")
    assert got.success
    assert got.data == "v"


def test_deprecated_create_api_service_and_client_paths() -> None:
    api = FlextApi()
    # Deprecated create_api_service function
    from flext_api.api import create_api_service

    svc = create_api_service()
    assert isinstance(svc, FlextApi)

    # Deprecated flext_api_create_client success
    ok = api.flext_api_create_client({"base_url": "https://example.org"})
    assert ok.success
    assert ok.data is not None

    # Deprecated flext_api_create_client failure
    bad = api.flext_api_create_client({"base_url": ""})
    assert not bad.success
    assert "Failed to create client" in (bad.error or "")


@pytest.mark.asyncio
async def test__create_client_impl_failure_and_success() -> None:
    api = FlextApi()
    # Failure: empty base_url
    with pytest.raises(ValueError):
        api._create_client_impl({"base_url": ""})
    # Success
    client = api._create_client_impl({"base_url": "https://api.example"})
    assert client is not None


def test_app_health_storage_error_and_nonawaitable_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Normal app
    app = create_flext_api_app()
    client = TestClient(app)

    # First, simulate storage set raising to hit degraded branch
    class BadStorage:
        def set(self, *_args, **_kwargs) -> Never:  # no awaitable
            msg = "boom"
            raise RuntimeError(msg)

        def delete(self, *_args, **_kwargs):  # no awaitable
            return {"ok": True}

    app.state.storage = BadStorage()
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "degraded"
    assert body.get("services", {}).get("storage", {}).get("status") == "degraded"

    # Second, simulate non-awaitable set/delete returning plain objects
    class PlainStorage:
        def set(self, *_args, **_kwargs):  # returns non-awaitable
            return {"ok": True}

        def delete(self, *_args, **_kwargs):  # returns non-awaitable
            return {"ok": True}

    app.state.storage = PlainStorage()
    r2 = client.get("/health")
    assert r2.status_code == 200
    body2 = r2.json()
    assert (
        body2.get("services", {}).get("storage", {}).get("last_check") == "successful"
    )


def test_app_error_fallback_route_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force app init to fail and hit /error route
    monkeypatch.setenv("FLEXT_API_FORCE_APP_INIT_FAIL", "1")
    # Re-import module to trigger fallback path
    try:
        # Remove cached module if any
        import sys

        if "flext_api.api_app" in sys.modules:
            del sys.modules["flext_api.api_app"]
        # Use TestClient on the reloaded module's app
        from importlib import reload

        import flext_api.api_app as api_app2
        from flext_api import api_app as api_app_mod  # noqa: F401

        reload(api_app2)
        c = TestClient(api_app2.app)
        resp = c.get("/error")
        assert resp.status_code == 200
        assert resp.json().get("status") == "failed_to_initialize"
    finally:
        # Clean up env var
        os.environ.pop("FLEXT_API_FORCE_APP_INIT_FAIL", None)
