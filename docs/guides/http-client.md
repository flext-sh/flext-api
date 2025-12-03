# HTTP Client Guide

Comprehensive guide for using the FLEXT-API HTTP client with railway patterns, error handling, and advanced features.

## HTTP Client Basics

### Creating HTTP Clients

```python
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

# Basic client
client = FlextApiClient(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"User-Agent": "FLEXT-API/0.9.9"}
)

# Client with authentication
auth_client = FlextApiClient(
    base_url="https://api.example.com",
    auth={"username": "user", "password": "pass"},
    headers={"Authorization": "Bearer token123"}
)

# Client with custom configuration
custom_client = FlextApiClient(
    base_url="https://api.example.com",
    timeout=60.0,
    max_retries=5,
    verify_ssl=True,
    proxies={"http": "http://proxy.company.com:8080"}
)
```

### HTTP Methods

All HTTP methods return `FlextResult[T]` for type-safe error handling.

```python
# GET request
result = client.get("/users")
if result.is_success:
    users = result.unwrap()
    print(f"Found {len(users)} users")

# GET with query parameters
result = client.get("/users", params={
    "limit": 10,
    "offset": 0,
    "status": "active"
})

# GET with custom headers
result = client.get("/users", headers={
    "Accept": "application/json",
    "X-API-Key": "your-api-key"
})

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

```python
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

