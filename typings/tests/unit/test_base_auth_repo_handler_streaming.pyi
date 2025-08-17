import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiBaseAuthService,
    FlextApiBaseHandlerService,
    FlextApiBaseRepositoryService,
    FlextApiBaseStreamingService,
    FlextApiMiddlewareProtocol,
)

class DummyAuth(FlextApiBaseAuthService):
    service_name: str

@pytest.mark.asyncio
async def test_auth_service_paths() -> None: ...

class DummyRepo(FlextApiBaseRepositoryService):
    service_name: str
    entity_type: type

@pytest.mark.asyncio
async def test_repository_service_paths() -> None: ...

class DummyMw:
    async def process_request(
        self, req: dict[str, object]
    ) -> FlextResult[dict[str, object]]: ...
    async def process_response(
        self, resp: dict[str, object]
    ) -> FlextResult[dict[str, object]]: ...

class DummyHandler(FlextApiBaseHandlerService):
    service_name: str
    middlewares: list[FlextApiMiddlewareProtocol] = ...

@pytest.mark.asyncio
async def test_handler_middleware_chain_and_error() -> None: ...

class DummyStream(FlextApiBaseStreamingService):
    service_name: str

@pytest.mark.asyncio
async def test_streaming_validation_and_errors() -> None: ...
