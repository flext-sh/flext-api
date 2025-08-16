"""Extended tests for base service abstractions in flext_api."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api.api_models import ClientConfig

# Ensure forward-ref'd protocols and types exist in eval namespace for model_rebuild
from flext_api.api_protocols import (  # noqa: F401
    FlextApiMiddlewareProtocol,
    FlextApiPluginProtocol,
    FlextApiQueryBuilderProtocol,
    FlextApiResponseBuilderProtocol,
)
from flext_api.base_service import (
    FlextApiBaseAuthService,
    FlextApiBaseClientService,
    FlextApiBaseHandlerService,
    FlextApiBaseRepositoryService,
)
from flext_api.typings import FlextTypes  # noqa: F401


class DummyClientService(FlextApiBaseClientService):
    """Minimal concrete client service for lifecycle and request tests."""

    service_name: str = "dummy"
    client_config: ClientConfig = ClientConfig(
        base_url="https://example.com",
        timeout=5.0,
        headers={},
        max_retries=0,
    )

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _execute_request(self, **_: object) -> FlextResult[dict[str, object]]:
        return FlextResult.ok({"ok": True})


# Ensure Pydantic resolves forward refs for subclass models
DummyClientService.model_rebuild()


@pytest.mark.asyncio
async def test_base_client_service_lifecycle_and_request() -> None:
    """Lifecycle start/stop, health, and request execution for client service."""
    svc = DummyClientService()
    start_res = await svc.start()
    assert start_res.success
    health = await svc.health_check()
    assert health.success
    assert health.data is not None
    assert health.data["status"] in {"healthy", "stopped"}
    res = await svc.request("GET", "http://example.com")
    assert res.success
    assert (await svc.stop()).success


class DummyAuth(FlextApiBaseAuthService):
    """Minimal concrete auth service for flow tests."""

    service_name: str = "auth"

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_authenticate(
        self,
        _credentials: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        return FlextResult.ok({"token": "abcdefghijklmnop"})

    async def _do_validate_token(self, token: str) -> FlextResult[bool]:
        return FlextResult.ok(len(token) >= 16)

    async def _do_refresh_token(self, token: str) -> FlextResult[str]:
        return FlextResult.ok(token + "1")


DummyAuth.model_rebuild()


@pytest.mark.asyncio
async def test_base_auth_service_flows() -> None:
    """Basic auth service flows: authenticate, validate, refresh."""
    auth = DummyAuth()
    res = await auth.authenticate({"u": 1})
    assert res.success
    assert res.data is not None
    token = str(res.data.get("token"))
    assert len(token) >= 16
    assert (await auth.validate_token(token)).data is True
    assert (await auth.refresh_token(token)).data == token + "1"


class DummyRepo(FlextApiBaseRepositoryService):
    """Minimal concrete repository service for CRUD tests."""

    service_name: str = "repo"
    entity_type: type = dict

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_find_by_id(self, entity_id: str) -> FlextResult[dict[str, object]]:
        return FlextResult.ok({"id": entity_id})

    async def _do_find_all(
        self,
        _filters: dict[str, object] | None,
        _limit: int | None,
        _offset: int | None,
    ) -> FlextResult[list[dict[str, object]]]:
        return FlextResult.ok([{"id": 1}])

    async def _do_save(
        self,
        entity: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        return FlextResult.ok(entity)

    async def _do_delete(self, _entity_id: str) -> FlextResult[None]:
        return FlextResult.ok(None)


DummyRepo.model_rebuild()


@pytest.mark.asyncio
async def test_base_repository_crud() -> None:
    """Repository CRUD operations return expected results."""
    repo = DummyRepo()
    assert (await repo.find_by_id("1")).data == {"id": "1"}
    assert (await repo.find_all()).data == [{"id": 1}]
    assert (await repo.save({"id": 2})).data == {"id": 2}
    assert (await repo.delete("2")).success


class DummyHandler(FlextApiBaseHandlerService):
    """Minimal concrete handler for request flow tests."""

    service_name: str = "handler"

    async def _do_start(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        return FlextResult.ok(None)

    async def _do_handle(
        self,
        request: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        return FlextResult.ok({"echo": request})


DummyHandler.model_rebuild()


@pytest.mark.asyncio
async def test_base_handler_flow() -> None:
    """Handler echoes request payload as response."""
    h = DummyHandler()
    res = await h.handle({"a": 1})
    assert res.success
    assert res.data == {"echo": {"a": 1}}
