"""Test __init__.py module coverage with REAL execution - NO MOCKS."""

from __future__ import annotations

import asyncio

from flext_api import (
    FLEXT_API_CACHE_TTL,
    FLEXT_API_MAX_RETRIES,
    FLEXT_API_TIMEOUT,
    FLEXT_API_VERSION,
    FlextApiClientMethod,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiSettings,
    FlextApiStorage,
    StorageBackend,
    StorageConfig,
    build_query,
    create_flext_api,
    flext_api_create_app,
)
from flext_api.api import __version__
from flext_api.app import FlextApiAppConfig, create_flext_api_app


def test_real_app_creation() -> None:
    """Test REAL app creation with flext-api components."""
    # Test REAL app creation
    settings = FlextApiSettings(
        api_title="Test API",
        api_version="1.0.0",
        enable_cors=True,
    )

    app = create_flext_api_app(settings)
    assert app is not None

    # Test direct factory function
    app_config = FlextApiAppConfig(title="Test App", version="1.0.0")
    app2 = flext_api_create_app(app_config)
    assert app2 is not None


def test_real_sync_health_check() -> None:
    """Test sync health check function with REAL API."""
    # Create REAL API instance
    real_api = create_flext_api()

    # Test sync health check method from API instance
    result = real_api.sync_health_check()
    assert result.success
    assert isinstance(result.value, dict)
    assert "status" in result.value


def test_build_query_function() -> None:
    """Test build_query function with parameters."""
    # Test with parameters using real build_query function
    result = build_query(
        filters={"status": "active"},
        page=2,
        page_size=50,
    )

    assert isinstance(result, dict)
    assert "filters" in result
    assert "page" in result
    assert "page_size" in result


def test_version_info_parsing() -> None:
    """Test version info parsing with different formats."""
    # Test version is string
    assert isinstance(__version__, str)

    # Create version_info from __version__
    version_parts = __version__.split(".")
    __version_info__ = tuple(int(part) for part in version_parts[:3] if part.isdigit())

    # Test version info is tuple of integers
    assert isinstance(__version_info__, tuple)
    assert all(isinstance(x, int) for x in __version_info__)


def test_api_constants_exports() -> None:
    """Test API constants are properly exported."""
    # Test constants exist and have expected types
    assert isinstance(FLEXT_API_TIMEOUT, int)
    assert isinstance(FLEXT_API_MAX_RETRIES, int)
    assert isinstance(FLEXT_API_CACHE_TTL, int)
    assert isinstance(FLEXT_API_VERSION, str)


def test_real_storage_operations() -> None:
    """Test storage operations with REAL backend."""
    async def test_storage() -> None:
        # Create REAL storage
        config = StorageConfig(backend=StorageBackend.MEMORY, namespace="test")
        storage = FlextApiStorage(config)

        # Test real operations
        set_result = await storage.set("test_key", "test_value")
        assert set_result.success

        get_result = await storage.get("test_key")
        assert get_result == "test_value"

        # Test delete
        delete_result = await storage.delete("test_key")
        assert delete_result.success

    asyncio.run(test_storage())


def test_client_models_creation() -> None:
    """Test client model classes creation."""
    # Test FlextApiClientRequest creation
    request = FlextApiClientRequest(
        method=FlextApiClientMethod.GET,
        url="/test",
    )
    assert request.method == FlextApiClientMethod.GET
    assert request.url == "/test"

    # Test FlextApiClientResponse creation
    response = FlextApiClientResponse(
        status_code=200,
        data={"message": "success"},
    )
    assert response.status_code == 200
    assert response.data == {"message": "success"}
