"""Compatibility models module mapping to api_models.

Re-exports domain models for tests that import flext_api.models directly.
"""

from __future__ import annotations

# Explicit re-exports to satisfy tests while keeping lint clean
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
