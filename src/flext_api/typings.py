"""Type definitions for flext-api domain.

All type aliases, type variables, and generic types are centralized here.
Following FLEXT standards: types only, no logic or classes.
"""

from collections.abc import Awaitable, Callable

from flext_core import FlextTypes


class FlextApiTypings(FlextTypes):
    """Single unified API typings class following FLEXT standards.

    Contains all type definitions for API domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    type HttpMethod = str
    type HttpStatusCode = int
    type HttpHeaders = dict[str, str]
    type Headers = dict[str, str]
    type HttpParams = dict[str, str | int | float | bool | None]
    type HttpData = str | bytes | dict[str, object] | None

    type UrlPath = str
    type BaseUrl = str
    type FullUrl = str
    type EndpointPath = str

    type TimeoutSeconds = float
    type RetryCount = int
    type PageSize = int
    type ApiVersion = str

    type RequestData = dict[str, object]
    type ResponseData = dict[str, object]
    type ErrorData = dict[str, object]

    type ApiKey = str
    type BearerToken = str
    type AuthHeader = str

    type ClientId = str
    type ConnectionStatus = str
    type ClientStatus = str

    type StorageKey = str
    type StorageValue = object
    type CacheTimeout = int

    type PageNumber = int
    type PageOffset = int
    type TotalCount = int

    type ValidationErrors = list[str]
    type FieldName = str
    type FieldValue = object

    type LogLevel = str
    type RequestId = str
    type CorrelationId = str
    type TraceId = str

    type ResponseTimeMs = float
    type ResponseSizeBytes = int
    type ThroughputRps = float

    type JsonObject = dict[str, object]
    type JsonArray = list[object]
    type JsonValue = str | int | float | bool | dict[str, object] | list[object] | None

    type StatusCode = int
    type Timeout = int | float
    type Retries = int
    type PoolSize = int
    type BackoffFactor = float
    type Token = str
    type Namespace = str
    type TTL = int | None

    type MiddlewareCallable = Callable[[object], Awaitable[object]]
    type PluginConfig = dict[str, object]
    type HandlerFunction = Callable[[object], object]

    type AppTitle = str
    type AppVersion = str
    type AppDescription = str
    type DocsUrl = str
    type Host = str
    type Port = int
    type Workers = int
    type ReloadEnabled = bool

    type Origin = str
    type AllowedOrigins = list[str]
    type AllowedMethods = list[str]
    type AllowedHeaders = list[str]
    type Hash = str
    type Salt = str
    type Signature = str
    type Certificate = str

    type UserId = str
    type Username = str
    type UserRole = str
    type Permissions = list[str]
    type SessionId = str
    type SessionData = dict[str, object]
    type SessionExpiry = int

    type IpAddress = str
    type Hostname = str
    type NetworkPort = int
    type ConnectionString = str
    type DatabaseName = str
    type TableName = str
    type CollectionName = str

    type FilePath = str
    type FileName = str
    type FileExtension = str
    type DirectoryPath = str

    type MetricName = str
    type MetricValue = int | float
    type MetricTags = dict[str, str]
    type RateLimitRequests = int
    type RateLimitWindow = int

    type CacheKey = str
    type CacheValue = object
    type CacheExpiry = int

    type ErrorMessage = str
    type ErrorCode = str
    type LogMessage = str
    type LogContext = dict[str, object]
    type Success = bool
    type Timestamp = str

    type TotalItems = int
    type HasNextPage = bool

    type Url = str
    type Endpoint = str
    type PathParams = dict[str, str]
    type QueryParams = dict[str, object]
    type JsonData = dict[str, object]
    type RequestBody = str | dict[str, object] | None
    type ResponseBody = str | dict[str, object] | None


__all__ = [
    "FlextApiTypings",
]
