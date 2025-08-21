"""
Core API fixtures for flext-api testing.

Provides reusable pytest fixtures for HTTP clients, configs, and sessions.
Uses pytest-asyncio for async fixtures and pytest-httpx for HTTP mocking.
"""

from __future__ import annotations

import aiohttp
import pytest
from httpx import AsyncClient

from flext_api import FlextApiClient, FlextApiConfig
from tests.support.factories import FlextApiConfigFactory


@pytest.fixture
async def http_client_session() -> aiohttp.ClientSession:
    """Provide real aiohttp session for integration tests."""
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
def flext_api_config() -> FlextApiConfig:
    """Provide test FlextApiConfig using factory."""
    return FlextApiConfigFactory(
        base_url="https://httpbin.org",
        timeout=10.0,
        max_retries=1,
    )


@pytest.fixture
async def flext_api_client(flext_api_config: FlextApiConfig) -> FlextApiClient:
    """Provide configured FlextApiClient for testing."""
    client = FlextApiClient(flext_api_config)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
async def httpx_async_client() -> AsyncClient:
    """Provide httpx AsyncClient for alternative testing."""
    async with AsyncClient() as client:
        yield client