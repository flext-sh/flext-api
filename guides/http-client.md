# HTTP Client Guide

<!-- TOC START -->
- [HTTP Client Guide](#http-client-guide)
  - [HTTP Client Basics](#http-client-basics)
    - [Creating HTTP Clients](#creating-http-clients)
    - [HTTP Methods](#http-methods)
  - [Advanced HTTP Features](#advanced-http-features)
    - [Request/Response Interceptors](#requestresponse-interceptors)
    - [Custom Headers and Authentication](#custom-headers-and-authentication)
  - [Error Handling](#error-handling)
    - [Railway Pattern Error Handling](#railway-pattern-error-handling)
    - [Error Types and Handling](#error-types-and-handling)
  - [Request Configuration](#request-configuration)
    - [Query Parameters](#query-parameters)
    - [Request Body Data](#request-body-data)
    - [Custom Headers](#custom-headers)
  - [Response Handling](#response-handling)
    - [Response Processing](#response-processing)
    - [Response Metadata](#response-metadata)
  - [Advanced Usage Patterns](#advanced-usage-patterns)
    - [Batch Operations](#batch-operations)
    - [Pagination](#pagination)
    - [Retry Logic](#retry-logic)
  - [Testing HTTP Clients](#testing-http-clients)
    - [Test Client Setup](#test-client-setup)
    - [Mocking External APIs](#mocking-external-apis)
  - [Performance Optimization](#performance-optimization)
    - [Connection Pooling](#connection-pooling)
    - [Request Batching](#request-batching)
  - [Security Best Practices](#security-best-practices)
    - [Secure Communication](#secure-communication)
    - [Sensitive Data Handling](#sensitive-data-handling)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
<!-- TOC END -->

Comprehensive guide for using the `flext_api` HTTP client with railway patterns, error handling, and advanced features.

The examples below use a small in-memory `FakeApi` transport so the code blocks can run without a network connection. In real usage, `FlextApi` performs actual HTTP requests and returns the same `p.Result[m.Api.HttpResponse]` values.

## HTTP Client Basics

### Creating HTTP Clients

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiClient, FlextApiSettings, c, m, p, r, t, u

# Basic client
settings = FlextApiSettings(
    base_url="https://api.example.com",
    timeout=30.0,
    default_headers={"User-Agent": "FLEXT-API/0.12.0"},
)
client = FlextApiClient(settings=settings)

print(client.base_url)
print(client.timeout)

# Client with authentication via default headers
auth_settings = FlextApiSettings(
    base_url="https://api.example.com",
    default_headers={"Authorization": "Bearer token123"},
)
auth_client = FlextApiClient(settings=auth_settings)

# Custom configuration
custom_settings = FlextApiSettings(
    base_url="https://api.example.com",
    timeout=60.0,
    max_retries=5,
    verify_ssl=True,
)
custom_client = FlextApiClient(settings=custom_settings)
```

### HTTP Methods

All HTTP methods on `FlextApi` return `p.Result[m.Api.HttpResponse]` for type-safe error handling.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        body: t.JsonValue = {"method": str(request.method), "url": request.url}
        if request.url.endswith("/users") and str(request.method) == "GET":
            body = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        elif request.url.endswith("/users") and str(request.method) == "POST":
            body = {"id": 3, "name": "Carlos"}
        elif request.url.endswith("/users/123") and str(request.method) in {"PUT", "PATCH"}:
            body = {"id": 123, "updated": True}
        elif request.url.endswith("/users/123") and str(request.method) == "DELETE":
            body = {"deleted": 123}
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=body,
                request_id="demo-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

# GET request
result = api.get("/users")
if result.success:
    response = result.unwrap()
    users = response.body
    print(f"Found {len(users)} users")

# GET with query parameters
result = api.get("/users", request_kwargs={"params": {"limit": "10", "offset": "0", "status": "active"}})

# GET with custom headers
result = api.get(
    "/users", headers={"Accept": "application/json", "X-API-Key": "your-api-key"}
)

# POST request
user_data = {"name": "Alice", "email": "alice@example.com"}
result = api.post("/users", data=user_data)

# PUT request
result = api.put("/users/123", data={"name": "Updated Name"})

# DELETE request
result = api.delete("/users/123")

# PATCH request
result = api.patch("/users/123", data={"email": "new@example.com"})
```

## Advanced HTTP Features

### Request/Response Interceptors

Add custom logic around requests by subclassing `FlextApi` and overriding `request`. The example returns a static response so it runs without a network connection.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class LoggingApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        logger = u.fetch_logger(__name__)
        logger.info(f"HTTP {request.method} {request.url}")
        result = super().request(request)
        if result.success:
            response = result.unwrap()
            logger.info(f"HTTP {response.status_code}")
        return result


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
logging_api = LoggingApi(settings=settings)

result = logging_api.request(
    m.Api.HttpRequest(method="GET", url="https://api.example.com/users")
)
print(result.success)
```

### Custom Headers and Authentication

```python
from __future__ import annotations
from flext_api import FlextApiClient, FlextApiSettings, c, m, p, r, t, u

# Bearer token authentication
settings = FlextApiSettings(
    base_url="https://api.example.com",
    default_headers={"Authorization": "Bearer your-jwt-token"},
)
client = FlextApiClient(settings=settings)
print(client.settings.Api.default_headers)

# API key authentication
api_key_settings = FlextApiSettings(
    base_url="https://api.example.com",
    default_headers={"X-API-Key": "your-api-key"},
)
client = FlextApiClient(settings=api_key_settings)
```

`FlextApiClient` does not accept a separate `auth` argument; configure authentication through `default_headers` or per-request headers.

## Error Handling

### Railway Pattern Error Handling

`flext_api` returns a `p.Result` for every request. Transport-level errors are reported as `result.failure` with a string message, while HTTP-level failures are available through the `m.Api.HttpResponse` model.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        if request.url.endswith("/users/999"):
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=404,
                    headers={"Content-Type": "application/json"},
                    body={"error": "User not found"},
                    request_id="demo-2",
                )
            )
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"id": 1, "name": "Alice"},
                request_id="demo-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)


def safe_api_call() -> p.Result[m.Api.HttpResponse]:
    result = api.get("/users/999")
    if result.success:
        response = result.unwrap()
        if response.status_code == 404:
            return r[m.Api.HttpResponse].fail("User not found")
        return r[m.Api.HttpResponse].ok(response)
    return r[m.Api.HttpResponse].fail(result.error or "Request failed")


result = safe_api_call()
if result.success:
    response = result.unwrap()
    print(f"User: {response.body}")
else:
    print(f"Error: {result.error}")
```

### Error Types and Handling

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        status = 200
        if request.url.endswith("/users/999"):
            status = 404
        elif request.url.endswith("/admin"):
            status = 403
        elif request.url.endswith("/rate-limited"):
            status = 429
        elif request.url.endswith("/server-error"):
            status = 500
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=status,
                headers={"Content-Type": "application/json"},
                body={"status": status},
                request_id="demo-3",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

result = api.get("/users/999")
if result.success:
    response = result.unwrap()
    if response.status_code == 404:
        print("Resource not found")
    elif response.status_code == 401:
        print("Authentication required")
    elif response.status_code == 403:
        print("Access forbidden")
    elif response.status_code == 429:
        print("Rate limit exceeded")
    elif response.status_code >= 500:
        print("Server error")
```

## Request Configuration

### Query Parameters

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"query_params": dict(request.query_params or {})},
                request_id="demo-4",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

# Simple query parameters
result = api.get("/users", request_kwargs={"params": {"active": True}})

# Multiple values for same parameter
result = api.get(
    "/users", request_kwargs={"params": {"tags": ["admin", "active"]}}
)

# Complex query parameters
result = api.get(
    "/search",
    request_kwargs={
        "params": {
            "q": "python developer",
            "location": "San Francisco",
            "remote": True,
            "salary_min": 50000,
            "salary_max": 100000,
        }
    },
)

response = result.unwrap()
print(response.body)
```

### Request Body Data

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        received = request.body
        if isinstance(received, bytes):
            received = received.decode("utf-8")
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"received": received},
                request_id="demo-5",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

# JSON-like data
user_data = {
    "name": "Alice",
    "email": "alice@example.com",
    "preferences": {"theme": "dark", "language": "en"},
}
result = api.post("/users", data=user_data)

# Raw bytes with a custom content type
xml_data = b"<user><name>Alice</name></user>"
result = api.post(
    "/users",
    data=xml_data,
    headers={"Content-Type": "application/xml"},
)

response = result.unwrap()
print(response.body)
```

### Custom Headers

```python
from __future__ import annotations
import uuid
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"headers": dict(request.headers)},
                request_id="demo-6",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

result = api.get(
    "/api/data",
    headers={
        "Accept": "application/json",
        "X-Client-Version": "1.0.0",
        "X-Request-ID": str(uuid.uuid4()),
    },
)

response = result.unwrap()
print(response.body)
```

## Response Handling

### Response Processing

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"id": 1, "name": "Alice"},
                request_id="demo-7",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

result = api.get("/users/123")
if result.success:
    response = result.unwrap()
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.body}")
    print(f"Request ID: {response.request_id}")
```

### Response Metadata

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={
                    "Content-Type": "application/json",
                    "Cache-Control": "max-age=3600",
                    "ETag": '"abc123"',
                },
                body={"ok": True},
                request_id="demo-8",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

result = api.get("/api/data")
if result.success:
    response = result.unwrap()
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Cache-Control: {response.headers.get('Cache-Control')}")
    print(f"ETag: {response.headers.get('ETag')}")
    print(f"Successful: {response.success}")
```

## Advanced Usage Patterns

### Batch Operations

```python
from __future__ import annotations
import asyncio
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=201,
                headers={"Content-Type": "application/json"},
                body={"created": True, "method": str(request.method)},
                request_id="demo-9",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)


async def batch_create_users(users: list[dict]) -> list[p.Result[m.Api.HttpResponse]]:
    async def create_one(user_data: dict) -> p.Result[m.Api.HttpResponse]:
        return api.post("/users", data=user_data)

    tasks = [create_one(user) for user in users]
    return await asyncio.gather(*tasks)


users = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"},
]

results = asyncio.run(batch_create_users(users))
for i, result in enumerate(results):
    if result.success:
        print(f"Created user {i + 1}")
    else:
        print(f"Failed to create user {i + 1}: {result.error}")
```

### Pagination

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        super().__init__(settings=settings)
        self._page = 0

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        self._page += 1
        page_size = int((request.query_params or {}).get("per_page", "50"))
        if self._page > 2:
            users: list[dict] = []
        else:
            users = [{"id": i, "name": f"User {i}"} for i in range(page_size)]
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=users,
                request_id="demo-10",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)


def get_all_users(page_size: int = 50) -> list[dict]:
    all_users: list[dict] = []
    page = 1
    while True:
        result = api.get(
            "/users", request_kwargs={"params": {"page": str(page), "per_page": str(page_size)}}
        )
        if result.failure:
            break
        users = result.unwrap().body
        if not isinstance(users, list) or not users:
            break
        all_users.extend(users)
        if len(users) < page_size:
            break
        page += 1
    return all_users


users = get_all_users(page_size=10)
print(f"Total users: {len(users)}")
```

### Retry Logic

Implement retry logic by wrapping `request` in a subclass. This example uses static responses to simulate a transient failure.

```python
from __future__ import annotations
import time
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class RetryApi(FlextApi):
    def __init__(
        self,
        settings: FlextApiSettings | None = None,
        max_retries: int = 3,
        retry_delay: float = 0.01,
    ) -> None:
        super().__init__(settings=settings)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._attempts = 0

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        self._attempts += 1
        if self._attempts < 3:
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=503,
                    headers={"Content-Type": "application/json"},
                    body={"error": "service unavailable"},
                    request_id="demo-11",
                )
            )
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"ok": True},
                request_id="demo-11",
            )
        )

    def _is_retryable(self, response: m.Api.HttpResponse) -> bool:
        return response.status_code in {408, 429, 500, 502, 503, 504}

    def get(self, url: str, **kwargs) -> p.Result[m.Api.HttpResponse]:
        for attempt in range(self.max_retries + 1):
            result = super().get(url, **kwargs)
            if result.success and not self._is_retryable(result.unwrap()):
                return result
            if attempt < self.max_retries:
                time.sleep(self.retry_delay * (2 ** attempt))
        return result


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
retry_api = RetryApi(settings=settings, max_retries=3, retry_delay=0.0)
result = retry_api.get("/data")
print(result.success)
```

## Testing HTTP Clients

### Test Client Setup

Because `pytest-markdown-docs` executes each Python block as a standalone script, the examples use plain functions and assertions rather than `pytest` fixtures or test classes.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        if request.url.endswith("/users") and str(request.method) == "GET":
            body = [{"id": 1, "name": "Alice"}]
        elif request.url.endswith("/users") and str(request.method) == "POST":
            body = {"id": 2, "name": "Test User"}
        elif request.url.endswith("/users/99999"):
            body = {"error": "not found"}
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=404,
                    headers={"Content-Type": "application/json"},
                    body=body,
                    request_id="test-1",
                )
            )
        else:
            body = {}
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200 if not request.url.endswith("/users/99999") else 404,
                headers={"Content-Type": "application/json"},
                body=body,
                request_id="test-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)


def test_get_users() -> None:
    result = api.get("/users")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    assert isinstance(response.body, list)


def test_create_user() -> None:
    user_data = {"name": "Test User", "email": "test@example.com"}
    result = api.post("/users", data=user_data)
    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    body = response.body
    assert isinstance(body, dict)
    assert body.get("name") == "Test User"


def test_error_handling() -> None:
    result = api.get("/users/99999")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 404


test_get_users()
test_create_user()
test_error_handling()
```

### Mocking External APIs

Instead of `unittest.mock`, create a small `FakeApi` or `FakeClient` subclass that returns deterministic responses. This keeps tests fast, deterministic, and independent of external services.

```python
from __future__ import annotations
from flext_api import FlextApiClient, FlextApiSettings, c, m, p, r, t, u


class FakeClient(FlextApiClient):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"id": 1, "name": "Test User"},
                request_id="mock-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
client = FakeClient(settings=settings)

result = client.request(m.Api.HttpRequest(method="GET", url="/users/1"))
assert result.success
response = result.unwrap()
assert response.status_code == 200
body = response.body
assert isinstance(body, dict)
assert body.get("name") == "Test User"
```

## Performance Optimization

### Connection Pooling

Connection pooling is handled by the underlying `httpx` client, which is created per request inside `FlextApiClient._execute_http_request`. Tuning the transport limits is not exposed through `FlextApiSettings` at the moment; keep clients as singletons and rely on the shared `fetch_global()` settings instance to reuse configured values.

```python
from __future__ import annotations
from flext_api import FlextApiClient, FlextApiSettings, c, m, p, r, t, u

settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
client = FlextApiClient(settings=settings)

# Reuse the same client instance across multiple calls to avoid repeated construction.
print(client.base_url)
```

### Request Batching

Execute multiple requests concurrently by collecting the `p.Result` values in a list and awaiting them with `asyncio.gather`, or by running them sequentially in a loop.

```python
from __future__ import annotations
import asyncio
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"ok": True},
                request_id="batch-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)


async def execute_requests(requests: list[m.Api.HttpRequest]) -> list[p.Result[m.Api.HttpResponse]]:
    async def execute_one(request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return api.request(request)

    tasks = [execute_one(request) for request in requests]
    return await asyncio.gather(*tasks)


requests = [
    m.Api.HttpRequest(method="GET", url="https://api.example.com/users/1"),
    m.Api.HttpRequest(method="GET", url="https://api.example.com/users/2"),
    m.Api.HttpRequest(method="POST", url="https://api.example.com/users", body={"name": "New User"}),
]
results = asyncio.run(execute_requests(requests))
assert all(result.success for result in results)
```

## Security Best Practices

### Secure Communication

```python
from __future__ import annotations
from flext_api import FlextApiClient, FlextApiSettings, c, m, p, r, t, u

# HTTPS only with SSL verification enabled
settings = FlextApiSettings(
    base_url="https://api.example.com",
    verify_ssl=True,
)
client = FlextApiClient(settings=settings)
print(client.settings.Api.verify_ssl)
```

Custom SSL contexts and certificate pinning are not exposed through the current `FlextApiSettings` API. Configure them at the deployment or reverse-proxy level instead.

### Sensitive Data Handling

When logging requests, redact sensitive fields before they reach the logger.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


SENSITIVE_FIELDS = {"password", "token", "secret", "key"}


def redact(data: t.JsonValue) -> t.JsonValue:
    if isinstance(data, dict):
        return {
            key: "***" if key.lower() in SENSITIVE_FIELDS else redact(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [redact(item) for item in data]
    return data


class SecureApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        logger = u.fetch_logger(__name__)
        logger.info(f"Request body: {redact(request.body)}")
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"ok": True},
                request_id="secure-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = SecureApi(settings=settings)
result = api.post("/login", data={"username": "alice", "password": "secret123"})
print(result.success)
```

## Troubleshooting

### Common Issues

**1. Connection Timeouts**

```python
from __future__ import annotations
import socket
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"ok": True},
                request_id="slow-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

# Increase the timeout for a slow endpoint
result = api.get("/slow-endpoint", request_kwargs={"timeout": 60.0})
print(result.success)

# Check basic network connectivity (does not perform an HTTP request)
try:
    socket.create_connection(("api.example.com", 443), timeout=5)
    print("Network connection OK")
except OSError:
    print("Network connection failed")
```

**2. SSL Certificate Errors**

If you are working with self-signed certificates during local development, you can disable SSL verification. Do not use this in production.

```python
from __future__ import annotations
from flext_api import FlextApiClient, FlextApiSettings, c, m, p, r, t, u

settings = FlextApiSettings(base_url="https://api.example.com", verify_ssl=False)
client = FlextApiClient(settings=settings)
print(client.settings.Api.verify_ssl)
```

Custom SSL context objects are not supported by the current `FlextApiClient` constructor.

**3. Rate Limiting**

```python
from __future__ import annotations
import time
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=429,
                headers={"Retry-After": "5"},
                body={"error": "rate limited"},
                request_id="rate-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
api = FakeApi(settings=settings)

result = api.get("/api/data")
if result.success:
    response = result.unwrap()
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            wait_time = int(retry_after)
            print(f"Rate limited. Retry after {wait_time} seconds")
            time.sleep(0)
```

This HTTP client guide provides comprehensive coverage of `flext_api`'s HTTP capabilities, from basic usage to advanced patterns and troubleshooting.
