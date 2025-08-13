"""Compatibility models module mapping to api_models.

Re-exports domain models for tests that import flext_api.models directly.
"""

from __future__ import annotations

from flext_api.api_models import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_PAGE_SIZE,
    DEFAULT_TIMEOUT,
    URL,
    ApiEndpoint,
    ApiErrorContext,
    ApiRequest,
    ApiResponse,
    ApiSession,
    BearerToken,
    ClientConfig,
    ClientProtocol,
    ClientStatus,
    HttpHeader,
    HttpMethod,
    HttpStatus,
    OperationType,
    PaginationInfo,
    QueryBuilder,
    QueryConfig,
    RequestDto,
    RequestState,
    ResponseBuilder,
    ResponseDto,
    ResponseState,
    TokenType,
)

# Explicit re-exports to satisfy tests while keeping lint clean

# Ensure Pydantic forward refs are fully resolved for compatibility
try:
    URL.model_rebuild()
    ApiEndpoint.model_rebuild()
    ApiRequest.model_rebuild()
    ApiResponse.model_rebuild()
    ApiSession.model_rebuild()
except Exception as _e:
    # Safe to continue; tests will surface any unresolved types
    ...

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
