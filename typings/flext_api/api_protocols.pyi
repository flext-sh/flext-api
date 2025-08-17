from collections.abc import AsyncIterator, Mapping
from typing import Protocol

from flext_core import FlextResult

from flext_api.typings import FlextTypes

__all__ = [
    "FlextApiAuthProtocol",
    "FlextApiAuthorizationProtocol",
    "FlextApiCacheProtocol",
    "FlextApiClientProtocol",
    "FlextApiConnectionPoolProtocol",
    "FlextApiHandlerProtocol",
    "FlextApiHealthCheckProtocol",
    "FlextApiMetricsProtocol",
    "FlextApiMiddlewareProtocol",
    "FlextApiPluginProtocol",
    "FlextApiQueryBuilderProtocol",
    "FlextApiRateLimitProtocol",
    "FlextApiRepositoryProtocol",
    "FlextApiResponseBuilderProtocol",
    "FlextApiServiceProtocol",
    "FlextApiStreamProtocol",
    "FlextApiValidatorProtocol",
    "FlextApiWebSocketProtocol",
]

class FlextApiClientProtocol(Protocol):
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
    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def post(
        self,
        url: str,
        *,
        json: FlextTypes.Core.JsonDict | None = None,
        data: str | bytes | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def put(
        self,
        url: str,
        *,
        json: FlextTypes.Core.JsonDict | None = None,
        data: str | bytes | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def delete(
        self, url: str, *, headers: Mapping[str, str] | None = None
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def close(self) -> None: ...

class FlextApiPluginProtocol(Protocol):
    name: str
    enabled: bool
    async def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: FlextTypes.Core.JsonDict,
    ) -> FlextResult[None]: ...
    async def after_response(
        self, response: FlextTypes.Core.JsonDict, method: str, url: str
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiConnectionPoolProtocol(Protocol):
    async def get_connection(
        self, host: str, port: int, *, ssl: bool = False
    ) -> FlextResult[object]: ...
    async def return_connection(self, connection: object) -> FlextResult[None]: ...
    async def close_pool(self) -> FlextResult[None]: ...

class FlextApiQueryBuilderProtocol(Protocol):
    def add_filter(
        self,
        field: str,
        *,
        value: FlextTypes.Core.JsonDict | str | float | bool | None,
        operator: str = "eq",
    ) -> FlextApiQueryBuilderProtocol: ...
    def add_sort(
        self, field: str, *, ascending: bool = True
    ) -> FlextApiQueryBuilderProtocol: ...
    def set_pagination(self, page: int, size: int) -> FlextApiQueryBuilderProtocol: ...
    def add_search(
        self, term: str, fields: list[str] | None = None
    ) -> FlextApiQueryBuilderProtocol: ...
    def select_fields(self, fields: list[str]) -> FlextApiQueryBuilderProtocol: ...
    def build(self) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiResponseBuilderProtocol(Protocol):
    def set_success(
        self, *, success: bool = True
    ) -> FlextApiResponseBuilderProtocol: ...
    def set_data(
        self,
        *,
        data: FlextTypes.Core.JsonDict | list[object] | str | float | bool | None,
    ) -> FlextApiResponseBuilderProtocol: ...
    def set_message(self, message: str) -> FlextApiResponseBuilderProtocol: ...
    def set_error(self, error: str | None) -> FlextApiResponseBuilderProtocol: ...
    def add_metadata(
        self, key: str, *, value: FlextTypes.Core.JsonDict | str | float | bool | None
    ) -> FlextApiResponseBuilderProtocol: ...
    def set_pagination(
        self, page: int, page_size: int, total: int
    ) -> FlextApiResponseBuilderProtocol: ...
    def build(self) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiServiceProtocol(Protocol):
    async def start(self) -> FlextResult[None]: ...
    async def stop(self) -> FlextResult[None]: ...
    async def restart(self) -> FlextResult[None]: ...
    async def health_check(self) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    def get_status(self) -> str: ...

class FlextApiAuthProtocol(Protocol):
    async def authenticate(
        self, credentials: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def validate_token(self, token: str) -> FlextResult[bool]: ...
    async def refresh_token(self, token: str) -> FlextResult[str]: ...
    async def revoke_token(self, token: str) -> FlextResult[None]: ...
    async def get_user_info(
        self, token: str
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiAuthorizationProtocol(Protocol):
    async def check_permission(
        self, user_id: str, resource: str, action: str
    ) -> FlextResult[bool]: ...
    async def get_user_roles(self, user_id: str) -> FlextResult[list[str]]: ...
    async def grant_permission(
        self, user_id: str, resource: str, action: str
    ) -> FlextResult[None]: ...

class FlextApiRepositoryProtocol(Protocol):
    async def find_by_id(
        self, entity_id: str
    ) -> FlextResult[FlextTypes.Core.JsonDict | None]: ...
    async def find_all(
        self,
        filters: FlextTypes.Core.JsonDict | None = None,
        page: int | None = None,
        size: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        *,
        sort_desc: bool = False,
    ) -> FlextResult[list[FlextTypes.Core.JsonDict]]: ...
    async def count(
        self, filters: FlextTypes.Core.JsonDict | None = None
    ) -> FlextResult[int]: ...
    async def save(
        self, entity: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def update(
        self, entity_id: str, updates: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def delete(self, entity_id: str) -> FlextResult[None]: ...
    async def exists(self, entity_id: str) -> FlextResult[bool]: ...

class FlextApiCacheProtocol(Protocol):
    async def get(self, key: str) -> FlextResult[FlextTypes.Core.JsonDict | None]: ...
    async def set(
        self, key: str, value: FlextTypes.Core.JsonDict, ttl_seconds: int | None = None
    ) -> FlextResult[None]: ...
    async def delete(self, key: str) -> FlextResult[bool]: ...
    async def clear(self) -> FlextResult[None]: ...

class FlextApiMiddlewareProtocol(Protocol):
    async def process_request(
        self, request: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    async def process_response(
        self, response: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiRateLimitProtocol(Protocol):
    async def check_rate_limit(
        self, identifier: str, resource: str, window_seconds: int, max_requests: int
    ) -> FlextResult[bool]: ...
    async def get_rate_limit_info(
        self, identifier: str, resource: str
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiHandlerProtocol(Protocol):
    async def handle(
        self, request: FlextTypes.Core.JsonDict
    ) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    def can_handle(self, request: FlextTypes.Core.JsonDict) -> bool: ...

class FlextApiValidatorProtocol(Protocol):
    async def validate_request(
        self, request: FlextTypes.Core.JsonDict
    ) -> FlextResult[None]: ...
    async def validate_response(
        self, response: FlextTypes.Core.JsonDict
    ) -> FlextResult[None]: ...

class FlextApiStreamProtocol(Protocol):
    def __aiter__(self) -> AsyncIterator[bytes]: ...
    async def __anext__(self) -> bytes: ...
    async def close(self) -> None: ...

class FlextApiWebSocketProtocol(Protocol):
    async def accept(self) -> FlextResult[None]: ...
    async def send_text(self, data: str) -> FlextResult[None]: ...
    async def send_bytes(self, data: bytes) -> FlextResult[None]: ...
    async def receive(self) -> FlextResult[str | bytes]: ...
    async def close(self, code: int = 1000, reason: str = "") -> FlextResult[None]: ...

class FlextApiMetricsProtocol(Protocol):
    def increment_counter(
        self, name: str, tags: dict[str, str] | None = None
    ) -> None: ...
    def record_gauge(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None: ...
    def record_histogram(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None: ...
    async def get_metrics(self) -> FlextResult[FlextTypes.Core.JsonDict]: ...

class FlextApiHealthCheckProtocol(Protocol):
    async def check_health(self) -> FlextResult[FlextTypes.Core.JsonDict]: ...
    def get_name(self) -> str: ...
    def is_critical(self) -> bool: ...
