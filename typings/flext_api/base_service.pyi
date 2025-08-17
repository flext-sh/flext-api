from abc import ABC
from collections.abc import AsyncIterator, Mapping

from flext_core import FlextDomainService, FlextResult

from flext_api.api_models import ClientConfig
from flext_api.api_protocols import (
    FlextApiMiddlewareProtocol,
    FlextApiPluginProtocol,
    FlextApiQueryBuilderProtocol,
    FlextApiResponseBuilderProtocol,
)
from flext_api.typings import FlextTypes

__all__ = [
    "FlextApiBaseAuthService",
    "FlextApiBaseBuilderService",
    "FlextApiBaseClientService",
    "FlextApiBaseHandlerService",
    "FlextApiBaseRepositoryService",
    "FlextApiBaseService",
    "FlextApiBaseStreamingService",
]

# ...existing code... (removed unused TypeVar declarations)

class FlextApiBaseService(FlextDomainService[dict[str, object]], ABC):
    service_name: str
    service_version: str
    is_running: bool
    async def start(self) -> FlextResult[None]: ...
    async def stop(self) -> FlextResult[None]: ...
    async def health_check(self) -> FlextResult[dict[str, object]]: ...
    def execute(self) -> FlextResult[dict[str, object]]: ...

class FlextApiBaseClientService(FlextApiBaseService, ABC):
    client_config: ClientConfig
    plugins: list[FlextApiPluginProtocol]
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        data: FlextTypes.Core.JsonDict | str | bytes | None = None,
        json: FlextTypes.Core.JsonDict | None = None,
        params: Mapping[str, str] | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def close(self) -> None: ...

class FlextApiBaseAuthService(FlextApiBaseService, ABC):
    auth_config: FlextTypes.Core.JsonDict
    async def authenticate(
        self, credentials: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def validate_token(self, token: str) -> FlextResult[bool]: ...
    async def refresh_token(self, token: str) -> FlextResult[str]: ...

class FlextApiBaseRepositoryService(FlextApiBaseService, ABC):
    entity_type: type
    async def find_by_id(
        self, entity_id: str
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def find_all(
        self,
        filters: FlextTypes.Core.JsonDict | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> FlextResult[list[FlextTypes.Core.JsonDict]]: ...
    async def save(
        self, entity: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def delete(self, entity_id: str) -> FlextResult[None]: ...

class FlextApiBaseHandlerService(FlextApiBaseService, ABC):
    middlewares: list[FlextApiMiddlewareProtocol]
    async def handle(
        self, request: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiBaseBuilderService(FlextApiBaseService, ABC):
    def for_query(self) -> FlextApiQueryBuilderProtocol: ...
    def for_response(self) -> FlextApiResponseBuilderProtocol: ...

class FlextApiBaseStreamingService(FlextApiBaseService, ABC):
    chunk_size: int
    async def stream_data(
        self, source: FlextTypes.Core.JsonDict | str | bytes
    ) -> AsyncIterator[bytes]: ...
