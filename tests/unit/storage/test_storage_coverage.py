"""Test storage.py coverage comprehensively."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from flext_api import (
    FlextApiStorage,
    StorageBackend,
    StorageConfig,
    create_file_storage,
    create_memory_storage,
    create_storage,
)


def test_unsupported_storage_backend() -> None:
    """Test unsupported storage backend error handling."""
    # Create config with invalid backend
    config = StorageConfig(backend="invalid_backend")

    # This should raise ValueError
    with pytest.raises(ValueError, match="Unsupported storage backend"):
        FlextApiStorage(config)


def test_storage_factory_functions() -> None:
    """Test storage factory functions."""
    # Test create_storage with invalid backend
    with pytest.raises(ValueError):
        create_storage("invalid_backend")

    # Test create_memory_storage
    storage = create_memory_storage("test_namespace")
    assert storage is not None

    # Test create_file_storage
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
        storage = create_file_storage(tmp_file.name, "test_namespace")
        assert storage is not None


@pytest.mark.asyncio
async def test_memory_storage_error_paths() -> None:
    """Test memory storage error handling paths."""
    storage = create_memory_storage("test")

    # Test operations that should succeed but test error handling paths
    result = await storage.get("nonexistent_key")
    assert result.success
    assert result.value is None

    # Test delete non-existent key
    result = await storage.delete("nonexistent_key")
    assert result.success
    assert result.value is False

    # Test exists for non-existent key
    result = await storage.exists("nonexistent_key")
    assert result.success
    assert result.value is False


@pytest.mark.asyncio
async def test_file_storage_error_paths() -> None:
    """Test file storage error handling paths."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "test_storage.json"
        storage = create_file_storage(str(storage_path), "test")

        # Test basic operations
        result = await storage.set("test_key", "test_value")
        assert result.success

        result = await storage.get("test_key")
        assert result.success
        assert result.value == "test_value"

        # Test delete
        result = await storage.delete("test_key")
        assert result.success
        assert result.value is True

        # Test clear
        result = await storage.clear()
        assert result.success


@pytest.mark.asyncio
async def test_storage_transaction_support() -> None:
    """Test storage transaction support."""
    storage = create_memory_storage("test")

    # Begin transaction
    tx_id = storage.begin_transaction()
    assert tx_id is not None

    # Add operations to transaction
    result = await storage.set("key1", "value1", transaction_id=tx_id)
    assert result.success

    result = await storage.set("key2", "value2", transaction_id=tx_id)
    assert result.success

    # Commit transaction
    result = await storage.commit_transaction(tx_id)
    assert result.success

    # Verify data was committed
    result = await storage.get("key1")
    assert result.success
    assert result.value == "value1"


@pytest.mark.asyncio
async def test_storage_transaction_rollback() -> None:
    """Test storage transaction rollback."""
    storage = create_memory_storage("test")

    # Begin transaction
    tx_id = storage.begin_transaction()

    # Add operations to transaction
    await storage.set("key1", "value1", transaction_id=tx_id)

    # Rollback transaction
    result = storage.rollback_transaction(tx_id)
    assert result.success

    # Verify data was not committed
    result = await storage.get("key1")
    assert result.success
    assert result.value is None


@pytest.mark.asyncio
async def test_storage_transaction_errors() -> None:
    """Test storage transaction error cases."""
    storage = create_memory_storage("test")

    # Test with invalid transaction ID
    result = await storage.set("key1", "value1", transaction_id="invalid_tx")
    assert not result.success
    assert "not found" in (result.error or "")

    # Test rollback invalid transaction
    result = storage.rollback_transaction("invalid_tx")
    assert not result.success
    assert "not found" in (result.error or "")


@pytest.mark.asyncio
async def test_storage_keys_with_patterns() -> None:
    """Test storage keys method with patterns."""
    storage = create_memory_storage("test")

    # Add some test data
    await storage.set("user:1", "data1")
    await storage.set("user:2", "data2")
    await storage.set("post:1", "data3")

    # Test keys without pattern
    result = await storage.keys()
    assert result.success
    assert len(result.value or []) == 3

    # Test keys with pattern (if supported)
    result = await storage.keys("user:*")
    assert result.success
    # Note: Pattern matching depends on implementation


@pytest.mark.asyncio
async def test_storage_namespace_isolation() -> None:
    """Test storage namespace isolation."""
    storage1 = create_memory_storage("namespace1")
    storage2 = create_memory_storage("namespace2")

    # Set data in different namespaces
    await storage1.set("same_key", "value1")
    await storage2.set("same_key", "value2")

    # Verify isolation
    result1 = await storage1.get("same_key")
    result2 = await storage2.get("same_key")

    assert result1.success
    assert result2.success
    assert result1.value == "value1"
    assert result2.value == "value2"


@pytest.mark.asyncio
async def test_storage_close_cleanup() -> None:
    """Test storage close and cleanup."""
    storage = create_memory_storage("test")

    # Add transaction and data
    tx_id = storage.begin_transaction()
    await storage.set("key1", "value1", transaction_id=tx_id)

    # Close storage (should rollback active transactions)
    result = await storage.close()
    assert result.success


def test_storage_config_validation() -> None:
    """Test storage configuration validation."""
    # Test valid config
    config = StorageConfig(
        backend=StorageBackend.MEMORY, enable_caching=True, cache_ttl_seconds=300
    )
    storage = FlextApiStorage(config)
    assert storage is not None

    # Test file backend config
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
        config = StorageConfig(
            backend=StorageBackend.FILE, file_path=tmp_file.name, enable_caching=False
        )
    storage = FlextApiStorage(config)
    assert storage is not None


def test_create_storage_with_kwargs() -> None:
    """Test create_storage with keyword arguments."""
    # Test with valid kwargs
    storage = create_storage(
        backend="memory", namespace="test", enable_caching=True, cache_ttl_seconds=600
    )
    assert storage is not None

    # Test with file backend
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
        storage = create_storage(
            backend="file", file_path=tmp_file.name, namespace="file_test"
        )
    assert storage is not None


@pytest.mark.asyncio
async def test_cache_functionality() -> None:
    """Test cache functionality if enabled."""
    storage = create_memory_storage("test", enable_caching=True, cache_ttl_seconds=300)

    # Set and get data (should use cache)
    await storage.set("cached_key", "cached_value")
    result = await storage.get("cached_key", use_cache=True)
    assert result.success
    assert result.value == "cached_value"

    # Test without cache
    result = await storage.get("cached_key", use_cache=False)
    assert result.success
    assert result.value == "cached_value"
