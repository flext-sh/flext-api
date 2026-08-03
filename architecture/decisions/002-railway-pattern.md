# 002. Railway-Oriented Error Handling

<!-- TOC START -->
- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
  - [Risks](#risks)
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
  - [Performance Considerations](#performance-considerations)
- [References](#references)
<!-- TOC END -->

Date: 2025-01-01

## Status

Accepted

## Context

HTTP operations are inherently unreliable: network failures, server errors, timeouts, and malformed responses are common. Traditional exception-based error handling makes code complex and error-prone. The FLEXT ecosystem needed a consistent approach to error handling that:

1. Makes error handling explicit and visible in the type system
2. Enables composable operations that can be chained together
3. Prevents silent failures and unhandled errors
4. Provides clear separation between success and failure paths
5. Integrates well with async/await patterns

## Decision

FLEXT-API uses **Railway-Oriented Programming** with `r[T]` for all HTTP operations. Every public method returns `p.Result[T]`. Operations are composed using `flat_map`, `map`, and `map_error` methods.

## Consequences

### Positive

- **Explicit Error Handling**: Errors are visible in type signatures and cannot be ignored
- **Composable Operations**: HTTP operations can be chained without nested try/catch blocks
- **Testable Code**: Railway pattern makes testing success and failure paths straightforward
- **Type Safety**: Type signatures catch unhandled error cases
- **Clear Intent**: Code reads like a recipe of operations that can succeed or fail

### Negative

- **Learning Curve**: Developers must learn railway pattern concepts
- **Verbose Code**: Some operations require more lines than exception-based code
- **Type Complexity**: Generic types can be harder to understand initially

### Risks

- **Adoption Resistance**: Teams accustomed to exceptions may resist the change
- **Type System Complexity**: Advanced generic patterns may confuse some developers

## Alternatives Considered

### Option 1: Traditional Exceptions

```python
from __future__ import annotations

import httpx


def get_user(user_id: int) -> dict:
    """Traditional exception-based example (not used in FLEXT-API)."""
    response = httpx.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()
```

- **Pros**: Familiar, concise for success paths
- **Cons**: Silent failures, complex error handling, hard to test
- **Rejected**: Not suitable for enterprise HTTP operations

### Option 2: Result Pattern (Custom Implementation)

```python
from __future__ import annotations


class Result:
    """Minimal custom result type (not used in FLEXT-API)."""

    def __init__(self, success: bool, value=None, error=None):
        self.success = success
        self.value = value
        self.error = error
```

- **Pros**: Simple implementation, explicit error handling
- **Cons**: No composability, reinventing the wheel, less type-safe
- **Rejected**: `r` from flext-core is more robust and feature-complete

### Option 3: Hybrid Approach

- **Description**: Use railway pattern internally but expose traditional APIs
- **Pros**: Gradual adoption, familiar external APIs
- **Cons**: Inconsistent error handling, defeats the purpose
- **Rejected**: Would undermine the architectural benefits

## Implementation Examples

### Basic HTTP Operation

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class UserApi(FlextApi):
    """Example facade that fetches a user and validates the response."""

    def fetch_user(self, user_id: int) -> p.Result[m.Api.HttpResponse]:
        """Get user with railway error handling."""
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


# In-memory implementation so the example runs without network access.
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
assert result.unwrap().body["name"] == "Alice"

not_found = api.fetch_user(999)
assert not_found.failure
assert "404" in not_found.error
```

### Usage in Application Code

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class ProfileApi(FlextApi):
    def fetch_profile(self, user_id: int) -> p.Result[m.Api.HttpResponse]:
        return self.get(f"/users/{user_id}/profile")


class FakeProfileApi(ProfileApi):
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
result = api.fetch_profile(123)

if result.success:
    profile = result.unwrap().body
    print(f"Found profile: {profile['bio']}")
else:
    print(f"Error: {result.error}")
```

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
test_get_user_not_found()
```

## Migration Strategy

- [x] Implement `r` integration in all HTTP operations
- [x] Update `FlextApi` and `FlextApiClient` to return `p.Result[T]`
- [ ] Update all remaining markdown examples to use real APIs
- [ ] Establish coding standards for railway pattern usage

## Best Practices

### Railway Pattern Guidelines

1. **Always Return `p.Result`**: Every public HTTP method should return `p.Result[T]`
2. **Use Descriptive Errors**: Error messages should be user-friendly and actionable
3. **Chain Operations**: Use `flat_map` for sequential operations, `map` for transformations
4. **Handle Errors Early**: Validate inputs and fail fast with clear error messages
5. **Test Both Paths**: Always test both success and failure code paths

### Error Message Standards

```python
from __future__ import annotations

from flext_api import r

# Good error messages
r[str].fail("Invalid user ID: must be a positive integer")
r[str].fail("HTTP request timeout after 30 seconds")
r[str].fail("JSON parsing failed: invalid response format")

# Avoid generic messages
r[str].fail("Error")  # Too vague
r[str].fail("Something went wrong")  # Not helpful
```

### Performance Considerations

- **Short-Circuiting**: Failed operations do not execute subsequent operations
- **Memory Efficiency**: No exception object creation for expected errors
- **Composable**: Enables efficient pipelining of operations

## References

- [Railway-Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- GitHub Issue: #156 - Railway Pattern Implementation
