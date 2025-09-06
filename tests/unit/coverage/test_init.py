"""Test __init__.py module coverage with REAL execution - NO MOCKS."""

from __future__ import annotations

import tempfile

import flext_api
from flext_api import (
    URL,
    ApiRequest,
    FlextApiConstants,
    FlextApiModels,
    FlextApiStorage,
    StorageBackend,
    StorageConfig,
    create_flext_api,
)

# Constants from FlextApiConstants
FLEXT_API_TIMEOUT = FlextApiConstants.Client.DEFAULT_TIMEOUT
FLEXT_API_VERSION = flext_api.__version__


def test_real_api_creation() -> None:
    """Test REAL API creation with flext-api components."""
    # Test REAL API creation
    api = create_flext_api()
    assert api is not None

    # Should have expected methods
    assert hasattr(api, "create_client")
    assert hasattr(api, "get_builder")


def test_real_storage_creation() -> None:
    """Test REAL storage creation."""
    # Test storage creation
    config = StorageConfig(backend=StorageBackend.MEMORY, namespace="test")
    storage = FlextApiStorage(config)
    assert storage is not None

    # Storage should be functional
    assert hasattr(storage, "get")
    assert hasattr(storage, "set")


def test_constants_access() -> None:
    """Test accessing constants from FlextApiConstants."""
    # Test timeout constant
    assert FLEXT_API_TIMEOUT is not None
    assert isinstance(FLEXT_API_TIMEOUT, (int, float))

    # Test version
    assert FLEXT_API_VERSION is not None
    assert isinstance(FLEXT_API_VERSION, str)
    assert len(FLEXT_API_VERSION) > 0


def test_models_functionality() -> None:
    """Test FlextApiModels functionality."""
    models = FlextApiModels()
    assert models is not None

    # Models should be instantiable
    assert hasattr(models, "__class__")
    assert models.__class__.__name__ == "FlextApiModels"


def test_url_value_object() -> None:
    """Test URL value object functionality."""
    # Test URL creation
    url = URL(url="https://api.example.com/v1/test")

    # URL is a Pydantic model with a url field
    assert url.url == "https://api.example.com/v1/test"
    assert str(url) == "https://api.example.com/v1/test"


def test_api_request_model() -> None:
    """Test ApiRequest model functionality."""
    # Test ApiRequest creation
    request = ApiRequest(
        id="test_init", method="GET", url="https://api.example.com/v1/init"
    )

    assert request.id == "test_init"
    assert request.method == "GET"
    assert request.url == "https://api.example.com/v1/init"


def test_storage_operations() -> None:
    """Test storage operations."""
    # Create storage
    config = StorageConfig(backend=StorageBackend.MEMORY, namespace="test")
    storage = FlextApiStorage(config)

    # Test set/get operations
    set_result = storage.set("key1", "value1")
    assert set_result.success is True

    get_result = storage.get("key1")
    assert get_result.success is True
    assert get_result.value == "value1"


def test_storage_backends() -> None:
    """Test different storage backends."""
    # Test memory backend
    memory_config = StorageConfig(
        backend=StorageBackend.MEMORY, namespace="memory_test"
    )
    memory_storage = FlextApiStorage(memory_config)
    assert memory_storage is not None

    # Test file backend

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        file_config = StorageConfig(
            backend=StorageBackend.FILE,
            namespace="file_test",
            file_path=tmp.name,
        )
    file_storage = FlextApiStorage(file_config)
    assert file_storage is not None


def test_query_builder_integration() -> None:
    """Test query builder integration."""
    # Create API instance
    api = create_flext_api()

    # Get builder
    builder = api.get_builder()
    assert builder is not None

    # Builder has a create method
    query_data = builder.create(
        filter_conditions={"status": "active"},
        page_number=1,
        page_size_value=20
    )

    assert isinstance(query_data, dict)
    assert query_data["filter_conditions"] == {"status": "active"}
    assert query_data["page_number"] == 1
    assert query_data["page_size_value"] == 20


def test_response_builder_integration() -> None:
    """Test response builder integration."""
    # Create API instance
    api = create_flext_api()

    # Get builder
    builder = api.get_builder()
    assert builder is not None

    # Test response building using create method
    response_data = builder.create(
        status="success",
        data={"message": "test"},
        message="Operation successful"
    )

    assert isinstance(response_data, dict)
    assert response_data["status"] == "success"
    assert response_data["message"] == "Operation successful"
    assert response_data["data"]["message"] == "test"


def test_client_creation_integration() -> None:
    """Test client creation integration."""
    # Create API instance
    api = create_flext_api()

    # Test client creation
    client_result = api.create_client(
        {"base_url": "https://api.example.com", "timeout": 30}
    )

    assert client_result.success is True
    client = client_result.value
    assert client is not None
    assert hasattr(client, "base_url")


def test_constants_structure() -> None:
    """Test FlextApiConstants structure."""
    # Should have expected nested classes/attributes
    assert hasattr(FlextApiConstants, "Client")
    assert hasattr(FlextApiConstants.Client, "DEFAULT_TIMEOUT")

    # Test default timeout value
    timeout = FlextApiConstants.Client.DEFAULT_TIMEOUT
    assert isinstance(timeout, (int, float))
    assert timeout > 0


def test_module_version() -> None:
    """Test module version information."""
    # Test version attribute
    assert hasattr(flext_api, "__version__")
    version = flext_api.__version__
    assert isinstance(version, str)
    assert len(version) > 0

    # Should follow semantic versioning pattern
    version_parts = version.split(".")
    assert len(version_parts) >= 3  # Major.Minor.Patch

    # First three parts should be numeric
    for i, part in enumerate(version_parts[:3]):
        assert part.isdigit(), f"Version part {i} should be numeric: {part}"


def test_integration_patterns() -> None:
    """Test integration patterns between components."""
    # Create API
    api = create_flext_api()

    # Create URL
    url_result = URL(url="https://api.example.com/v1/integration")
    assert url_result is not None

    # Create ApiRequest with URL
    url_string = str(url_result)
    request = ApiRequest(id="integration_test", method="POST", url=url_string)

    # Create storage for request
    config = StorageConfig(backend=StorageBackend.MEMORY, namespace="integration")
    storage = FlextApiStorage(config)

    # All components should work together
    assert api is not None
    assert request is not None
    assert storage is not None
    assert "api.example.com" in request.url
