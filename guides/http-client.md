# HTTP Client Guide

<!-- TOC START -->
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

Comprehensive guide for using the FLEXT-API HTTP client with railway patterns, error handling, and advanced features.

## HTTP Client Basics

### Creating HTTP Clients

```python notest
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import d
from flext_core import FlextDispatcher
from flext_core import e
from flext_core import h
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u

# Basic client
client = FlextApiClient(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"User-Agent": "FLEXT-API/0.9.9"},
)

# Client with authentication
auth_client = FlextApiClient(
    base_url="https://api.example.com",
    auth={"username": "user", "password": "pass"},
    headers={"Authorization": "Bearer token123"},
)

# Client with custom configuration
custom_client = FlextApiClient(
    base_url="https://api.example.com",
    timeout=60.0,
    max_retries=5,
    verify_ssl=True,
    proxies={"http": "http://proxy.company.com:8080"},
)
```

### HTTP Methods

All HTTP methods return `r[T]` for type-safe error handling.

```python notest
# GET request
result = client.get("/users")
if result.success:
    users = result.unwrap()
    u.Cli.print(f"Found {len(users)} users")

# GET with query parameters
result = client.get("/users", params={"limit": 10, "offset": 0, "status": "active"})

# GET with custom headers
result = client.get(
    "/users", headers={"Accept": "application/json", "X-API-Key": "your-api-key"}
)

# POST request
user_data = {"name": "Alice", "email": "alice@example.com"}
result = client.post("/users", json=user_data)

# PUT request
result = client.put("/users/123", json={"name": "Updated Name"})

# DELETE request
result = client.delete("/users/123")

# PATCH request
result = client.patch("/users/123", json={"email": "new@example.com"})
```

## Advanced HTTP Features

### Request/Response Interceptors

Add custom logic before and after HTTP requests.

```python notest
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import d
from flext_core import FlextDispatcher
from flext_core import e
from flext_core import h
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u


class LoggingClient(FlextApiClient):
    """HTTP client with automatic request/response logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = u.fetch_logger(__name__)

    def _log_request(self, method: str, url: str, **kwargs):
        """Log outgoing request."""
        self.logger.info(
            "HTTP Request",
            extra={
                "method": method,
                "url": url,
                "headers": kwargs.get("headers", {}),
                "params": kwargs.get("params", {}),
                "data_size": len(str(kwargs.get("json", kwargs.get("data", "")))),
            },
        )

    def _log_response(self, response, duration_ms: float):
        """Log response details."""
        self.logger.info(
            "HTTP Response",
            extra={
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "content_length": len(response.content) if response.content else 0,
            },
        )

    def get(self, url, **kwargs):
        self._log_request("GET", url, **kwargs)
        start_time = time.time()

        result = super().get(url, **kwargs)

        duration_ms = (time.time() - start_time) * 1000
        if result.success:
            self._log_response(result.unwrap(), duration_ms)

        return result
```

### Custom Headers and Authentication

```python notest
# Bearer token authentication
client = FlextApiClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer your-jwt-token"},
)

# API key authentication
client = FlextApiClient(
    base_url="https://api.example.com", headers={"X-API-Key": "your-api-key"}
)

# Basic authentication
client = FlextApiClient(
    base_url="https://api.example.com", auth=("username", "password")
)


# Custom authentication handler
class CustomAuth:
    def __init__(self, token: str):
        self.token = token

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


custom_auth = CustomAuth("your-token")
client = FlextApiClient(base_url="https://api.example.com", auth=custom_auth)
```

## Error Handling

### Railway Pattern Error Handling

FLEXT-API uses the railway pattern for type-safe error handling.

```python notest
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import d
from flext_core import FlextDispatcher
from flext_core import e
from flext_core import h
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u


def safe_api_call():
    """Example of safe API call with error handling."""
    result = client.get("/users/123")

    # Type-safe error handling
    if result.success:
        user = result.unwrap()
        return r[dict].ok(user)
    else:
        error = result.error
        # Handle different error types
        if error.code == "NOT_FOUND":
            return r[dict].fail("User not found")
        elif error.code == "UNAUTHORIZED":
            return r[dict].fail("Authentication required")
        else:
            return r[dict].fail(f"API error: {error.message}")


# Usage
result = safe_api_call()
if result.success:
    user = result.unwrap()
    u.Cli.print(f"User: {user['name']}")
else:
    u.Cli.print(f"Error: {result.error}")
```

### Error Types and Handling

```python notest
# HTTP error responses
try:
    result = client.get("/users/999")
    if result.failure:
        error = result.error

        # Handle specific HTTP errors
        if error.status_code == 404:
            u.Cli.print("Resource not found")
        elif error.status_code == 401:
            u.Cli.print("Authentication required")
        elif error.status_code == 403:
            u.Cli.print("Access forbidden")
        elif error.status_code == 429:
            u.Cli.print("Rate limit exceeded")
        elif error.status_code >= 500:
            u.Cli.print("Server error")

except Exception as e:
    u.Cli.print(f"Unexpected error: {e}")
```

## Request Configuration

