# 002. Railway-Oriented Error Handling

<!-- TOC START -->
- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
- [Alternatives Considered](#alternatives-considered)
  - [Option 1: Traditional Exceptions](#option-1-traditional-exceptions)
  - [Option 2: Result Pattern (Custom Implementation)](#option-2-result-pattern-custom-implementation)
  - [Option 3: Hybrid Approach](#option-3-hybrid-approach)
- [Implementation Examples](#implementation-examples)
  - [Basic HTTP Operation](#basic-http-operation)
  - [Usage in Application Code](#usage-in-application-code)
  - [Testing Railway Code](#testing-railway-code)
- [Migration Strategy](#migration-strategy)
- [Best Practices](#best-practices)
  - [Railway Pattern Guidelines](#railway-pattern-guidelines)
  - [Error Message Standards](#error-message-standards)
- [References](#references)
<!-- TOC END -->

Date: 2025-01-01

## Status

Accepted

## Context

HTTP operations are inherently unreliable: network failures, server errors, timeouts, and malformed responses are common. Traditional exception-based error handling makes code complex and error-prone. The FLEXT ecosystem needed a consistent approach to error handling that makes errors explicit, composable, and testable.

## Decision

FLEXT-API uses **Railway-Oriented Programming** with `r[T]` for all HTTP operations. Every public method returns `p.Result[T]`. Operations are composed using `flat_map`, `map`, and `map_error` methods.

## Consequences

### Positive

- **Explicit Error Handling**: Errors are visible in type signatures and cannot be ignored
- **Composable Operations**: HTTP operations can be chained without nested try/catch blocks
- **Testable Code**: Railway pattern makes testing success and failure paths straightforward
- **Type Safety**: Type signatures catch unhandled error cases

### Negative

- **Learning Curve**: Developers must learn railway pattern concepts
- **Verbose Code**: Some operations require more lines than exception-based code

## Alternatives Considered

### Option 1: Traditional Exceptions

```python
from __future__ import annotations

import httpx


def get_user(user_id: int) -> dict:
    """Traditional exception-based example (not used in FLEXT-API)."""
    response = httpx.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()```
### Option 2: Result Pattern (Custom Implementation)

```python
from __future__ import annotations


class Result:
    """Minimal custom result type (not used in FLEXT-API)."""

    def __init__(self, success: bool, value=None, error=None):
        self.success = success
        self.value = value
        self.error = error```
### Option 3: Hybrid Approach

- **Description**: Use railway pattern internally but expose traditional APIs
- **Rejected**: Would undermine the architectural benefits

## Implementation Examples

### Basic HTTP Operation

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class UserApi(FlextApi):
    def fetch_user(self, user_id: int) -> p.Result[m.Api.HttpResponse]:
        return (
            self
            .get(f"/users/{user_id}")
            .flat_map(self._validate_ok)
            .map_error(lambda err: f"User fetch failed: {err}")
        )

    def _validate_ok(
        self, response: m.Api.HttpResponse
    ) -> p.Result[m.Api.HttpResponse]:
        if response.success:
            return r[m.Api.HttpResponse].ok(response)
        return r[m.Api.HttpResponse].fail(
            f"HTTP {response.status_code}: request failed"
        )


class FakeUserApi(UserApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        if url.endswith("/users/123"):
            return r[m.Api.HttpResponse].ok(
                m.Api.create_response(
                    status_code=200,
                    body={"id": 123, "name": "Alice"},
                    headers={"Content-Type": "application/json"},
                )
            )
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(status_code=404, body={"error": "not found"})
        )


api = FakeUserApi(settings=FlextApiSettings(base_url="https://example.com"))
result = api.fetch_user(123)
assert result.success
assert result.unwrap().body["name"] == "Alice"```
### Usage in Application Code

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class FakeProfileApi(FlextApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"user_id": 123, "bio": "FLEXT enthusiast"},
                headers={"Content-Type": "application/json"},
            )
        )


api = FakeProfileApi(settings=FlextApiSettings(base_url="https://example.com"))
result = api.get("/users/123/profile")

if result.success:
    profile = result.unwrap().body
    print(f"Found profile: {profile['bio']}")
else:
    print(f"Error: {result.error}")```
### Testing Railway Code

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class FakeUserApi(FlextApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        if url.endswith("/users/123"):
            return r[m.Api.HttpResponse].ok(
                m.Api.create_response(
                    status_code=200,
                    body={"id": 123, "name": "John"},
                    headers={"Content-Type": "application/json"},
                )
            )
        return r[m.Api.HttpResponse].fail("HTTP 404")


def test_get_user_success():
    api = FakeUserApi(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/users/123")
    assert result.success
    assert result.unwrap().body["name"] == "John"


def test_get_user_not_found():
    api = FakeUserApi(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/users/999")
    assert result.failure
    assert "404" in result.error


test_get_user_success()
test_get_user_not_found()```
## Migration Strategy

- [x] Implement `r` integration in all HTTP operations
- [x] Update `FlextApi` and `FlextApiClient` to return `p.Result[T]`
- [ ] Update all remaining markdown examples to use real APIs

## Best Practices

### Railway Pattern Guidelines

1. Always return `p.Result[T]` from public HTTP methods
2. Use descriptive errors
3. Chain operations with `flat_map` and `map`
4. Test both success and failure paths

### Error Message Standards

```python
from __future__ import annotations

from flext_api import r

r[str].fail("Invalid user ID: must be a positive integer")
r[str].fail("HTTP request timeout after 30 seconds")
r[str].fail("JSON parsing failed: invalid response format")```
## References

- [Railway-Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- GitHub Issue: #156 - Railway Pattern Implementation
