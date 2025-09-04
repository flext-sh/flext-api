"""Extended tests for base services using flext-core patterns."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from flext_core import FlextResult

from flext_api import FlextApiBaseService


class DummyAuthService(FlextApiBaseService):
    """Minimal auth service for testing authentication patterns."""

    _service_name: str

    def __init__(self) -> None:
        super().__init__()
        # Store service name as a simple attribute (not in Pydantic data)
        self._service_name = "dummy-auth"

    @property
    def service_name(self) -> str:
        """Get service name."""
        return self._service_name

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def authenticate(
        self, credentials: dict[str, object]
    ) -> FlextResult[dict[str, object]]:
        """Authenticate user with credentials."""
        username = credentials.get("username")
        if username == "valid_user":
            return FlextResult[dict[str, object]].ok({
                "token": "auth_token_123",
                "user_id": "user_123",
                "expires_in": 3600,
            })
        return FlextResult[dict[str, object]].fail("Invalid credentials")


class DummyRepositoryService(FlextApiBaseService):
    """Minimal repository service for testing data access patterns."""

    _service_name: str

    def __init__(self) -> None:
        super().__init__()
        # Store service name as a simple attribute (not in Pydantic data)
        self._service_name = "dummy-repository"
        self._data: dict[str, dict[str, object]] = {}

    @property
    def service_name(self) -> str:
        """Get service name."""
        return self._service_name

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def save(
        self, entity_id: str, data: dict[str, object]
    ) -> FlextResult[dict[str, object]]:
        """Save entity data."""
        self._data[entity_id] = data
        return FlextResult[dict[str, object]].ok(data)

    async def find_by_id(self, entity_id: str) -> FlextResult[dict[str, object] | None]:
        """Find entity by ID."""
        if entity_id in self._data:
            return FlextResult[dict[str, object] | None].ok(self._data[entity_id])
        return FlextResult[dict[str, object] | None].ok(None)

    async def delete(self, entity_id: str) -> FlextResult[bool]:
        """Delete entity by ID."""
        if entity_id in self._data:
            del self._data[entity_id]
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].ok(data=False)


class DummyStreamingService(FlextApiBaseService):
    """Minimal streaming service for testing async iteration patterns."""

    _service_name: str

    def __init__(self) -> None:
        super().__init__()
        # Store service name as a simple attribute (not in Pydantic data)
        self._service_name = "dummy-streaming"

    @property
    def service_name(self) -> str:
        """Get service name."""
        return self._service_name

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult[None].ok(None)

    async def stream_data(self, count: int = 5) -> AsyncIterator[dict[str, object]]:
        """Stream data items asynchronously."""
        for i in range(count):
            yield {"item": i, "value": f"data_{i}", "timestamp": f"2023-01-0{i + 1}"}


@pytest.mark.asyncio
async def test_auth_service_authentication() -> None:
    """Test authentication service functionality."""
    auth_service = DummyAuthService()

    await auth_service.start_async()

    # Test valid authentication
    valid_result = await auth_service.authenticate({
        "username": "valid_user",
        "password": "test",
    })
    assert valid_result.success
    assert valid_result.value is not None
    assert valid_result.value["token"] == "auth_token_123"
    assert valid_result.value["user_id"] == "user_123"

    # Test invalid authentication
    invalid_result = await auth_service.authenticate({"username": "invalid_user"})
    assert not invalid_result.success
    assert invalid_result.error == "Invalid credentials"

    await auth_service.stop_async()


@pytest.mark.asyncio
async def test_repository_service_crud_operations() -> None:
    """Test repository service CRUD operations."""
    repo_service = DummyRepositoryService()

    await repo_service.start_async()

    # Test save
    test_data = {"name": "Test Entity", "value": 42, "active": True}
    save_result = await repo_service.save("entity_1", test_data)
    assert save_result.success
    assert save_result.value == test_data

    # Test find
    find_result = await repo_service.find_by_id("entity_1")
    assert find_result.success
    assert find_result.value == test_data

    # Test find non-existent
    not_found_result = await repo_service.find_by_id("non_existent")
    assert not_found_result.success
    assert not_found_result.value is None

    # Test delete
    delete_result = await repo_service.delete("entity_1")
    assert delete_result.success
    assert delete_result.value is True

    # Test delete non-existent
    delete_missing_result = await repo_service.delete("non_existent")
    assert delete_missing_result.success
    assert delete_missing_result.value is False

    await repo_service.stop_async()


@pytest.mark.asyncio
async def test_streaming_service_async_iteration() -> None:
    """Test streaming service async iteration."""
    streaming_service = DummyStreamingService()

    await streaming_service.start_async()

    # Test streaming data
    items = [item async for item in streaming_service.stream_data(3)]

    assert len(items) == 3
    assert items[0]["item"] == 0
    assert items[0]["value"] == "data_0"
    assert items[1]["item"] == 1
    assert items[2]["item"] == 2

    await streaming_service.stop_async()


@pytest.mark.asyncio
async def test_service_lifecycle_integration() -> None:
    """Test service lifecycle and integration patterns."""
    auth_service = DummyAuthService()
    repo_service = DummyRepositoryService()
    stream_service = DummyStreamingService()

    # Start all services
    await auth_service.start_async()
    await repo_service.start_async()
    await stream_service.start_async()

    # Test integrated workflow
    # 1. Authenticate user
    auth_result = await auth_service.authenticate({"username": "valid_user"})
    assert auth_result.success

    # 2. Save user session data
    session_data = {
        "user_id": auth_result.value["user_id"],
        "token": auth_result.value["token"],
    }
    save_result = await repo_service.save("session_123", session_data)
    assert save_result.success

    # 3. Stream some data
    stream_count = 0
    async for _ in stream_service.stream_data(2):
        stream_count += 1
    assert stream_count == 2

    # Stop all services
    await auth_service.stop_async()
    await repo_service.stop_async()
    await stream_service.stop_async()


def test_service_initialization_and_properties() -> None:
    """Test service initialization and basic properties."""
    auth_service = DummyAuthService()
    repo_service = DummyRepositoryService()
    stream_service = DummyStreamingService()

    assert auth_service.service_name == "dummy-auth"
    assert repo_service.service_name == "dummy-repository"
    assert stream_service.service_name == "dummy-streaming"

    assert hasattr(auth_service, "is_running")
    assert hasattr(repo_service, "is_running")
    assert hasattr(stream_service, "is_running")
