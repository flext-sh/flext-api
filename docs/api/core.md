# Core API Reference

<!-- TOC START -->
- [Core HTTP Client](#core-http-client)
  - [FlextApiClient - Main HTTP Client](#flextapiclient-main-http-client)
  - [FlextApi - Unified Facade](#flextapi-unified-facade)
  - [HTTP Methods](#http-methods)
- [Configuration](#configuration)
  - [FlextApiSettings - Configuration Model](#flextapisettings-configuration-model)
- [HTTP Models](#http-models)
  - [Request/Response Models](#requestresponse-models)
- [HTTP Utilities](#http-utilities)
  - [RequestUtils - Helper Functions](#requestutils-helper-functions)
- [Usage Examples](#usage-examples)
  - [Complete HTTP Client Example](#complete-http-client-example)
<!-- TOC END -->

This section covers the core HTTP client and configuration types that form the
public surface of `flext-api`.

## Core HTTP Client

### FlextApiClient - Main HTTP Client

`FlextApiClient` is the low-level HTTP client. It is bound to typed settings and
executes validated `m.Api.HttpRequest` instances through `request(...)`. It does
not expose `get/post/put/delete/patch` directly; those methods live on the
`FlextApi` facade.

```python
from __future__ import annotations

from flext_api import FlextApiClient, FlextApiSettings, c, m, p

# Settings are the only constructor argument.
settings = FlextApiSettings(
    base_url="https://api.example.com",
    timeout=30.0,
    max_retries=3,
    default_headers={"User-Agent": "flext-api"},
)

client = FlextApiClient(settings=settings)

# The client exposes configured values as properties.
print(client.base_url)  # https://api.example.com
print(client.timeout)  # 30.0

# Build and execute a validated request model.
request = m.Api.HttpRequest(
    method=c.Api.Method.GET,
    url="/users",
    headers={"Accept": "application/json"},
    query_params={"limit": "10"},
)
result: p.Result[m.Api.HttpResponse] = client.request(request)

if result.success:
    response = result.unwrap()
    print(response.status_code)
    print(response.body)
else:
    print(f"Transport error: {result.error}")```
**Key Features:**

- Type-safe HTTP operations via Pydantic models
- Monadic error handling through `p.Result`
- Settings-driven configuration (env vars, `FLEXT_API_*` prefix)
- Request validation before any network call

**Configuration Options:**

- `base_url`: Base URL for relative requests
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum retry attempts
- `verify_ssl`: Enable TLS certificate verification
- `default_headers`: Headers applied to all requests

### FlextApi - Unified Facade

`FlextApi` is the public entry point. It creates and owns a `FlextApiClient`
lazily and exposes convenience methods for each HTTP verb.

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p

api = FlextApi(settings=FlextApiSettings(base_url="https://api.example.com"))

result: p.Result[m.Api.HttpResponse] = api.get(
    "/users",
    headers={"Accept": "application/json"},
    request_kwargs={"params": {"limit": 10}},
)

if result.success:
    response = result.unwrap()
    print(f"Status: {response.status_code}")
    print(f"Body: {response.body}")
else:
    print(f"Error: {result.error}")```
### HTTP Methods

All methods return `p.Result[m.Api.HttpResponse]`.

**GET Requests:**

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p

api = FlextApi(settings=FlextApiSettings(base_url="https://api.example.com"))

result: p.Result[m.Api.HttpResponse] = api.get("/users")

result = api.get("/users", request_kwargs={"params": {"limit": 10, "offset": 0}})

result = api.get("/users", headers={"Accept": "application/json"})```
**POST/PUT/PATCH/DELETE Requests:**

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p

api = FlextApi(settings=FlextApiSettings(base_url="https://api.example.com"))

post_result: p.Result[m.Api.HttpResponse] = api.post(
    "/users", data={"name": "Alice", "email": "alice@example.com"}
)

put_result = api.put("/users/123", data={"name": "Updated Name"})

patch_result = api.patch("/users/123", data={"email": "new@example.com"})

delete_result = api.delete("/users/123")```
## Configuration

### FlextApiSettings - Configuration Model

`FlextApiSettings` is a Pydantic settings model. Project-specific fields are
nested under the `Api` namespace, but flat constructor arguments are automatically
lifted into that namespace for convenience.

```python
from __future__ import annotations

from flext_api import FlextApiSettings

# Flat constructor (preferred)
settings = FlextApiSettings(
    base_url="https://api.example.com",
    timeout=30.0,
    max_retries=3,
    verify_ssl=True,
    default_headers={"User-Agent": "flext-api"},
)

# Equivalent nested constructor
settings_nested = FlextApiSettings(
    Api={"base_url": "https://api.example.com", "timeout": 30.0, "max_retries": 3}
)

# Access the resolved namespace values.
print(settings.Api.base_url)
print(settings.Api.timeout)```
To extend settings with custom fields, subclass `FlextApiSettings` and add fields
outside the `Api` namespace or declare an additional nested group.

```python
from __future__ import annotations

from flext_api import FlextApiSettings
from pydantic import Field


class MyApiConfig(FlextApiSettings):
    """Custom API configuration with an extra scalar flag."""

    custom_setting: str = Field(default="default_value")


config = MyApiConfig(base_url="https://api.example.com", custom_setting="custom")
assert config.custom_setting == "custom"
assert config.Api.base_url == "https://api.example.com"```
## HTTP Models

### Request/Response Models

HTTP payloads are represented by immutable Pydantic value models under
`m.Api`.

```python
from __future__ import annotations

from flext_api import c, m

request = m.Api.HttpRequest(
    method=c.Api.Method.POST,
    url="https://api.example.com/users",
    headers={"Content-Type": "application/json"},
    body={"name": "Alice", "email": "alice@example.com"},
)

json_data = request.model_dump_json(exclude={"content_type"})
deserialized = m.Api.HttpRequest.model_validate_json(json_data)
assert deserialized.method == "POST"

response = m.Api.create_response(
    status_code=201,
    headers={"Content-Type": "application/json"},
    body={"id": 1, "name": "Alice"},
)
assert response.success
assert response.status_code == 201```
## HTTP Utilities

### RequestUtils - Helper Functions

`u.Api.RequestUtils` provides small, pure helpers for normalizing request
components before they are validated into `m.Api.HttpRequest`.

```python
from __future__ import annotations

from flext_api import c, u

# Build a normalized request payload from raw call-site arguments.
payload_result = u.Api.RequestUtils.build_request_payload(
    method=c.Api.Method.GET,
    url="/users",
    headers={"Accept": "application/json"},
    request_kwargs={"params": {"limit": 10}},
)
assert payload_result.success
payload = payload_result.unwrap()
print(payload.root)

# Merge headers.
merged_result = u.Api.RequestUtils.merge_headers(
    {"Content-Type": "application/json"},
    {"headers": {"Authorization": "Bearer token123"}},
)
assert merged_result.success
print(merged_result.unwrap())

# Coerce and validate timeouts.
timeout_result = u.Api.RequestUtils.coerce_positive_timeout(5.0)
assert timeout_result.success
print(timeout_result.unwrap())```
## Usage Examples

### Complete HTTP Client Example

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class UserApiClient:
    """Thin wrapper over the FlextApi facade for a user-management API."""

    def __init__(self, base_url: str = "https://api.example.com"):
        self.api = FlextApi(settings=FlextApiSettings(base_url=base_url, timeout=10.0))

    def list_users(self, limit: int = 10) -> p.Result[m.Api.HttpResponse]:
        return self.api.get("/users", request_kwargs={"params": {"_limit": limit}})

    def get_user(self, user_id: int) -> p.Result[m.Api.HttpResponse]:
        return self.api.get(f"/users/{user_id}")

    def create_user(self, user_data: dict) -> p.Result[m.Api.HttpResponse]:
        return self.api.post("/users", data=user_data)

    def update_user(
        self, user_id: int, user_data: dict
    ) -> p.Result[m.Api.HttpResponse]:
        return self.api.put(f"/users/{user_id}", data=user_data)

    def delete_user(self, user_id: int) -> p.Result[m.Api.HttpResponse]:
        return self.api.delete(f"/users/{user_id}")


# Usage example against a fake facade so the example runs without network access.
class FakeUserApi(UserApiClient):
    def __init__(self):
        super().__init__(base_url="https://example.com")

    def list_users(self, limit: int = 10) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body=[{"id": i, "name": f"User {i}"} for i in range(limit)],
                headers={"Content-Type": "application/json"},
            )
        )

    def get_user(self, user_id: int) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"id": user_id, "name": "User Name"},
                headers={"Content-Type": "application/json"},
            )
        )

    def create_user(self, user_data: dict) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=201,
                body={"id": 1, **user_data},
                headers={"Content-Type": "application/json"},
            )
        )

    def update_user(
        self, user_id: int, user_data: dict
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"id": user_id, **user_data},
                headers={"Content-Type": "application/json"},
            )
        )

    def delete_user(self, user_id: int) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=204, body={}, headers={"Content-Type": "application/json"}
            )
        )


client = FakeUserApi()
users_result = client.list_users(limit=5)
if users_result.success:
    users = users_result.unwrap().body
    print(f"Retrieved {len(users)} users")

create_result = client.create_user({"name": "John Doe", "email": "john@example.com"})
if create_result.success:
    user = create_result.unwrap().body
    print(f"Created user: {user['name']}")

update_result = client.update_user(1, {"name": "Jane Doe"})
if update_result.success:
    print(f"Updated user: {update_result.unwrap().body['name']}")

delete_result = client.delete_user(1)
if delete_result.success:
    print(f"Deleted user, status: {delete_result.unwrap().status_code}")```
This core API provides the public HTTP surface for `flext-api`: typed settings, a
validated request model, a monadic response model, and the `FlextApi` facade for
convenient HTTP verbs.
