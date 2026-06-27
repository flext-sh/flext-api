# C4 Model - Code

<!-- TOC START -->
- [Overview](#overview)
- [Code Diagram](#code-diagram)
- [Code Structure Analysis](#code-structure-analysis)
  - [Core Module Relationships](#core-module-relationships)
  - [Key Classes and Their Responsibilities](#key-classes-and-their-responsibilities)
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

    package "settings.py" as settings {
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
            class Base
            interface ProtocolInterface
        }

        package "http.py" {
            class FlextWeb
            class FlextWebClientImplementation
        }

        package "graphql.py" {
            class GraphQL
            class GraphQLClient
        }

        package "websocket.py" {
            class WebSocket
            class WebSocketClient
        }

        BaseextWebFlextWeb
        BaseaphQLGraphQL
        BasebSockeWebSocket
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
    class r
    class FlextContainer
    class FlextModels
    class FlextLogger
    class s
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
        class u.Field
        class validator
    }

    package "websockets" {
        class WebSocketClient
    }
}

' Relationships
FlextApiClient --> r : uses
FlextApiClient --> AsyncClient : uses
FlextApiModels --> BaseModel : extends
FlextApiSettings --> BaseModel : extends
FlextApi --> s : extends
FlextApiClient --> s : extends

FlextWebncClient : uses
WebSocketSockeWebSocketClient

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
├── settings.py           # Configuration management
├── constants.py        # Constants and enumerations
├── protocols/          # Protocol implementations
├── storage.py          # Storage abstractions
└── utilities.py        # Utility functions
```

### Key Classes and Their Responsibilities

#### FlextApi (api.py)

```python
```

### Test Fixtures and Mocks

```python
# conftest.py - Shared test fixtures
@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    client = Mock(spec=FlextApiClient)
    client.get.return_value = r.ok(MockHttpResponse())
    return client


@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return FlextApiSettings(base_url="https://httpbin.org", timeout=10.0, max_retries=1)


@pytest.fixture
async def async_client(test_config):
    """Real HTTP client for integration tests."""
    client = FlextApiClient(test_config)
    yield client
    await client.close()```
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
                    max_keepalive_connections=self.max_keepalive,
                ),
                timeout=httpx.Timeout(30.0),
            )

        return self._pools[base_url]

    async def close_all(self):
        """Close all connection pools."""
        for client in self._pools.values():
            await client.aclose()
        self._pools.clear()```
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

    async def set(
        self, key: str, response: FlextApiModels.HttpResponse, ttl: Optional[int] = None
    ):
        """Cache response with optional TTL."""
        async with self._lock:
            cached = CachedResponse(
                status_code=response.status_code,
                headers=response.headers,
                body=response.body,
                cached_at=datetime.now(UTC),
                ttl=ttl or self.default_ttl,
            )
            self.cache[key] = cached

    def make_cache_key(self, method: str, url: str, headers: Dict[str, str]) -> str:
        """Generate cache key from request."""
        key_data = f"{method}:{url}:{sorted(headers.items())}"
        return hashlib.sha256(key_data.encode()).hexdigest()```
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
            "oauth": OAuthAuthHandler(),
        }

    def get_handler(self, scheme: str) -> AuthHandler:
        """Get authentication handler for scheme."""
        if scheme not in self._handlers:
            raise ValueError(f"Unsupported auth scheme: {scheme}")
        return self._handlers[scheme]

    async def authenticate_request(
        self, request: FlextApiModels.HttpRequest, credentials: AuthCredentials
    ) -> p.Result[FlextApiModels.HttpRequest]:
        """Add authentication to request."""
        handler = self.get_handler(credentials.scheme)

        auth_result = await handler.authenticate(request, credentials)
        if auth_result.failure:
            return r.fail(f"Authentication failed: {auth_result.error}")

        authenticated_request = auth_result.unwrap()
        return r.ok(authenticated_request)```
______________________________________________________________________

**C4 Model Complete**: This concludes the C4 model documentation for FLEXT-API, showing the progression from high-level system context down to implementation details.
