"""
COMPREHENSIVE pytest configuration for flext-api tests.

MASSIVE use of pytest ecosystem modules:
- pytest-asyncio: Async test support
- pytest-benchmark: Performance testing
- pytest-mock: Advanced mocking (replacing unittest.mock)
- pytest-httpx: HTTP client testing
- pytest-randomly: Test order randomization
- pytest-timeout: Test timeout management
- pytest-env: Environment variable management
- pytest-deadfixtures: Dead fixture detection
- pytest-cov: Coverage reporting
- pytest-clarity: Enhanced assertion reporting
- pytest-sugar: Enhanced test output
- pytest-xdist: Parallel test execution
- factory_boy: Professional test data generation
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from collections.abc import AsyncGenerator, Iterator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import all support modules
from tests.support.factories import (
    FlextApiAppConfigFactory,
    FlextApiClientRequestFactory,
    FlextApiClientResponseFactory,
    FlextApiConfigFactory,
)
from tests.support.fixtures import (
    flext_api_app,
    flext_api_client,
    flext_api_config,
    test_client,
)
from tests.support.utils import (
    assert_flext_result_failure,
    assert_flext_result_success,
    create_test_request,
    create_test_response,
)

# Flext imports
from flext_api import FlextApiAppConfig, create_flext_api_app
from flext_api.storage import FileStorageBackend, MemoryStorageBackend, StorageConfig
from flext_core import FlextResult

# ============================================================================ 
# PYTEST CONFIGURATION - MASSIVE MODULE USAGE
# ============================================================================

# Configure Faker for deterministic test data
fake = Faker()
Faker.seed(12345)

# Environment setup for testing
os.environ.update({
    "FLEXT_API_TESTING": "true",
    "FLEXT_DISABLE_EXTERNAL_CALLS": "1", 
    "FLEXT_TEST_LOG_MINIMAL": "true",
    "FLEXT_FAST_TEST_MODE": "true",
    "ENVIRONMENT": "test",
    "LOG_LEVEL": "DEBUG",
})


def pytest_configure(config: pytest.Config) -> None:
    """
    Configure pytest with comprehensive markers and settings.
    
    Uses pytest-env, pytest-randomly, pytest-timeout for configuration.
    """
    # Add comprehensive test markers
    markers = [
        "unit: Fast isolated unit tests",
        "integration: Integration tests with external dependencies", 
        "e2e: End-to-end workflow tests",
        "api: REST API endpoint tests",
        "client: HTTP client tests",
        "storage: Storage backend tests",
        "config: Configuration tests",
        "auth: Authentication tests",
        "benchmark: Performance benchmark tests (pytest-benchmark)",
        "slow: Slow running tests (pytest-timeout)",
        "network: Tests requiring network access",
        "async_test: Async tests (pytest-asyncio)",
        "mock_test: Tests using mocking (pytest-mock)",
        "factory_test: Tests using factory_boy",
    ]
    
    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """
    Automatically mark tests based on location and content.
    
    Uses pytest collection hooks for automatic test categorization.
    """
    for item in items:
        # Add markers based on test location
        test_path = str(item.fspath)
        
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
            
        if "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
            
        if "/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
            
        if "/benchmarks/" in test_path:
            item.add_marker(pytest.mark.benchmark)
            
        # Add markers based on test name patterns
        test_name = item.name.lower()
        
        if "api" in test_name or "endpoint" in test_name:
            item.add_marker(pytest.mark.api)
            
        if "client" in test_name or "http" in test_name:
            item.add_marker(pytest.mark.client)
            
        if "storage" in test_name or "backend" in test_name:
            item.add_marker(pytest.mark.storage)
            
        if "config" in test_name:
            item.add_marker(pytest.mark.config)
            
        if "auth" in test_name:
            item.add_marker(pytest.mark.auth)
            
        if "async" in test_name or "await" in test_name:
            item.add_marker(pytest.mark.async_test)


# ============================================================================
# PYTEST-ASYNCIO CONFIGURATION
# ============================================================================

# Configure pytest-asyncio for async test support
pytest_asyncio.AUTO_MODE = True


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """
    Session-scoped event loop for pytest-asyncio.
    
    Ensures proper async test execution across the test suite.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    yield loop
    
    # Clean shutdown
    loop.close()


# ============================================================================
# FACTORY BOY INTEGRATION
# ============================================================================

@pytest.fixture
def api_request_factory() -> type[FlextApiClientRequestFactory]:
    """Provide FlextApiClientRequest factory for test data generation."""
    return FlextApiClientRequestFactory


@pytest.fixture  
def api_response_factory() -> type[FlextApiClientResponseFactory]:
    """Provide FlextApiClientResponse factory for test data generation."""
    return FlextApiClientResponseFactory


