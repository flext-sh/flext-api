# API Reference - flext-api

**Complete API documentation** for flext-api HTTP client and FastAPI integration library.

> **Status**: Version 0.9.0 - Based on actual src/ implementation

---

## 📦 Package Exports

### Main Exports

```python
from flext_api import (
    # Core HTTP components
    FlextApi,              # Main HTTP facade
    FlextApiClient,        # HTTP client implementation
    create_flext_api,      # Client factory function

    # Configuration and models
    FlextApiConfig,        # Configuration management
    FlextApiModels,        # Domain models
    FlextApiConstants,     # HTTP constants

    # Utilities and support
    FlextApiUtilities,     # Helper functions
    FlextApiStorage,       # Storage abstraction
    FlextApiExceptions,    # Exception hierarchy
    FlextApiProtocols,     # Type protocols
    FlextApiTypes,         # Type definitions

    # Enums
    StorageBackend,        # Storage backend options
)

# FastAPI integration (separate import)
from flext_api.app import create_fastapi_app
```

---

## 🌐 HTTP Client

### FlextApiClient

Main HTTP client for making async HTTP requests.

```python
from flext_api import FlextApiClient

class FlextApiClient:
    def __init__(
        self,
        base_url: str = "https://api.example.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: dict[str, str] | None = None
    ) -> None: ...

    async def request(
        self,
        request: FlextApiModels.HttpRequest
    ) -> FlextApiModels.HttpResponse: ...

    async def get(self, url: str, **kwargs) -> FlextApiModels.HttpResponse: ...
    async def post(self, url: str, **kwargs) -> FlextApiModels.HttpResponse: ...
    async def put(self, url: str, **kwargs) -> FlextApiModels.HttpResponse: ...
    async def delete(self, url: str, **kwargs) -> FlextApiModels.HttpResponse: ...
```

#### Example Usage

```python
import asyncio
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels

async def example():
    client = FlextApiClient(
        base_url="https://httpbin.org",
        timeout=30,
        headers={"User-Agent": "flext-api/0.9.0"}
    )

    # Using request method
    request = FlextApiModels.HttpRequest(
        method="GET",
        url="/get",
        headers={"Accept": "application/json"}
    )

    response = await client.request(request)
    print(f"Status: {response.status_code}")

    # Using convenience methods
    response = await client.get("/get")
    response = await client.post("/post", json={"key": "value"})

asyncio.run(example())
```

### FlextApi

High-level facade for HTTP operations.

```python
from flext_api import FlextApi

class FlextApi:
    def __init__(self, base_url: str | None = None) -> None: ...

    async def get(self, url: str) -> dict: ...
    async def post(self, url: str, data: dict) -> dict: ...
    # Additional HTTP methods...
```

---

## 🏗️ Models

### FlextApiModels

Domain models for HTTP operations using Pydantic v2.

```python
from flext_api.models import FlextApiModels

# HTTP Request/Response Models
class HttpRequest(FlextModels.Entity):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    body: str | dict[str, object] | None = None
    timeout: int | float = 30

class HttpResponse(FlextModels.Entity):
    status_code: int
    body: str | dict[str, object] | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    url: str
    method: str
    elapsed_time: float | None = None

    @property
    def is_success(self) -> bool: ...
    @property
    def is_client_error(self) -> bool: ...
    @property
    def is_server_error(self) -> bool: ...

# Configuration Models
class ClientConfig(FlextModels.Value):
    base_url: str = "https://api.example.com"
    timeout: float = 30.0
    max_retries: int = 3
    headers: dict[str, str] = Field(default_factory=dict)
    auth_token: str | None = None

    def get_auth_header(self) -> dict[str, str]: ...
    def get_default_headers(self) -> dict[str, str]: ...

# FastAPI Configuration
class AppConfig(FlextModels.Entity):
    title: str = Field(..., min_length=1)
    app_version: str = Field(..., min_length=1)  # Note: app_version, not version
    description: str = "FlextAPI Application"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
```

#### Usage Examples

```python
from flext_api.models import FlextApiModels

# Create HTTP request
request = FlextApiModels.HttpRequest(
    method="POST",
    url="https://api.example.com/data",
    headers={"Content-Type": "application/json"},
    body={"key": "value"},
    timeout=30
)

# Client configuration
config = FlextApiModels.ClientConfig(
    base_url="https://api.example.com",
    timeout=60,
    auth_token="your-token-here"
)

# FastAPI app configuration
app_config = FlextApiModels.AppConfig(
    title="My API",
    app_version="1.0.0",  # Required field
    description="My FastAPI application"
)
```

---

## 🚀 FastAPI Integration

### create_fastapi_app

Factory function for creating FastAPI applications.

```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

def create_fastapi_app(config: FlextApiModels.AppConfig) -> object:
    """Create FastAPI application with the given configuration.

    Args:
        config: Application configuration

    Returns:
        FastAPI application instance with health endpoint
    """
```

#### Example Usage

```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels
import uvicorn

# Create configuration
config = FlextApiModels.AppConfig(
    title="My FastAPI Application",
    app_version="2.1.0",
    description="Built with flext-api",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create app
app = create_fastapi_app(config)

# The app automatically includes:
# - Health check endpoint at /health
# - Proper OpenAPI documentation
# - CORS and security headers

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## ⚙️ Configuration

### FlextApiConfig

Configuration management with environment variable support.

```python
from flext_api.config import FlextApiConfig

