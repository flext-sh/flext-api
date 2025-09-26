# API Reference - flext-api

**Complete API Documentation for FLEXT HTTP Foundation**

This reference documents all public APIs, classes, and methods provided by flext-api for HTTP client and FastAPI application development.

---

## 📋 Module Overview

| Module                   | Purpose                           | Key Classes        |
| ------------------------ | --------------------------------- | ------------------ |
| **flext_api.client**     | HTTP client implementation        | FlextApiClient     |
| **flext_api.models**     | Domain models and data structures | FlextApiModels     |
| **flext_api.config**     | Configuration management          | FlextApiConfig     |
| **flext_api.app**        | FastAPI application factory       | create_fastapi_app |
| **flext_api.utilities**  | HTTP utilities and helpers        | FlextApiUtilities  |
| **flext_api.exceptions** | HTTP-specific exceptions          | FlextApiException  |
| **flext_api.storage**    | HTTP storage and caching          | FlextApiStorage    |

---

## 🌐 HTTP Client API

### **FlextApiClient**

Main HTTP client for all HTTP operations within the FLEXT ecosystem.

```python
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels
```

#### **Constructor**

```python
def __init__(
    self,
    base_url: str = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    headers: dict[str, str] = None,
    **kwargs
) -> None:
```

**Parameters:**

- `base_url` (str, optional): Base URL for all requests
- `timeout` (float): Request timeout in seconds (default: 30.0)
- `max_retries` (int): Maximum retry attempts (default: 3, not implemented)
- `headers` (dict): Default headers for all requests
- `**kwargs`: Additional configuration options

**Example:**

```python
client = FlextApiClient(
    base_url="https://api.example.com",
    timeout=FlextApiConstants.DEFAULT_TIMEOUT,
    headers={"User-Agent": "my-service/1.0.0"}
)
```

#### **Methods**

##### **async request()**

Execute HTTP request with FlextResult error handling.

```python
async def request(
    self,
    request: FlextApiModels.HttpRequest
) -> FlextResult[FlextApiModels.HttpResponse]:
```

**Parameters:**

- `request` (HttpRequest): HTTP request model with method, URL, headers, body

**Returns:**

- `FlextResult[HttpResponse]`: Result containing HTTP response or error

**Example:**

```python
request = FlextApiModels.HttpRequest(
    method="GET",
    url="/users",
    headers={"Accept": "application/json"}
)

result = await client.request(request)
if result.is_success:
    response = result.unwrap()
    print(f"Status: {response.status_code}")
    print(f"Data: {response.body}")
```

##### **async get()**

Convenience method for GET requests.

```python
async def get(
    self,
    url: str,
    params: dict = None,
    headers: dict[str, str] = None
) -> FlextResult[FlextApiModels.HttpResponse]:
```

##### **async post()**

Convenience method for POST requests.

```python
async def post(
    self,
    url: str,
    json: dict = None,
    data: str = None,
    headers: dict[str, str] = None
) -> FlextResult[FlextApiModels.HttpResponse]:
```

##### **async close()**

Close the HTTP client and cleanup resources.

```python
async def close(self) -> None:
```

**Example:**

```python
try:
    # Use client for requests
    result = await client.get("/data")
finally:
    await client.close()
```

---

## 📄 Data Models API

### **FlextApiModels**

Container for all HTTP-related data models.

```python
from flext_api.models import FlextApiModels
```

#### **HttpRequest**

HTTP request model with validation.

```python
class HttpRequest(FlextModels.Entity):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    body: str | dict[str, object] | None = None
    timeout: int | float = 30
```

**Example:**

```python
request = FlextApiModels.HttpRequest(
    method="POST",
    url="/api/data",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer token123"
    },
    body={"key": "value", "timestamp": "2025-09-17"}
)
```

#### **HttpResponse**

HTTP response model.

```python
class HttpResponse(FlextModels.Entity):
    status_code: int
    body: str | dict[str, object] | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    url: str
    method: str
    elapsed_time: float | None = None
```

**Properties:**

```python
@property
def is_success(self) -> bool:
    """Check if response indicates success (2xx status codes)."""

@property
def is_client_error(self) -> bool:
    """Check if response indicates client error (4xx status codes)."""

@property
def is_server_error(self) -> bool:
    """Check if response indicates server error (5xx status codes)."""
```

