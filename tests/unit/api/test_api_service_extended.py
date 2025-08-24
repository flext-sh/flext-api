"""Extended tests for FlextApi service behaviors and helpers."""

from __future__ import annotations

import asyncio

import pytest
from flext_core import FlextResult

from flext_api import FlextApi, create_flext_api


@pytest.mark.asyncio
async def test_health_check_async_returns_coroutine_and_ok() -> None:
    """health_check_async should return a coroutine and yield success."""
    svc = create_flext_api()
    coro = svc.health_check_async()
    assert asyncio.iscoroutine(coro)
    res = await coro
    assert isinstance(res, FlextResult)
    assert res.success


def test_sync_health_check_runs_ok() -> None:
    """sync_health_check wrapper should work and include service info."""
    svc = create_flext_api()
    res = svc.sync_health_check()
    assert res.success
    assert "service" in (res.value or {})


def test_client_creation_and_info_and_legacy() -> None:
    """Client creation, service info, and legacy wrapper should behave properly."""
    svc = FlextApi()
    result = svc.create_client({"base_url": "https://example.com", "timeout": 1.0})
    assert result.success
    assert svc.get_client() is not None
    info = svc.get_service_info()
    assert info["client_configured"] is True

    # Legacy wrapper success
    legacy_ok = svc.create_client({"base_url": "https://example.com"})
    assert legacy_ok.success

    # Legacy wrapper failure
    bad = svc.create_client({"base_url": ""})
    assert not bad.success


def test_create_client_impl_valid_and_invalid() -> None:
    """Internal client creation returns FlextResult for invalid and valid configs."""
    svc = FlextApi()
    # Invalid -> returns failure FlextResult
    result = svc._create_client_impl({"base_url": ""})
    assert not result.success
    assert "Invalid URL format" in result.error

    # Valid -> returns success FlextResult with instance
    result = svc._create_client_impl(
        {"base_url": "https://api.example.com", "timeout": 0.1},
    )
    assert result.success
    assert result.value is not None


def test_builders_accessors() -> None:
    """Builder accessors should return non-null builder instances."""
    svc = FlextApi()
    qb = svc.get_query_builder()
    rb = svc.get_response_builder()
    assert qb is not None
    assert rb is not None
