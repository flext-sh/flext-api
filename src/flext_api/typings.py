"""Type definitions for flext-api domain.

All type aliases, type variables, and generic types are centralized here.
Following FLEXT standards: types only, no logic or classes.
"""

from collections.abc import Awaitable, Callable
from typing import TypeVar

# Type variables for generics
T = TypeVar("T")
RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")
ConfigT = TypeVar("ConfigT")

# HTTP-related type aliases
type HttpMethod = str
type HttpStatusCode = int
type HttpHeaders = dict[str, str]
type Headers = dict[str, str]  # Alias for consistency
type HttpParams = dict[str, str | int | float | bool | None]
type HttpData = str | bytes | dict[str, object] | None

# URL and endpoint types
type UrlPath = str
type BaseUrl = str
type FullUrl = str
type EndpointPath = str

# Configuration types
type TimeoutSeconds = float
type RetryCount = int
type PageSize = int
type ApiVersion = str

# Request/Response data types
type RequestData = dict[str, object]
type ResponseData = dict[str, object]
type ErrorData = dict[str, object]

# Authentication types
type ApiKey = str
type BearerToken = str
type AuthHeader = str

# Client and connection types
type ClientId = str
type ConnectionStatus = str
type ClientStatus = str

# Storage and caching types
type StorageKey = str
type StorageValue = object
type CacheTimeout = int

# Pagination types
type PageNumber = int
type PageOffset = int
type TotalCount = int

# Validation types
type ValidationErrors = list[str]
type FieldName = str
type FieldValue = object

# Logging and monitoring types
type LogLevel = str
type RequestId = str
type CorrelationId = str
type TraceId = str

# Performance types
type ResponseTimeMs = float
type ResponseSizeBytes = int
type ThroughputRps = float

# Generic container types
type JsonObject = dict[str, object]
type JsonArray = list[object]
type JsonValue = str | int | float | bool | JsonObject | JsonArray | None

# Additional HTTP and API types
type StatusCode = int
type Timeout = int | float
type Retries = int
type PoolSize = int
type BackoffFactor = float
type Token = str
type Namespace = str
type TTL = int | None

# Plugin and middleware types
type MiddlewareCallable = Callable[[object], Awaitable[object]]
type PluginConfig = dict[str, object]
type HandlerFunction = Callable[[object], object]

# Application and server types
type AppTitle = str
type AppVersion = str
type AppDescription = str
type DocsUrl = str
type Host = str
type Port = int
type Workers = int
type ReloadEnabled = bool

# Security and authentication types
type Origin = str
type AllowedOrigins = list[str]
type AllowedMethods = list[str]
type AllowedHeaders = list[str]
type Hash = str
type Salt = str
type Signature = str
type Certificate = str

# User and session types
type UserId = str
type Username = str
type UserRole = str
type Permissions = list[str]
type SessionId = str
type SessionData = dict[str, object]
type SessionExpiry = int

# Network and infrastructure types
type IpAddress = str
type Hostname = str
type NetworkPort = int
type ConnectionString = str
type DatabaseName = str
type TableName = str
type CollectionName = str

# File and system types
type FilePath = str
type FileName = str
type FileExtension = str
type DirectoryPath = str

# Metrics and monitoring types
type MetricName = str
type MetricValue = int | float
type MetricTags = dict[str, str]
type RateLimitRequests = int
type RateLimitWindow = int

# Cache and storage types
type CacheKey = str
type CacheValue = object
type CacheExpiry = int

# Message and error types
type ErrorMessage = str
type ErrorCode = str
type LogMessage = str
type LogContext = dict[str, object]
type Success = bool
type Timestamp = str

# Pagination extended types
type TotalItems = int
type HasNextPage = bool

# Path and URL extended types
type Url = str
type Endpoint = str
type PathParams = dict[str, str]
type QueryParams = dict[str, object]
type JsonData = dict[str, object]
type RequestBody = str | dict[str, object] | None
type ResponseBody = str | dict[str, object] | None

__all__ = [
    "TTL",
    "AllowedHeaders",
    "AllowedMethods",
    "AllowedOrigins",
    # Authentication types
    "ApiKey",
    "ApiVersion",
    "AppDescription",
    # Application types
    "AppTitle",
    "AppVersion",
    "AuthHeader",
    "BackoffFactor",
    "BaseUrl",
    "BearerToken",
    "CacheExpiry",
    "CacheKey",
    "CacheTimeout",
    "CacheValue",
    "Certificate",
    # Client types
    "ClientId",
    "ClientStatus",
    "CollectionName",
    "ConfigT",
    "ConnectionStatus",
    "ConnectionString",
    "CorrelationId",
    "DatabaseName",
    "DirectoryPath",
    "DocsUrl",
    "Endpoint",
    "EndpointPath",
    "ErrorCode",
    "ErrorData",
    # Message types
    "ErrorMessage",
    "FieldName",
    "FieldValue",
    "FileExtension",
    "FileName",
    # File types
    "FilePath",
    "FullUrl",
    "HandlerFunction",
    "HasNextPage",
    "Hash",
    # Server types
    "Host",
    "Hostname",
    "HttpData",
    "HttpHeaders",
    # HTTP types
    "HttpMethod",
    "HttpParams",
    "HttpStatusCode",
    # Network types
    "IpAddress",
    "JsonArray",
    "JsonData",
    # JSON types
    "JsonObject",
    "JsonValue",
    "LogContext",
    # Logging types
    "LogLevel",
    "LogMessage",
    # Metrics types
    "MetricName",
    "MetricTags",
    "MetricValue",
    # Plugin types
    "MiddlewareCallable",
    "Namespace",
    "NetworkPort",
    # Security types
    "Origin",
    # Pagination types
    "PageNumber",
    "PageOffset",
    "PageSize",
    "PathParams",
    "Permissions",
    "PluginConfig",
    "PoolSize",
    "Port",
    "QueryParams",
    "RateLimitRequests",
    "RateLimitWindow",
    "ReloadEnabled",
    "RequestBody",
    # Request/Response types
    "RequestData",
    "RequestId",
    "RequestT",
    "ResponseBody",
    "ResponseData",
    "ResponseSizeBytes",
    "ResponseT",
    # Performance types
    "ResponseTimeMs",
    "Retries",
    "RetryCount",
    "Salt",
    "SessionData",
    "SessionExpiry",
    # Session types
    "SessionId",
    "Signature",
    "StatusCode",
    # Storage types
    "StorageKey",
    "StorageValue",
    "Success",
    # Type variables
    "T",
    "TableName",
    "ThroughputRps",
    "Timeout",
    # Configuration types
    "TimeoutSeconds",
    "Timestamp",
    "Token",
    "TotalCount",
    "TotalItems",
    "TraceId",
    "Url",
    # URL types
    "UrlPath",
    # User types
    "UserId",
    "UserRole",
    "Username",
    # Validation types
    "ValidationErrors",
    "Workers",
]