#### **ClientConfig**

HTTP client configuration model.

```python
class ClientConfig(FlextModels.Value):
    base_url: str = "https://api.example.com"
    timeout: float = 30.0
    max_retries: int = 3
    headers: dict[str, str] = Field(default_factory=dict)
    auth_token: str | None = None
    api_key: str | None = None
```

**Methods:**

```python
def get_auth_header(self) -> dict[str, str]:
    """Get authentication header if configured."""

def get_default_headers(self) -> dict[str, str]:
    """Get all default headers including auth."""
```

#### **AppConfig**

FastAPI application configuration.

```python
class AppConfig(FlextModels.Entity):
    title: str = Field(..., min_length=1)
    app_version: str = Field(..., min_length=1)
    description: str = "FlextAPI Application"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
```

---

## ⚙️ Configuration API

### **FlextApiConfig**

Environment-aware HTTP configuration management.

```python
from flext_api.config import FlextApiConfig
```

#### **Constructor**

```python
def __init__(
    self,
    base_url: str = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    **kwargs
) -> None:
```

#### **Methods**

```python
def get_timeout(self) -> float:
    """Get configured timeout value."""

def get_max_retries(self) -> int:
    """Get configured max retry attempts."""

def get_default_headers(self) -> dict[str, str]:
    """Get default HTTP headers."""

def load_from_env(self) -> FlextResult[None]:
    """Load configuration from environment variables."""
```

**Environment Variables:**

- `HTTP_BASE_URL`: Default base URL
- `HTTP_TIMEOUT`: Request timeout in seconds
- `HTTP_MAX_RETRIES`: Maximum retry attempts
- `HTTP_AUTH_TOKEN`: Default authentication token

---

## 🚀 FastAPI Application API

### **create_fastapi_app()**

Factory function for creating FastAPI applications.

```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

def create_fastapi_app(
    config: FlextApiModels.AppConfig
) -> FastAPI:
```

**Parameters:**

- `config` (AppConfig): Application configuration with title, version, description

**Returns:**

- `FastAPI`: Configured FastAPI application instance

**Example:**

```python
config = FlextApiModels.AppConfig(
    title="My API Service",
    app_version="1.0.0",
    description="Enterprise API using flext-api",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app = create_fastapi_app(config)

# Add custom endpoints
@app.get("/api/v1/status")
async def get_status():
    return {
        "service": "my-api",
        "version": "1.0.0",
        "status": "healthy"
    }

# Run with: uvicorn main:app --reload
```

**Built-in Endpoints:**

- `GET /health` - Health check endpoint returning `{"status": "healthy"}`

---

## 🛠️ Utilities API

### **FlextApiUtilities**

HTTP utilities extending flext-core functionality.

```python
from flext_api.utilities import FlextApiUtilities
```

#### **Response Builder**

```python
class ResponseBuilder:
    @staticmethod
    def build_success_response(
        data: object = None,
        message: str = "Success",
        status_code: int = 200
    ) -> FlextResult[dict]:

    @staticmethod
    def build_error_response(
        message: str = None,
        status_code: int = 500,
        error_code: str = None
    ) -> FlextResult[dict]:
```

**Example:**

```python
# Build success response
success_result = FlextApiUtilities.ResponseBuilder.build_success_response(
    data={"users": [1, 2, 3]},
    message="Users retrieved successfully"
)

# Build error response
error_result = FlextApiUtilities.ResponseBuilder.build_error_response(
    message="User not found",
    status_code=404,
    error_code="USER_NOT_FOUND"
)
```

#### **HTTP Validator**

```python
class HttpValidator:
    @staticmethod
    def validate_url(url: str) -> FlextResult[str]:

    @staticmethod
    def validate_http_method(method: str) -> FlextResult[str]:

    @staticmethod
    def validate_status_code(code: int | str) -> FlextResult[int]:
```

#### **Data Transformer**

```python
class DataTransformer:
    @staticmethod
    def to_json(data: object) -> FlextResult[str]:

    @staticmethod
    def from_json(json_str: str) -> FlextResult[object]:

    @staticmethod
    def to_dict(data: object) -> FlextResult[dict[str, object]]:
```

