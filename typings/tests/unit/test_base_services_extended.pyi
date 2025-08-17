import pytest

from flext_api import (
    ClientConfig,
    FlextApiBaseAuthService,
    FlextApiBaseClientService,
    FlextApiBaseHandlerService,
    FlextApiBaseRepositoryService,
    FlextApiMiddlewareProtocol as FlextApiMiddlewareProtocol,
    FlextApiPluginProtocol as FlextApiPluginProtocol,
    FlextApiQueryBuilderProtocol as FlextApiQueryBuilderProtocol,
    FlextApiResponseBuilderProtocol as FlextApiResponseBuilderProtocol,
)
from flext_api.typings import FlextTypes as FlextTypes

class DummyClientService(FlextApiBaseClientService):
    service_name: str
    client_config: ClientConfig

@pytest.mark.asyncio
async def test_base_client_service_lifecycle_and_request() -> None: ...

class DummyAuth(FlextApiBaseAuthService):
    service_name: str

@pytest.mark.asyncio
async def test_base_auth_service_flows() -> None: ...

class DummyRepo(FlextApiBaseRepositoryService):
    service_name: str
    entity_type: type

@pytest.mark.asyncio
async def test_base_repository_crud() -> None: ...

class DummyHandler(FlextApiBaseHandlerService):
    service_name: str

@pytest.mark.asyncio
async def test_base_handler_flow() -> None: ...
