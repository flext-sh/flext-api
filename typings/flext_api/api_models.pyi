from datetime import datetime
from enum import IntEnum, StrEnum

from _typeshed import Incomplete
from flext_core import FlextEntity, FlextResult, FlextValue

__all__ = [
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_TIMEOUT",
    "URL",
    "ApiEndpoint",
    "ApiErrorContext",
    "ApiRequest",
    "ApiResponse",
    "ApiSession",
    "BearerToken",
    "ClientConfig",
    "ClientProtocol",
    "ClientStatus",
    "HttpHeader",
    "HttpMethod",
    "HttpStatus",
    "OperationType",
    "PaginationInfo",
    "QueryBuilder",
    "QueryConfig",
    "RequestDto",
    "RequestState",
    "ResponseBuilder",
    "ResponseDto",
    "ResponseState",
    "TokenType",
]

DEFAULT_TIMEOUT: float
DEFAULT_PAGE_SIZE: int
DEFAULT_MAX_RETRIES: int

class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"

class HttpStatus(IntEnum):
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    PARTIAL_CONTENT = 206
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304
    TEMPORARY_REDIRECT = 307
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    GONE = 410
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    @property
    def is_informational(self) -> bool: ...
    @property
    def is_success(self) -> bool: ...
    @property
    def is_redirection(self) -> bool: ...
    @property
    def is_client_error(self) -> bool: ...
    @property
    def is_server_error(self) -> bool: ...

class ClientProtocol(StrEnum):
    HTTP = "http"
    HTTPS = "https"

class ClientStatus(StrEnum):
    IDLE = "idle"
    ACTIVE = "active"
    RUNNING = "running"
    STOPPED = "stopped"
    CLOSED = "closed"
    ERROR = "error"