### Query Parameters

```python notest
# Simple query parameters
result = client.get("/users", params={"active": True})

# Multiple values for same parameter
result = client.get(
    "/users", params={"tags": ["REDACTED_LDAP_BIND_PASSWORD", "active"]}
)

# Complex query parameters
result = client.get(
    "/search",
    params={
        "q": "python developer",
        "location": "San Francisco",
        "remote": True,
        "salary_min": 50000,
        "salary_max": 100000,
    },
)
```

### Request Body Data

```python notest
# JSON data (default)
user_data = {
    "name": "Alice",
    "email": "alice@example.com",
    "preferences": {"theme": "dark", "language": "en"},
}
result = client.post("/users", json=user_data)

# Form data
form_data = {
    "name": "Alice",
    "email": "alice@example.com",
    "file": open("resume.pdf", "rb"),
}
result = client.post("/users", data=form_data)

# Raw data
xml_data = "<user><name>Alice</name></user>"
result = client.post(
    "/users", data=xml_data, headers={"Content-Type": "application/xml"}
)
```

### Custom Headers

```python notest
# Per-request headers
result = client.get(
    "/api/data",
    headers={
        "Accept": "application/json",
        "X-Client-Version": "1.0.0",
        "X-Request-ID": str(uuid.uuid4()),
    },
)

# Conditional headers
result = client.get(
    "/api/data",
    headers={
        "If-Modified-Since": "Wed, 21 Oct 2025 07:28:00 GMT",
        "If-None-Match": '"abc123"',
    },
)

# Custom content types
result = client.post(
    "/api/upload",
    data=binary_data,
    headers={"Content-Type": "application/octet-stream"},
)
```

## Response Handling

### Response Processing

```python notest
# Get response t.JsonValue
result = client.get("/users/123")
if result.success:
    response = result.unwrap()

    # Access response data
    u.Cli.print(f"Status: {response.status_code}")
    u.Cli.print(f"Headers: {dict(response.headers)}")
    u.Cli.print(f"Content: {response.text}")

    # Parse JSON response
    user_data = response.json()
    u.Cli.print(f"User: {user_data['name']}")

    # Access raw response content
    raw_content = response.content
    u.Cli.print(f"Raw content length: {len(raw_content)}")
```

### Response Metadata

```python notest
# Response timing
result = client.get("/slow-endpoint")
if result.success:
    response = result.unwrap()
    u.Cli.print(f"Request took: {response.elapsed.total_seconds()}s")

# Response headers
result = client.get("/api/data")
if result.success:
    response = result.unwrap()
    u.Cli.print(f"Content-Type: {response.headers.get('Content-Type')}")
    u.Cli.print(f"Cache-Control: {response.headers.get('Cache-Control')}")
    u.Cli.print(f"ETag: {response.headers.get('ETag')}")
```

## Advanced Usage Patterns

### Batch Operations

```python notest
from typing import List


async def batch_create_users(users: List[dict]) -> List[r[dict]]:
    """Create multiple users in parallel."""
    import asyncio

    async def create_user(user_data: dict) -> p.Result[dict]:
        return client.post("/users", json=user_data)

    # Execute requests concurrently
    tasks = [create_user(user) for user in users]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results


# Usage
users = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"},
]

results = await batch_create_users(users)

for i, result in enumerate(results):
    if result.success:
        u.Cli.print(f"✅ Created user {i + 1}")
    else:
        u.Cli.print(f"❌ Failed to create user {i + 1}: {result.error}")
```

### Pagination

```python notest
def get_all_users(page_size: int = 50) -> List[dict]:
    """Get all users with pagination."""
    all_users = []
    page = 1

    while True:
        result = client.get("/users", params={"page": page, "per_page": page_size})

        if result.failure:
            break

        users = result.unwrap()
        if not users:
            break

        all_users.extend(users)

        # Check if we've reached the last page
        if len(users) < page_size:
            break

        page += 1

    return all_users


# Usage
users = get_all_users(page_size=100)
u.Cli.print(f"Total users: {len(users)}")
```

### Retry Logic

```python notest
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import d
from flext_core import FlextDispatcher
from flext_core import e
from flext_core import h
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u


class RetryClient(FlextApiClient):
    """HTTP client with custom retry logic."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_retries = kwargs.get("max_retries", 3)
        self.retry_delay = kwargs.get("retry_delay", 1.0)

    def get(self, url, **kwargs):
        """GET request with retry logic."""
        for attempt in range(self.max_retries + 1):
            result = super().get(url, **kwargs)

            if result.success:
                return result

            # Check if error is retryable
            if not self._is_retryable_error(result.error):
                return result

            if attempt < self.max_retries:
                time.sleep(self.retry_delay * (2**attempt))  # Exponential backoff

        return result

    def _is_retryable_error(self, error) -> bool:
        """Check if error is worth retrying."""
        retryable_codes = [408, 429, 500, 502, 503, 504]
        return error.status_code in retryable_codes


# Usage
retry_client = RetryClient(
    base_url="https://unreliable-api.com", max_retries=3, retry_delay=1.0
)

result = retry_client.get("/data")
```