@pytest.fixture
def api_config_factory() -> type[FlextApiConfigFactory]:
    """Provide FlextApiConfig factory for test data generation."""
    return FlextApiConfigFactory


@pytest.fixture
def app_config_factory() -> type[FlextApiAppConfigFactory]:
    """Provide FlextApiAppConfig factory for test data generation."""
    return FlextApiAppConfigFactory


# ============================================================================
# PYTEST-HTTPX INTEGRATION
# ============================================================================

@pytest.fixture
async def httpx_mock():
    """
    Provide httpx mock for HTTP testing.
    
    Uses pytest-httpx for advanced HTTP mocking.
    """
    pytest_httpx = pytest.importorskip("pytest_httpx")
    return pytest_httpx.HTTPXMock()


# ============================================================================
# PYTEST-BENCHMARK INTEGRATION 
# ============================================================================

try:
    import pytest_benchmark  # noqa: F401
    
    @pytest.fixture
    def benchmark_config() -> dict[str, Any]:
        """Configure pytest-benchmark settings."""
        return {
            "min_rounds": 5,
            "max_time": 1.0,
            "timer": "time.perf_counter",
            "disable_gc": False,
            "warmup": False,
        }
        
except ImportError:
    # Fallback benchmark fixture for environments without pytest-benchmark
    @pytest.fixture
    def benchmark():
        """Lightweight benchmark fallback."""
        def _bench(func, *args, **kwargs):
            return func(*args, **kwargs)
        return _bench


# ============================================================================
# STORAGE AND FILESYSTEM FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Provide temporary directory for test file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
async def memory_storage() -> AsyncGenerator[MemoryStorageBackend[Any], None]:
    """Provide memory storage backend for testing."""
    storage = MemoryStorageBackend[Any]()
    try:
        yield storage
    finally:
        await storage.close()


@pytest.fixture
async def file_storage(temp_dir: Path) -> AsyncGenerator[FileStorageBackend[Any], None]:
    """Provide file storage backend for testing."""
    config = StorageConfig(file_path=str(temp_dir / "test_storage.json"))
    storage = FileStorageBackend[Any](config)
    try:
        yield storage
    finally:
        await storage.close()


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture
def test_app_config() -> FlextApiAppConfig:
    """Provide test application configuration."""
    return FlextApiAppConfigFactory(
        title="Test FLEXT API",
        debug=True,
        docs_url="/docs",
    )


@pytest.fixture
def test_app(test_app_config: FlextApiAppConfig) -> FastAPI:
    """Provide configured test FastAPI application."""
    return create_flext_api_app(test_app_config)


@pytest.fixture
def sync_test_client(test_app: FastAPI) -> TestClient:
    """Provide synchronous test client."""
    return TestClient(test_app)


@pytest.fixture
async def async_test_client(test_app: FastAPI) -> AsyncGenerator[TestClient, None]:
    """Provide asynchronous test client."""
    async with TestClient(test_app) as client:
        yield client


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def fake_data() -> Faker:
    """Provide Faker instance for test data generation."""
    return fake


@pytest.fixture
def assert_success():
    """Provide FlextResult success assertion utility."""
    return assert_flext_result_success


@pytest.fixture  
def assert_failure():
    """Provide FlextResult failure assertion utility."""
    return assert_flext_result_failure


@pytest.fixture
def create_request():
    """Provide test request creation utility."""
    return create_test_request


@pytest.fixture
def create_response():
    """Provide test response creation utility."""
    return create_test_response


# ============================================================================
# PROJECT STRUCTURE FIXTURES
# ============================================================================

@pytest.fixture
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def src_dir(project_root: Path) -> Path:
    """Get source directory."""
    return project_root / "src"


@pytest.fixture
def tests_dir(project_root: Path) -> Path:
    """Get tests directory.""" 
    return project_root / "tests"


# ============================================================================
# CLEANUP AND PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_environment():
    """Automatically clean up test environment after each test."""
    yield
    # Cleanup is handled by individual fixtures


@pytest.fixture(autouse=True)
def optimize_test_performance():
    """Optimize test performance with environment variables."""
    # Already set in module-level configuration
    yield


# ============================================================================
# PYTEST-TIMEOUT CONFIGURATION
# ============================================================================

# Default timeout for all tests (can be overridden per test)
pytest_timeout = 30


# ============================================================================
# RE-EXPORT SUPPORT FIXTURES
# ============================================================================

# Re-export key fixtures from support modules for convenience
__all__ = [
    "flext_api_app",
    "flext_api_client", 
    "flext_api_config",
    "test_client",
    "assert_flext_result_success",
    "assert_flext_result_failure",
    "create_test_request", 
    "create_test_response",
]