class RequestState(StrEnum):
    CREATED = "created"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ResponseState(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"

class TokenType(StrEnum):
    BEARER = "Bearer"
    JWT = "JWT"
    API_KEY = "ApiKey"

class OperationType(StrEnum):
    QUERY = "query"
    RESPONSE = "response"
    BATCH = "batch"
    STREAM = "stream"

class URL(FlextValue):
    model_config: Incomplete
    raw_url: str
    scheme: str
    host: str
    port: int | None
    path: str
    query: str | None
    fragment: str | None
    @classmethod
    def validate_raw_url(cls, v: str) -> str: ...
    @classmethod
    def validate_scheme(cls, v: str) -> str: ...
    @classmethod
    def validate_host(cls, v: str) -> str: ...
    @classmethod
    def validate_port(cls, v: int | None) -> int | None: ...
    def validate_business_rules(self) -> FlextResult[None]: ...
    @classmethod
    def create(cls, url: str) -> FlextResult[URL]: ...
    def is_secure(self) -> bool: ...
    def base_url(self) -> str: ...
    def full_path(self) -> str: ...

class HttpHeader(FlextValue):
    model_config: Incomplete
    name: str
    value: str
    def validate_business_rules(self) -> FlextResult[None]: ...
    @classmethod
    def create(cls, name: str, value: str) -> FlextResult[HttpHeader]: ...
    def is_authorization(self) -> bool: ...
    def is_content_type(self) -> bool: ...
    def to_dict(
        self, *, by_alias: bool = False, exclude_none: bool = False
    ) -> dict[str, object]: ...
    def to_tuple(self) -> tuple[str, str]: ...

class BearerToken(FlextValue):
    model_config: Incomplete
    token: str
    token_type: TokenType
    expires_at: datetime | None
    @classmethod
    def validate_token(cls, v: str) -> str: ...
    def validate_business_rules(self) -> FlextResult[None]: ...
    @classmethod
    def create(
        cls, token: str, token_type: str | TokenType | None = None
    ) -> FlextResult[BearerToken]: ...
    def is_expired(self) -> bool: ...
    def is_jwt_format(self) -> bool: ...
    def to_authorization_header(self) -> HttpHeader: ...
    def get_raw_token(self) -> str: ...

class ClientConfig(FlextValue):
    model_config: Incomplete
    base_url: str
    timeout: float
    headers: dict[str, str]
    max_retries: int
    @classmethod
    def validate_base_url(cls, v: str) -> str: ...
    @classmethod
    def validate_timeout(cls, v: float) -> float: ...
    @classmethod
    def validate_max_retries(cls, v: int) -> int: ...
    def validate_business_rules(self) -> FlextResult[None]: ...

class QueryConfig(FlextValue):
    model_config: Incomplete
    filters: list[dict[str, object]]
    sorts: list[dict[str, str]]
    page: int
    page_size: int
    search: str | None
    fields: list[str] | None
    def validate_business_rules(self) -> FlextResult[None]: ...
    def to_dict(
        self, *, by_alias: bool = False, exclude_none: bool = False
    ) -> dict[str, object]: ...

class PaginationInfo(FlextValue):
    model_config: Incomplete
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool
    @classmethod
    def create(
        cls, page: int, page_size: int, total: int
    ) -> FlextResult[PaginationInfo]: ...

class ApiRequest(FlextEntity):
    model_config: Incomplete
    method: HttpMethod
    url: str
    headers: dict[str, str]
    body: dict[str, object] | None
    query_params: dict[str, str]
    state: RequestState
    timeout: float
    retry_count: int
    max_retries: int
    def validate_business_rules(self) -> FlextResult[None]: ...
    def can_retry(self) -> bool: ...
    def increment_retry(self) -> FlextResult[ApiRequest]: ...
    def start_processing(self) -> FlextResult[ApiRequest]: ...
    def complete_processing(self) -> FlextResult[ApiRequest]: ...
    def fail_processing(self, error: str) -> FlextResult[ApiRequest]: ...

class ApiResponse(FlextEntity):
    model_config: Incomplete
    status_code: int
    headers: dict[str, str]
    body: dict[str, object] | None
    state: ResponseState
    request_id: str | None
    elapsed_time: float
    from_cache: bool
    error_message: str | None
    def validate_business_rules(self) -> FlextResult[None]: ...
    def is_success(self) -> bool: ...
    def is_error(self) -> bool: ...
    def mark_success(self) -> FlextResult[ApiResponse]: ...
    def mark_error(self, error_message: str) -> FlextResult[ApiResponse]: ...
    def mark_timeout(self) -> FlextResult[ApiResponse]: ...

class ApiEndpoint(FlextEntity):
    model_config: Incomplete
    path: str
    methods: list[HttpMethod]
    description: str | None
    auth_required: bool
    rate_limit: int | None
    timeout: float
    deprecated: bool
    api_version: str
    def validate_business_rules(self) -> FlextResult[None]: ...
    def supports_method(self, method: HttpMethod) -> bool: ...
    def requires_authentication(self) -> bool: ...
    def is_deprecated(self) -> bool: ...

class ApiSession(FlextEntity):
    model_config: Incomplete
    user_id: str | None
    token: str | None
    token_type: TokenType
    expires_at: datetime | None
    last_activity: datetime | None
    is_active: bool
    refresh_token: str | None
    permissions: list[str]
    def validate_business_rules(self) -> FlextResult[None]: ...
    def is_expired(self) -> bool: ...
    def has_permission(self, permission: str) -> bool: ...
    def extend_session(self, duration_minutes: int = 60) -> FlextResult[ApiSession]: ...
    def deactivate(self) -> FlextResult[ApiSession]: ...

class RequestDto(FlextValue):
    method: str
    url: str
    headers: dict[str, str] | None
    params: dict[str, object] | None
    json_data: dict[str, object] | None
    data: str | bytes | None
    timeout: float | None
    def validate_business_rules(self) -> FlextResult[None]: ...

class ResponseDto(FlextValue):
    status_code: int
    headers: dict[str, str] | None
    data: dict[str, object] | list[object] | str | bytes | None
    elapsed_time: float
    request_id: str | None
    from_cache: bool
    def validate_business_rules(self) -> FlextResult[None]: ...

class ApiErrorContext(FlextValue):
    method: str | None
    endpoint: str | None
    status_code: int | None
    error_code: str | None
    details: dict[str, object] | None
    def validate_business_rules(self) -> FlextResult[None]: ...
    def to_dict(
        self, *, by_alias: bool = False, exclude_none: bool = False
    ) -> dict[str, object]: ...

class QueryBuilder(FlextValue):
    filters: list[dict[str, object]]
    sorts: list[dict[str, str]]
    page: int
    page_size: int
    search: str | None
    fields: list[str] | None
    includes: list[str] | None
    excludes: list[str] | None
    def validate_business_rules(self) -> FlextResult[None]: ...
    def to_query_config(self) -> QueryConfig: ...

class ResponseBuilder(FlextValue):
    success: bool
    data: dict[str, object] | list[object] | str | None
    message: str | None
    errors: list[str] | None
    metadata: dict[str, object] | None
    pagination: PaginationInfo | None
    status_code: int
    def validate_business_rules(self) -> FlextResult[None]: ...
    def to_dict(
        self, *, by_alias: bool = False, exclude_none: bool = False
    ) -> dict[str, object]: ...
