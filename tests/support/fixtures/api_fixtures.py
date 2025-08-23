"""Core API fixtures for flext-api testing.

Provides reusable pytest fixtures for HTTP clients, configs, and sessions.
Uses pytest-asyncio for async fixtures and pytest-httpx for HTTP mocking.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import aiohttp
import pytest
from httpx import AsyncClient

from flext_api import FlextApiClient, FlextApiClientConfig
from flext_api.config import FlextApiSettings
from tests.support.factories import FlextApiConfigFactory


@pytest.fixture
async def http_client_session() -> AsyncGenerator[aiohttp.ClientSession]:
    """Provide real aiohttp session for integration tests."""
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
def flext_api_config() -> FlextApiSettings:
    """Provide test FlextApiSettings using factory."""
    return FlextApiConfigFactory(
        api_host="httpbin.org",
        default_timeout=10,
        max_retries=1,
    )


@pytest.fixture
async def flext_api_client(flext_api_config: FlextApiSettings) -> AsyncGenerator[FlextApiClient]:
    """Provide configured FlextApiClient for testing."""
    # Convert FlextApiSettings to FlextApiClientConfig
    client_config = FlextApiClientConfig(base_url=f"https://{flext_api_config.api_host}")
    client = FlextApiClient(client_config)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
async def httpx_async_client() -> AsyncGenerator[AsyncClient]:
    """Provide httpx AsyncClient for alternative testing."""
    async with AsyncClient() as client:
        yield client