class FlextApiConfig:
    def __init__(self) -> None: ...

    # Configuration methods
    def get_timeout(self) -> float: ...
    def get_max_retries(self) -> int: ...
    def get_default_headers(self) -> dict[str, str]: ...
```

---

## 📊 Constants

### FlextApiConstants

HTTP-specific constants and default values.

```python
from flext_api.constants import FlextApiConstants, HttpMethods

class FlextApiConstants:
    DEFAULT_BASE_URL = "https://api.example.com"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRIES = 3
    DEFAULT_PAGE_SIZE = 20

    # HTTP Status Code Ranges
    SUCCESS_END = 300
    CLIENT_ERROR_START = 400
    SERVER_ERROR_START = 500
    SERVER_ERROR_END = 600

    # Port ranges
    MIN_PORT = 1
    MAX_PORT = 65535

# HTTP Methods enum
class HttpMethods:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
```

---

## 🛠️ Utilities

### FlextApiUtilities

Helper functions and utilities.

```python
from flext_api.utilities import FlextApiUtilities

class FlextApiUtilities:
    # Utility methods for HTTP operations
    @staticmethod
    def parse_url(url: str) -> dict: ...

    @staticmethod
    def build_query_string(params: dict) -> str: ...

    @staticmethod
    def sanitize_headers(headers: dict) -> dict: ...
```

---

## 💾 Storage

### FlextApiStorage

Storage abstraction for HTTP caching and persistence.

```python
from flext_api.storage import FlextApiStorage
from flext_api.enums import StorageBackend

class FlextApiStorage:
    def __init__(
        self,
        backend: StorageBackend = StorageBackend.MEMORY
    ) -> None: ...

    async def get(self, key: str) -> object | None: ...
    async def set(self, key: str, value: object) -> None: ...
    async def delete(self, key: str) -> bool: ...

# Available storage backends
class StorageBackend(Enum):
    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
```

---

## 🚨 Exceptions

### FlextApiExceptions

HTTP-specific exception hierarchy.

```python
from flext_api.exceptions import FlextApiExceptions

class FlextApiExceptions:
    class FlextApiError(Exception): ...
    class HttpError(FlextApiError): ...
    class ClientError(HttpError): ...
    class ServerError(HttpError): ...
    class TimeoutError(FlextApiError): ...
    class ConfigurationError(FlextApiError): ...
```

---

## 🔍 Type System

### FlextApiTypes

Type definitions and aliases.

```python
from flext_api.typings import FlextApiTypes

class FlextApiTypes:
    # Type aliases for common patterns
    Headers = dict[str, str]
    QueryParams = dict[str, str | int | float | bool]
    RequestBody = str | dict[str, object] | None
    ResponseBody = str | dict[str, object] | None
```

### FlextApiProtocols

Type protocols for interfaces.

```python
from flext_api.protocols import FlextApiProtocols

class FlextApiProtocols:
    class HttpClientProtocol(Protocol):
        async def request(self, request: HttpRequest) -> HttpResponse: ...

    class StorageProtocol(Protocol):
        async def get(self, key: str) -> object | None: ...
        async def set(self, key: str, value: object) -> None: ...
```

---

## 🏭 Factory Functions

### create_flext_api

Factory function for creating configured FlextApi instances.

```python
from flext_api import create_flext_api

def create_flext_api(
    base_url: str | None = None,
    **kwargs
) -> FlextApi:
    """Create a configured FlextApi instance."""
    pass
```

---

## 💡 Usage Patterns

### Complete Example

```python
import asyncio
from flext_api import FlextApiClient, FlextApiConfig
from flext_api.models import FlextApiModels
from flext_api.app import create_fastapi_app

async def complete_example():
    # 1. Create HTTP client
    client = FlextApiClient(
        base_url="https://httpbin.org",
        timeout=30
    )

    # 2. Make HTTP request
    request = FlextApiModels.HttpRequest(
        method="GET",
        url="/json",
        headers={"Accept": "application/json"}
    )

    response = await client.request(request)

    if response.is_success:
        print("Success:", response.body)
    else:
        print("Error:", response.status_code)

    # 3. Create FastAPI app
    app_config = FlextApiModels.AppConfig(
        title="Example API",
        app_version="1.0.0"
    )

    app = create_fastapi_app(app_config)
    print("FastAPI app created with health endpoint at /health")

if __name__ == "__main__":
    asyncio.run(complete_example())
```

---

## 🚧 Implementation Status

### Working Components ✅

- **FlextApiClient**: Async HTTP client with connection pooling
- **FlextApiModels**: Pydantic v2 domain models
- **create_fastapi_app**: FastAPI application factory
- **Configuration**: Environment-aware settings
- **Type System**: Complete type annotations

### Known Issues ⚠️

- **Test Coverage**: 78% pass rate (261/334 tests passing)
- **Missing Constants**: Some tests expect HttpMethods constants not available
- **Model Validation**: Stricter Pydantic validation than expected by some tests

### Quality Gates ✅

- **Linting**: Ruff passes with zero violations
- **Type Checking**: MyPy strict mode passes
- **Security**: Bandit passes with no critical issues

---

**Version**: 0.9.0
**Last Updated**: September 17, 2025
**Validation**: Based on actual src/ implementation and exports