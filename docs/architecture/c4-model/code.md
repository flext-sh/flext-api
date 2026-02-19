# C4 Model - Code


<!-- TOC START -->
- [Overview](#overview)
- [Code Diagram](#code-diagram)
- [Code Structure Analysis](#code-structure-analysis)
  - [Core Module Relationships](#core-module-relationships)
  - [Key Classes and Their Responsibilities](#key-classes-and-their-responsibilities)
- [Protocol Implementation Details](#protocol-implementation-details)
  - [Protocol Architecture](#protocol-architecture)
  - [Protocol Registry Pattern](#protocol-registry-pattern)
- [Dependency Injection Pattern](#dependency-injection-pattern)
  - [FlextContainer Integration](#flextcontainer-integration)
- [Error Handling Architecture](#error-handling-architecture)
  - [Railway Pattern Implementation](#railway-pattern-implementation)
- [Configuration Management](#configuration-management)
  - [Pydantic-based Configuration](#pydantic-based-configuration)
- [Storage Abstraction](#storage-abstraction)
  - [Backend Interface Pattern](#backend-interface-pattern)
- [Testing Architecture](#testing-architecture)
  - [Test Structure](#test-structure)
  - [Test Fixtures and Mocks](#test-fixtures-and-mocks)
- [Performance Optimizations](#performance-optimizations)
  - [Connection Pooling](#connection-pooling)
  - [Response Caching](#response-caching)
- [Security Implementation](#security-implementation)
  - [Authentication Handlers](#authentication-handlers)
<!-- TOC END -->

## Overview

This document describes the **Code** level of the C4 model for FLEXT-API, showing the actual implementation details, class relationships, and code organization.

## Code Diagram

```plantuml
@startuml FLEXT-API Code Structure
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Code.puml

title FLEXT-API Code Structure

package "flext_api" as flext_api {
    package "__init__.py" as init {
        class FlextApi
        class FlextApiClient
        class FlextApiApp
        class FlextApiSettings
        class FlextApiConstants
        class FlextApiModels
        class FlextApiUtilities
    }

    package "api.py" as api {
        class FlextApi
        note right: Thin facade for all functionality
    }

    package "client.py" as client {
        class FlextApiClient
        class FlextWebOperations
        class LifecycleManager
        class ConfigurationManager

        FlextApiClient --> FlextWebOperations
        FlextApiClient --> LifecycleManager
        FlextApiClient --> ConfigurationManager
    }

    package "app.py" as app {
        class FlextApiApp
        class create_fastapi_app

        note right: FastAPI application factory
    }

    package "models.py" as models {
        class FlextApiModels
        class FlextApiModels.HttpRequest
        class FlextApiModels.HttpResponse
        class FlextWebEndpoint
        class ApiConfiguration

        FlextApiModels --> FlextApiModels.HttpRequest
        FlextApiModels --> FlextApiModels.HttpResponse
        FlextApiModels --> FlextWebEndpoint
        FlextApiModels --> ApiConfiguration
    }

    package "config.py" as config {
        class FlextApiSettings
        class EnvironmentConfig
        class FileConfig

        FlextApiSettings --> EnvironmentConfig
        FlextApiSettings --> FileConfig
    }

    package "constants.py" as constants {
        class FlextApiConstants
        note right: HTTP status codes, timeouts, limits
    }

    package "protocols/" as protocols {
        package "__init__.py" {
            class FlextApiProtocols
            class BaseProtocol
            interface ProtocolInterface
        }

        package "http.py" {
            class FlextWebProtocol
            class FlextWebClientImplementation
        }

        package "graphql.py" {
            class GraphQLProtocol
            class GraphQLClient
        }

        package "websocket.py" {
            class WebSocketProtocol
            class WebSocketClient
        }

        BaseProtocol <|-- FlextWebProtocol
        BaseProtocol <|-- GraphQLProtocol
        BaseProtocol <|-- WebSocketProtocol
    }

    package "storage.py" as storage {
        class FlextApiStorage
        class StorageBackend
        class S3Backend
        class GCSBackend
        class LocalBackend

        StorageBackend <|-- S3Backend
        StorageBackend <|-- GCSBackend
        StorageBackend <|-- LocalBackend
    }

    package "utilities.py" as utilities {
        class FlextApiUtilities
        class FlextWebUtilities
        class ValidationUtilities
        class EncodingUtilities
    }
}

package "flext_core" as flext_core {
    class FlextResult
    class FlextContainer
    class FlextModels
    class FlextLogger
    class FlextService
    class FlextBus
    class FlextContext
}

package "External Libraries" as external {
    package "httpx" {
        class AsyncClient
        class Client
    }

    package "fastapi" {
        class FastAPI
        class Request
        class Response
    }

    package "pydantic" {
        class BaseModel
        class Field
        class validator
    }

    package "websockets" {
        class WebSocketClientProtocol
    }
}

' Relationships
FlextApiClient --> FlextResult : uses
FlextApiClient --> AsyncClient : uses
FlextApiModels --> BaseModel : extends
FlextApiSettings --> BaseModel : extends
FlextApi --> FlextService : extends
FlextApiClient --> FlextService : extends

FlextWebProtocol --> AsyncClient : uses
WebSocketProtocol --> WebSocketClientProtocol : uses

create_fastapi_app --> FastAPI : creates
create_fastapi_app --> FlextApiClient : integrates

@enduml
```

## Code Structure Analysis

### Core Module Relationships

```
flext_api/
├── __init__.py          # Public API exports
├── api.py              # Main facade class
├── client.py           # HTTP client implementation
├── app.py              # FastAPI application factory
├── models.py           # Data models and validation
├── config.py           # Configuration management
├── constants.py        # Constants and enumerations
├── protocols/          # Protocol implementations
├── storage.py          # Storage abstractions
└── utilities.py        # Utility functions
```

### Key Classes and Their Responsibilities

#### FlextApi (api.py)

```python
class FlextApi(FlextService[FlextApiSettings]):
    """Thin facade providing access to all FLEXT-API functionality."""

    # Main entry points
    def client(self, **config) -> FlextApiClient:
        """Create HTTP client with FLEXT integration."""

    def create_fastapi_app(self, **config) -> FastAPI:
        """Create FastAPI application with FLEXT patterns."""

    def storage(self) -> FlextApiStorage:
        """Access storage abstractions."""

    # Domain access
    @property
    def models(self) -> FlextApiModels:
        """Access domain models."""

    @property
    def constants(self) -> FlextApiConstants:
        """Access constants and enumerations."""
```

#### FlextApiClient (client.py)

```python
class FlextApiClient(FlextService[None]):
    """Enterprise HTTP client with railway pattern integration."""

    # Core HTTP methods
    def get(self, url: str, **kwargs) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP GET request."""

    def post(self, url: str, data=None, **kwargs) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP POST request."""

    def put(self, url: str, data=None, **kwargs) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP PUT request."""

    def delete(self, url: str, **kwargs) -> FlextResult[FlextApiModels.HttpResponse]:
        """HTTP DELETE request."""

    # Advanced features
    def request(self, request: FlextApiModels.HttpRequest) -> FlextResult[FlextApiModels.HttpResponse]:
        """Generic HTTP request."""

    async def arequest(self, request: FlextApiModels.HttpRequest) -> FlextResult[FlextApiModels.HttpResponse]:
        """Async HTTP request."""
```

#### FlextApiModels (models.py)

```python
class FlextApiModels(FlextModels):
    """Pydantic models extending flext-core base classes."""

    class FlextApiModels.HttpRequest(FlextModels.FlextApiModels.HttpRequest):
        """HTTP request model with validation."""
        method: str
        url: str
        headers: Dict[str, str] = {}
        body: Optional[object] = None
        timeout: float = 30.0

        @computed_field
        def full_url(self) -> str:
            """Computed full URL with protocol."""

        @computed_field
        def request_size(self) -> int:
            """Request body size in bytes."""

    class FlextApiModels.HttpResponse(FlextModels.FlextApiModels.HttpResponse):
        """HTTP response model with validation."""
        status_code: int
        headers: Dict[str, str]
        body: object
        response_time: float

        @computed_field
        def is_success(self) -> bool:
            """Check if response indicates success."""

        @computed_field
        def content_type(self) -> str:
            """Extract content type from headers."""
```

## Protocol Implementation Details

### Protocol Architecture

```python
# Protocol base interface
class BaseProtocol(ABC):
    """Abstract base class for all protocols."""

    @abstractmethod
    def create_client(self, config: dict) -> object:
        """Create protocol-specific client."""
        pass

    @abstractmethod
    async def execute_request(self, request: object) -> FlextResult[object]:
        """Execute protocol-specific request."""
        pass

# HTTP Protocol Implementation
class FlextWebProtocol(BaseProtocol):
    """HTTP/REST protocol implementation."""

    def create_client(self, config: dict) -> FlextApiClient:
        """Create HTTP client instance."""
        return FlextApiClient(**config)

    async def execute_request(self, request: FlextApiModels.HttpRequest) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request with error handling."""
        try:
            # HTTP-specific implementation
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=request.full_url,
                    headers=request.headers,
                    content=request.body,
                    timeout=request.timeout
                )

                return FlextResult.ok(FlextApiModels.HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.text,
                    response_time=response.elapsed.total_seconds()
                ))

        except Exception as e:
            return FlextResult.fail(f"HTTP request failed: {e}")
```

### Protocol Registry Pattern

```python
class ProtocolRegistry:
    """Registry for protocol implementations."""

    def __init__(self):
        self._protocols: Dict[str, Type[BaseProtocol]] = {}

    def register(self, name: str, protocol_class: Type[BaseProtocol]):
        """Register a protocol implementation."""
        self._protocols[name] = protocol_class

    def get_protocol(self, name: str) -> BaseProtocol:
        """Get protocol instance by name."""
        if name not in self._protocols:
            raise ValueError(f"Protocol '{name}' not registered")

        return self._protocols[name]()

    def list_protocols(self) -> t.StringList:
        """List all registered protocols."""
        return list(self._protocols.keys())
```

## Dependency Injection Pattern

### FlextContainer Integration

```python
# Service registration in FlextApi.__init__
container = FlextContainer.get_global()

# Register core services
container.register("http_client", lambda: FlextApiClient())
container.register("fastapi_app_factory", lambda: create_fastapi_app)
container.register("storage_backend", lambda: FlextApiStorage())
container.register("config_manager", lambda: FlextApiSettings())

# Usage in application code
http_client = container.get("http_client")
storage = container.get("storage_backend")

# Railway pattern error handling
if http_client.is_failure:
    logger.error(f"Failed to get HTTP client: {http_client.error}")
    return

if storage.is_failure:
    logger.error(f"Failed to get storage: {storage.error}")
    return

# Use services
client = http_client.unwrap()
store = storage.unwrap()
```

## Error Handling Architecture

### Railway Pattern Implementation

```python
# All public methods return FlextResult[T]
def get(self, url: str, **kwargs) -> FlextResult[FlextApiModels.HttpResponse]:
    """HTTP GET with comprehensive error handling."""

    # Input validation
    validation_result = self._validate_url(url)
    if validation_result.is_failure:
        return FlextResult.fail(validation_result.error)

    # Request building
    request_result = self._build_request("GET", url, **kwargs)
    if request_result.is_failure:
        return FlextResult.fail(f"Request building failed: {request_result.error}")

    # HTTP execution
    response_result = await self._execute_request(request_result.unwrap())
    if response_result.is_failure:
        return FlextResult.fail(f"HTTP execution failed: {response_result.error}")

    # Response processing
    processed_result = self._process_response(response_result.unwrap())
    if processed_result.is_failure:
        return FlextResult.fail(f"Response processing failed: {processed_result.error}")

    return processed_result

# Usage with railway pattern
result = client.get("/api/users")

# Chained operations
user_data = (result
    .flat_map(lambda resp: parse_json(resp.body))
    .map(lambda data: extract_users(data))
    .map_error(lambda err: log_error(f"User fetch failed: {err}"))
)

if user_data.is_success:
    users = user_data.unwrap()
    print(f"Fetched {len(users)} users")
```

## Configuration Management

### Pydantic-based Configuration

```python
class FlextApiSettings(BaseModel):
    """Configuration model with validation."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )

    # HTTP client settings
    base_url: Optional[str] = None
    timeout: float = Field(default=30.0, gt=0, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, gt=0, le=60)

    # Authentication
    auth_type: AuthType = AuthType.NONE
    api_key: Optional[str] = None
    jwt_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    # SSL/TLS settings
    verify_ssl: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None

    # Connection settings
    max_connections: int = Field(default=100, gt=0, le=1000)
    max_keepalive: int = Field(default=20, gt=0, le=100)

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v):
        """Validate base URL format."""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")
        return v

    @model_validator(mode="after")
    def validate_auth_config(self):
        """Validate authentication configuration consistency."""
        if self.auth_type == AuthType.API_KEY and not self.api_key:
            raise ValueError("API key required when auth_type is API_KEY")

        if self.auth_type == AuthType.JWT and not self.jwt_token:
            raise ValueError("JWT token required when auth_type is JWT")

        if self.auth_type == AuthType.BASIC and (not self.username or not self.password):
            raise ValueError("Username and password required for basic auth")

        return self
```

## Storage Abstraction

### Backend Interface Pattern

```python
class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO,
        path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> FlextResult[str]:
        """Upload file to storage."""
        pass

    @abstractmethod
    async def download_file(self, path: str) -> FlextResult[bytes]:
        """Download file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> FlextResult[bool]:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def list_files(self, prefix: str = "") -> FlextResult[List[FileInfo]]:
        """List files in storage."""
        pass

    @abstractmethod
    async def get_file_info(self, path: str) -> FlextResult[FileInfo]:
        """Get file information."""
        pass

# S3 Implementation
class S3Backend(StorageBackend):
    """Amazon S3 storage backend."""

    def __init__(self, config: Dict[str, object]):
        self.bucket = config["bucket"]
        self.client = boto3.client(
            "s3",
            aws_access_key_id=config.get("access_key"),
            aws_secret_access_key=config.get("secret_key"),
            region_name=config.get("region", "us-east-1")
        )

    async def upload_file(
        self,
        file: BinaryIO,
        path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> FlextResult[str]:
        """Upload file to S3."""
        try:
            self.client.upload_fileobj(
                file,
                self.bucket,
                path,
                ExtraArgs={
                    "Metadata": metadata or {},
                    "ACL": "private"
                }
            )
            return FlextResult.ok(f"s3://{self.bucket}/{path}")
        except Exception as e:
            return FlextResult.fail(f"S3 upload failed: {e}")
```

## Testing Architecture

### Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_client.py     # HTTP client tests
│   ├── test_models.py     # Model validation tests
│   ├── test_config.py     # Configuration tests
│   └── test_utilities.py  # Utility function tests
├── integration/           # Integration tests
│   ├── test_httpbin.py    # Real HTTP service tests
│   └── test_storage.py    # Storage backend tests
├── e2e/                   # End-to-end tests
│   └── test_full_flow.py  # Complete workflow tests
└── conftest.py           # Shared test fixtures
```

### Test Fixtures and Mocks

```python
# conftest.py - Shared test fixtures
@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    client = Mock(spec=FlextApiClient)
    client.get.return_value = FlextResult.ok(MockHttpResponse())
    return client

@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return FlextApiSettings(
        base_url="https://httpbin.org",
        timeout=10.0,
        max_retries=1
    )

@pytest.fixture
async def async_client(test_config):
    """Real HTTP client for integration tests."""
    client = FlextApiClient(test_config)
    yield client
    await client.close()
```

## Performance Optimizations

### Connection Pooling

```python
class ConnectionPoolManager:
    """HTTP connection pool management."""

    def __init__(self, max_connections: int = 100, max_keepalive: int = 20):
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self._pools: Dict[str, httpx.AsyncClient] = {}

    async def get_client(self, base_url: str) -> httpx.AsyncClient:
        """Get or create client for base URL."""
        if base_url not in self._pools:
            self._pools[base_url] = httpx.AsyncClient(
                base_url=base_url,
                limits=httpx.Limits(
                    max_connections=self.max_connections,
                    max_keepalive_connections=self.max_keepalive
                ),
                timeout=httpx.Timeout(30.0)
            )

        return self._pools[base_url]

    async def close_all(self):
        """Close all connection pools."""
        for client in self._pools.values():
            await client.aclose()
        self._pools.clear()
```

### Response Caching

```python
class ResponseCache:
    """HTTP response caching with TTL."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache = TTLCache(maxsize=max_size, ttl=default_ttl)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[CachedResponse]:
        """Get cached response."""
        async with self._lock:
            return self.cache.get(key)

    async def set(self, key: str, response: FlextApiModels.HttpResponse, ttl: Optional[int] = None):
        """Cache response with optional TTL."""
        async with self._lock:
            cached = CachedResponse(
                status_code=response.status_code,
                headers=response.headers,
                body=response.body,
                cached_at=datetime.now(UTC),
                ttl=ttl or self.default_ttl
            )
            self.cache[key] = cached

    def make_cache_key(self, method: str, url: str, headers: Dict[str, str]) -> str:
        """Generate cache key from request."""
        key_data = f"{method}:{url}:{sorted(headers.items())}"
        return hashlib.sha256(key_data.encode()).hexdigest()
```

## Security Implementation

### Authentication Handlers

```python
class AuthenticationManager:
    """Multi-scheme authentication manager."""

    def __init__(self):
        self._handlers: Dict[str, AuthHandler] = {
            "jwt": JwtAuthHandler(),
            "api_key": ApiKeyAuthHandler(),
            "basic": BasicAuthHandler(),
            "oauth": OAuthAuthHandler()
        }

    def get_handler(self, scheme: str) -> AuthHandler:
        """Get authentication handler for scheme."""
        if scheme not in self._handlers:
            raise ValueError(f"Unsupported auth scheme: {scheme}")
        return self._handlers[scheme]

    async def authenticate_request(
        self,
        request: FlextApiModels.HttpRequest,
        credentials: AuthCredentials
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Add authentication to request."""
        handler = self.get_handler(credentials.scheme)

        auth_result = await handler.authenticate(request, credentials)
        if auth_result.is_failure:
            return FlextResult.fail(f"Authentication failed: {auth_result.error}")

        authenticated_request = auth_result.unwrap()
        return FlextResult.ok(authenticated_request)
```

---

**C4 Model Complete**: This concludes the C4 model documentation for FLEXT-API, showing the progression from high-level system context down to implementation details.