---

## 💾 Storage API

### **FlextApiStorage**

HTTP-specific storage and caching.

```python
from flext_api.storage import FlextApiStorage
```

#### **Constructor**

```python
def __init__(
    self,
    config: dict = None,
    max_size: int = None,
    default_ttl: int = None
) -> None:
```

#### **Methods**

```python
def set(self, key: str, value: object, ttl: int = None) -> FlextResult[None]:
    """Store HTTP data."""

def get(self, key: str, default: object = None) -> FlextResult[object]:
    """Get HTTP data."""

def delete(self, key: str) -> FlextResult[None]:
    """Delete HTTP data."""

def exists(self, key: str) -> FlextResult[bool]:
    """Check if HTTP data exists."""

def clear(self) -> FlextResult[None]:
    """Clear all HTTP data."""

def size(self) -> FlextResult[int]:
    """Get number of stored items."""

def keys(self) -> FlextResult[list[str]]:
    """Get all keys in storage."""
```

---

## ⚠️ Exception API

### **FlextApiException**

Base exception for all HTTP-related errors.

```python
from flext_api.exceptions import FlextApiException

class FlextApiException(FlextException):
    """Base HTTP API exception."""
    pass

class HttpClientException(FlextApiException):
    """HTTP client exceptions."""
    pass

class HttpServerException(FlextApiException):
    """HTTP server exceptions."""
    pass

class ConfigurationException(FlextApiException):
    """HTTP configuration exceptions."""
    pass
```

---

## 📊 Constants API

### **FlextApiConstants**

HTTP-related constants and configuration values.

```python
from flext_api.constants import FlextApiConstants, HttpMethods

# HTTP Methods Enum
class HttpMethods(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

# Constants
class FlextApiConstants:
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRIES = 3
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    MIN_HTTP_STATUS = 100
    MAX_HTTP_STATUS = 599
```

---

## 🔄 FlextResult Integration

All HTTP operations return `FlextResult[T]` for type-safe error handling:

```python
from flext_core import FlextResult

# Successful result
result = await client.get("/data")
if result.is_success:
    response = result.unwrap()
    print(f"Data: {response.body}")

# Handle errors
if result.is_failure:
    print(f"Error: {result.error}")

# Chaining operations
result = (await client.get("/users")
    .map(lambda response: response.json())
    .filter(lambda data: len(data) > 0)
)
```

---

## 🧪 Testing Utilities

### **Test Helpers**

```python
from flext_api.testing import FlextApiTestClient

# Test client for unit tests
test_client = FlextApiTestClient(base_url="https://httpbin.org")

# Mock HTTP responses
from flext_api.testing import mock_http_response

@mock_http_response(status_code=200, json={"test": "data"})
async def test_api_call():
    result = await client.get("/test")
    assert result.is_success
```

---

## 📈 Performance Considerations

### **Connection Management**

```python
# Reuse client instances for better performance
async with FlextApiClient(base_url="https://api.example.com") as client:
    result1 = await client.get("/endpoint1")
    result2 = await client.get("/endpoint2")
    # Client automatically closed
```

### **Batch Operations**

```python
# Batch multiple requests
requests = [
    FlextApiModels.HttpRequest(method="GET", url=f"/users/{i}")
    for i in range(10)
]

results = await client.batch_request(requests)
```

---

## 🔒 Security Best Practices

### **Authentication**

```python
# Bearer token authentication
client = FlextApiClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer your-token-here"}
)

# API key authentication
config = FlextApiModels.ClientConfig(
    api_key="your-api-key",
    base_url="https://api.example.com"
)
client = FlextApiClient(config=config)
```

### **SSL/TLS Configuration**

```python
# HTTPS enforcement (default)
client = FlextApiClient(
    base_url="https://secure-api.com",  # Always use HTTPS
    verify_ssl=True  # Verify SSL certificates
)
```

---

**API Reference Complete**: This documentation covers all public APIs available in flext-api v0.9.9. For implementation examples and advanced usage patterns, see the [Getting Started Guide](getting-started.md) and [Architecture Documentation](architecture.md).