class LoggingClient(FlextApiClient):
    """HTTP client with automatic request/response logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = FlextLogger(__name__)

    def _log_request(self, method: str, url: str, **kwargs):
        """Log outgoing request."""
        self.logger.info("HTTP Request", extra={
            "method": method,
            "url": url,
            "headers": kwargs.get("headers", {}),
            "params": kwargs.get("params", {}),
            "data_size": len(str(kwargs.get("json", kwargs.get("data", ""))))
        })

    def _log_response(self, response, duration_ms: float):
        """Log response details."""
        self.logger.info("HTTP Response", extra={
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "content_length": len(response.content) if response.content else 0
        })

    def get(self, url, **kwargs):
        self._log_request("GET", url, **kwargs)
        start_time = time.time()

        result = super().get(url, **kwargs)

        duration_ms = (time.time() - start_time) * 1000
        if result.is_success:
            self._log_response(result.unwrap(), duration_ms)

        return result
```

### Custom Headers and Authentication

```python
# Bearer token authentication
client = FlextApiClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer your-jwt-token"}
)

# API key authentication
client = FlextApiClient(
    base_url="https://api.example.com",
    headers={"X-API-Key": "your-api-key"}
)

# Basic authentication
client = FlextApiClient(
    base_url="https://api.example.com",
    auth=("username", "password")
)

# Custom authentication handler
class CustomAuth:
    def __init__(self, token: str):
        self.token = token

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request

custom_auth = CustomAuth("your-token")
client = FlextApiClient(
    base_url="https://api.example.com",
    auth=custom_auth
)
```

## Error Handling

### Railway Pattern Error Handling

FLEXT-API uses the railway pattern for type-safe error handling.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

def safe_api_call():
    """Example of safe API call with error handling."""
    result = client.get("/users/123")

    # Type-safe error handling
    if result.is_success:
        user = result.unwrap()
        return FlextResult[dict].ok(user)
    else:
        error = result.error
        # Handle different error types
        if error.code == "NOT_FOUND":
            return FlextResult[dict].fail("User not found")
        elif error.code == "UNAUTHORIZED":
            return FlextResult[dict].fail("Authentication required")
        else:
            return FlextResult[dict].fail(f"API error: {error.message}")

# Usage
result = safe_api_call()
if result.is_success:
    user = result.unwrap()
    print(f"User: {user['name']}")
else:
    print(f"Error: {result.error}")
```

### Error Types and Handling

```python
# HTTP error responses
try:
    result = client.get("/users/999")
    if result.is_failure:
        error = result.error

        # Handle specific HTTP errors
        if error.status_code == 404:
            print("Resource not found")
        elif error.status_code == 401:
            print("Authentication required")
        elif error.status_code == 403:
            print("Access forbidden")
        elif error.status_code == 429:
            print("Rate limit exceeded")
        elif error.status_code >= 500:
            print("Server error")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Request Configuration

### Query Parameters

```python
# Simple query parameters
result = client.get("/users", params={"active": True})

# Multiple values for same parameter
result = client.get("/users", params={"tags": ["REDACTED_LDAP_BIND_PASSWORD", "active"]})

# Complex query parameters
result = client.get("/search", params={
    "q": "python developer",
    "location": "San Francisco",
    "remote": True,
    "salary_min": 50000,
    "salary_max": 100000
})
```

### Request Body Data

```python
# JSON data (default)
user_data = {
    "name": "Alice",
    "email": "alice@example.com",
    "preferences": {"theme": "dark", "language": "en"}
}
result = client.post("/users", json=user_data)

# Form data
form_data = {
    "name": "Alice",
    "email": "alice@example.com",
    "file": open("resume.pdf", "rb")
}
result = client.post("/users", data=form_data)

# Raw data
xml_data = "<user><name>Alice</name></user>"
result = client.post("/users", data=xml_data, headers={
    "Content-Type": "application/xml"
})
```

### Custom Headers

```python
# Per-request headers
result = client.get("/api/data", headers={
    "Accept": "application/json",
    "X-Client-Version": "1.0.0",
    "X-Request-ID": str(uuid.uuid4())
})

# Conditional headers
result = client.get("/api/data", headers={
    "If-Modified-Since": "Wed, 21 Oct 2025 07:28:00 GMT",
    "If-None-Match": '"abc123"'
})

# Custom content types
result = client.post("/api/upload", data=binary_data, headers={
    "Content-Type": "application/octet-stream"
})
```

## Response Handling

### Response Processing

```python
# Get response object
result = client.get("/users/123")
if result.is_success:
    response = result.unwrap()

    # Access response data
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Content: {response.text}")

    # Parse JSON response
    user_data = response.json()
    print(f"User: {user_data['name']}")

    # Access raw response content
    raw_content = response.content
    print(f"Raw content length: {len(raw_content)}")
```

### Response Metadata

```python
# Response timing
result = client.get("/slow-endpoint")
if result.is_success:
    response = result.unwrap()
    print(f"Request took: {response.elapsed.total_seconds()}s")

# Response headers
result = client.get("/api/data")
if result.is_success:
    response = result.unwrap()
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Cache-Control: {response.headers.get('Cache-Control')}")
    print(f"ETag: {response.headers.get('ETag')}")
```

## Advanced Usage Patterns

### Batch Operations

```python
from typing import List

async def batch_create_users(users: List[dict]) -> List[FlextResult[dict]]:
    """Create multiple users in parallel."""
    import asyncio

    async def create_user(user_data: dict) -> FlextResult[dict]:
        return client.post("/users", json=user_data)

    # Execute requests concurrently
    tasks = [create_user(user) for user in users]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results

# Usage
users = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"}
]

results = await batch_create_users(users)

for i, result in enumerate(results):
    if result.is_success:
        print(f"✅ Created user {i+1}")
    else:
        print(f"❌ Failed to create user {i+1}: {result.error}")
```

### Pagination

```python
def get_all_users(page_size: int = 50) -> List[dict]:
    """Get all users with pagination."""
    all_users = []
    page = 1

    while True:
        result = client.get("/users", params={
            "page": page,
            "per_page": page_size
        })

        if result.is_failure:
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
print(f"Total users: {len(users)}")
```

### Retry Logic

```python
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
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

            if result.is_success:
                return result

            # Check if error is retryable
            if not self._is_retryable_error(result.error):
                return result

            if attempt < self.max_retries:
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

        return result

    def _is_retryable_error(self, error) -> bool:
        """Check if error is worth retrying."""
        retryable_codes = [408, 429, 500, 502, 503, 504]
        return error.status_code in retryable_codes

# Usage
retry_client = RetryClient(
    base_url="https://unreliable-api.com",
    max_retries=3,
    retry_delay=1.0
)

result = retry_client.get("/data")
```

## Testing HTTP Clients

### Test Client Setup

```python
import pytest
from flext_api import FlextApiClient
from flext_api.testing import FlextApiTestClient

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

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 200

        users = response.json()
        assert isinstance(users, list)

    def test_create_user(self):
        """Test POST /users endpoint."""
        user_data = {"name": "Test User", "email": "test@example.com"}
        result = self.client.post("/users", json=user_data)

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 201

        user = response.json()
        assert user["name"] == "Test User"
        assert "id" in user

    def test_error_handling(self):
        """Test error response handling."""
        result = self.client.get("/users/99999")

        assert result.is_failure
        error = result.error
        assert error.status_code == 404
        assert "not found" in error.message.lower()
```

### Mocking External APIs

```python
from unittest.mock import Mock, patch
import pytest

@patch('flext_api.client.httpx.Client')
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

    assert result.is_success
    user = result.unwrap()
    assert user["name"] == "Test User"
```

## Performance Optimization

### Connection Pooling

```python
# Configure connection pooling for better performance
client = FlextApiClient(
    base_url="https://api.example.com",
    transport=httpx.HTTPTransport(
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
)
```

### Request Batching

```python
from typing import List, Dict, object

def batch_requests(requests: List[t.Dict]) -> List[FlextResult[object]]:
    """Execute multiple HTTP requests efficiently."""

    async def execute_batch():
        import asyncio

        async def execute_request(req_data: t.Dict) -> FlextResult[object]:
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

```python
# HTTPS only
client = FlextApiClient(
    base_url="https://api.example.com",
    verify_ssl=True  # Verify SSL certificates
)

# Custom SSL context
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

client = FlextApiClient(
    base_url="https://api.example.com",
    verify_ssl=True,
    ssl_context=ssl_context
)
```

### Sensitive Data Handling

```python
# Avoid logging sensitive data
class SecureClient(FlextApiClient):
    def _prepare_request_data(self, data: dict) -> dict[str, object]:
        """Remove sensitive fields before logging."""
        sensitive_fields = ["password", "token", "secret", "key"]

        if isinstance(data, dict):
            return {k: "***" if k.lower() in sensitive_fields else v
                   for k, v in data.items()}
        return data
```

## Troubleshooting

### Common Issues

**1. Connection Timeouts**

```python
# Increase timeout for slow endpoints
result = client.get("/slow-endpoint", timeout=60.0)

# Check network connectivity
import socket
try:
    socket.create_connection(("api.example.com", 443), timeout=5)
    print("Network connection OK")
except OSError:
    print("Network connection failed")
```

**2. SSL Certificate Errors**

```python
# Disable SSL verification (NOT recommended for production)
client = FlextApiClient(
    base_url="https://api.example.com",
    verify_ssl=False
)

# Or use custom SSL context for self-signed certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = FlextApiClient(
    base_url="https://api.example.com",
    ssl_context=ssl_context
)
```

**3. Rate Limiting**

```python
# Handle rate limit responses
result = client.get("/api/data")

if result.is_failure and result.error.status_code == 429:
    retry_after = result.error.headers.get("Retry-After")
    if retry_after:
        wait_time = int(retry_after)
        print(f"Rate limited. Retry after {wait_time} seconds")
        time.sleep(wait_time)
```

This HTTP client guide provides comprehensive coverage of FLEXT-API's HTTP capabilities, from basic usage to advanced patterns and troubleshooting.
