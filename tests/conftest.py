"""Pytest configuration and shared fixtures for FLEXT-API.

Modern test configuration for FastAPI with async support.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import all modules at top level to avoid PLC0415
try:
    from flext_api.database import create_test_database
    from flext_api.database import get_session
    from flext_api.main import create_app
    from flext_api.repositories import PipelineRepository
    from flext_api.services import PipelineService
except ImportError:
    # Handle import failures gracefully in test environment
    create_app = None
    create_test_database = None
    get_session = None
    PipelineRepository = None
    PipelineService = None

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from _pytest.config import Config
    from _pytest.nodes import Item
    from fastapi import FastAPI


# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom markers."""
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "unit: Unit tests that don't require external dependencies",
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests that may require external services",
    )
    config.addinivalue_line(
        "markers",
        "slow: Tests that take more than 1 second to run",
    )
    config.addinivalue_line(
        "markers",
        "smoke: Quick smoke tests for CI/CD",
    )
    config.addinivalue_line(
        "markers",
        "e2e: End-to-end tests",
    )
    config.addinivalue_line(
        "markers",
        "api: API endpoint tests",
    )
    config.addinivalue_line(
        "markers",
        "auth: Authentication tests",
    )


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Modify collected test items with auto-markers."""
    for item in items:
        # Auto-mark based on test location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


# ============================================================================
# Event Loop Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    """Get event loop policy for async tests."""
    return asyncio.DefaultEventLoopPolicy()


# ============================================================================
# FastAPI App Fixtures
# ============================================================================


@pytest.fixture
def app() -> FastAPI:
    """Create FastAPI app for testing."""
    if create_app is None:
        pytest.skip("flext_api.main not available")
    return create_app(testing=True)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Get auth headers for testing."""
    return {"Authorization": "Bearer test-token-123"}


@pytest.fixture
def REDACTED_LDAP_BIND_PASSWORD_headers() -> dict[str, str]:
    """Get REDACTED_LDAP_BIND_PASSWORD headers for testing."""
    return {"Authorization": "Bearer REDACTED_LDAP_BIND_PASSWORD-test-token-456"}


@pytest_asyncio.fixture
async def authenticated_client(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> AsyncClient:
    """Create authenticated client."""
    async_client.headers.update(auth_headers)
    return async_client


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_db() -> AsyncIterator[Any]:
    """Create test database session."""
    if create_test_database is None or get_session is None:
        pytest.skip("flext_api.database not available")

    # Create test database
    engine = await create_test_database()

    async with get_session(engine) as session:
        yield session

    # Cleanup
    await engine.dispose()


# ============================================================================
# Repository Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def pipeline_repository(test_db: Any) -> AsyncIterator[Any]:
    """Create pipeline repository for testing."""
    if PipelineRepository is None:
        pytest.skip("flext_api.repositories not available")

    repo = PipelineRepository(session=test_db)
    yield repo


# ============================================================================
# Service Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def pipeline_service(pipeline_repository: Any) -> AsyncIterator[Any]:
    """Create pipeline service for testing."""
    if PipelineService is None:
        pytest.skip("flext_api.services not available")

    service = PipelineService(repository=pipeline_repository)
    yield service


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_pipeline_data() -> dict[str, Any]:
    """Get sample pipeline data for testing."""
    return {
        "name": "test-pipeline",
        "description": "Test pipeline for API tests",
        "config": {
            "source": "postgres",
            "destination": "snowflake",
            "schedule": "@daily",
        },
        "metadata": {
            "owner": "test_user",
            "team": "data_team",
        },
    }


@pytest.fixture
def sample_plugin_data() -> dict[str, Any]:
    """Get sample plugin data for testing."""
    return {
        "name": "test-plugin",
        "type": "extractor",
        "version": "1.0.0",
        "config": {
            "connection_string": "postgresql://localhost/test",
            "batch_size": 1000,
        },
    }


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_external_service(mocker: Any) -> Any:
    """Create mock external service."""
    mock = mocker.Mock()
    mock.validate.return_value = True
    mock.execute.return_value = {"status": "success"}
    return mock


@pytest.fixture
def mock_grpc_client(mocker: Any) -> Any:
    """Create mock gRPC client."""
    mock = mocker.Mock()
    mock.CreatePipeline.return_value = mocker.Mock(id="pipeline-123")
    return mock


# ============================================================================
# Response Fixtures
# ============================================================================


@pytest.fixture
def success_response() -> dict[str, Any]:
    """Get success response for testing."""
    return {
        "status": "success",
        "data": {},
        "message": "Operation completed successfully",
    }


@pytest.fixture
def error_response() -> dict[str, Any]:
    """Get error response for testing."""
    return {
        "status": "error",
        "error": {
            "code": "TEST_ERROR",
            "message": "Test error occurred",
        },
    }