## Testing HTTP Clients

### Test Client Setup

```python notest
import pytest
from flext_api import FlextApiClient
from flext_api import FlextApiTestClient


class TestUserAPI:
    def setup_method(self):
        # Create test client
        self.client = FlextApiTestClient(app)

        # Or create real client for integration tests
        self.real_client = FlextApiClient(
            base_url="https://jsonplaceholder.typicode.com"
        )

    def test_get_users(self):
        """Test GET /users endpoint."""
        result = self.client.get("/users")

        assert result.success
        response = result.unwrap()
        assert response.status_code == 200

        users = response.json()
        assert isinstance(users, list)

    def test_create_user(self):
        """Test POST /users endpoint."""
        user_data = {"name": "Test User", "email": "test@example.com"}
        result = self.client.post("/users", json=user_data)

        assert result.success
        response = result.unwrap()
        assert response.status_code == 201

        user = response.json()
        assert user["name"] == "Test User"
        assert "id" in user

    def test_error_handling(self):
        """Test error response handling."""
        result = self.client.get("/users/99999")

        assert result.failure
        error = result.error
        assert error.status_code == 404
        assert "not found" in error.message.lower()
```

### Mocking External APIs

```python notest
from unittest.mock import Mock, patch
import pytest


@patch("flext_api.client.httpx.Client")
def test_external_api_call(mock_http_client):
    """Test HTTP client with mocked external API."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Test User"}
    mock_response.headers = {"Content-Type": "application/json"}

    mock_http_client.return_value.request.return_value = mock_response

    # Test client behavior
    client = FlextApiClient(base_url="https://api.example.com")
    result = client.get("/users/1")

    assert result.success
    user = result.unwrap()
    assert user["name"] == "Test User"
```

## Performance Optimization

### Connection Pooling

```python notest
# Configure connection pooling for better performance
client = FlextApiClient(
    base_url="https://api.example.com",
    transport=httpx.HTTPTransport(
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    ),
)
```

### Request Batching

```python notest
from typing import List, Dict, t.JsonValue

def batch_requests(requests: List[m.Dict]) -> List[r[t.JsonValue]]:
    """Execute multiple HTTP requests efficiently."""

    async def execute_batch():
        import asyncio

        async def execute_request(req_data: m.Dict) -> p.Result[t.JsonValue]:
            method = req_data.get("method", "GET")
            url = req_data["url"]
            **kwargs = req_data.get("kwargs", {})

            if method == "GET":
                return client.get(url, **kwargs)
            elif method == "POST":
                return client.post(url, **kwargs)
            # Add other methods as needed

        # Execute all requests concurrently
        tasks = [execute_request(req) for req in requests]
        return await asyncio.gather(*tasks)

    return asyncio.run(execute_batch())

# Usage
requests = [
    {"method": "GET", "url": "/users/1"},
    {"method": "GET", "url": "/users/2"},
    {"method": "POST", "url": "/users", "kwargs": {"json": {"name": "New User"}}}
]

results = batch_requests(requests)
```

## Security Best Practices

### Secure Communication

```python notest
# HTTPS only
client = FlextApiClient(
    base_url="https://api.example.com",
    verify_ssl=True,  # Verify SSL certificates
)

# Custom SSL context
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

client = FlextApiClient(
    base_url="https://api.example.com", verify_ssl=True, ssl_context=ssl_context
)
```

### Sensitive Data Handling

```python notest
# Avoid logging sensitive data
class SecureClient(FlextApiClient):
    def _prepare_request_data(self, data: dict) -> t.JsonMapping:
        """Remove sensitive fields before logging."""
        sensitive_fields = ["password", "token", "secret", "key"]

        if isinstance(data, dict):
            return {
                k: "***" if k.lower() in sensitive_fields else v
                for k, v in data.items()
            }
        return data
```

## Troubleshooting

### Common Issues

**1. Connection Timeouts**

```python notest
# Increase timeout for slow endpoints
result = client.get("/slow-endpoint", timeout=60.0)

# Check network connectivity
import socket

try:
    socket.create_connection(("api.example.com", 443), timeout=5)
    u.Cli.print("Network connection OK")
except OSError:
    u.Cli.print("Network connection failed")
```

**2. SSL Certificate Errors**

```python notest
# Disable SSL verification (NOT recommended for production)
client = FlextApiClient(base_url="https://api.example.com", verify_ssl=False)

# Or use custom SSL context for self-signed certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = FlextApiClient(base_url="https://api.example.com", ssl_context=ssl_context)
```

**3. Rate Limiting**

```python notest
# Handle rate limit responses
result = client.get("/api/data")

if result.failure and result.error.status_code == 429:
    retry_after = result.error.headers.get("Retry-After")
    if retry_after:
        wait_time = int(retry_after)
        u.Cli.print(f"Rate limited. Retry after {wait_time} seconds")
        time.sleep(wait_time)
```

This HTTP client guide provides comprehensive coverage of FLEXT-API's HTTP capabilities, from basic usage to advanced patterns and troubleshooting.
