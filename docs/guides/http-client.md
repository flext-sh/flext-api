# HTTP Client Guide

FLEXT-API exposes two HTTP entry points:

- `FlextApi` is the public facade for convenience methods such as `get`, `post`, `put`, `patch`, and `delete`.
- `FlextApiClient` is the lower-level client. It accepts only `settings=` at construction time and executes a validated `m.Api.HttpRequest` through `request(...)`.

## Facade Usage

```python
from flext_api import FlextApi, FlextApiSettings

settings = FlextApiSettings(base_url="https://api.example.com")
api = FlextApi(settings=settings)

result = api.get(
    "/users",
    headers={"Accept": "application/json"},
    request_kwargs={"params": {"limit": 10, "active": True}},
)

if result.success:
    response = result.value
    print(response.status_code)
else:
    print(result.error or "request failed")
```

## Client Usage

```python
from flext_api import FlextApiClient, FlextApiSettings, c, m

settings = FlextApiSettings(base_url="https://api.example.com")
client = FlextApiClient(settings=settings)

request = m.Api.HttpRequest.model_validate({
    "method": c.Api.Method.GET,
    "url": "/users",
    "headers": {"Accept": "application/json"},
    "query_params": {"limit": "10"},
    "timeout": settings.timeout,
})

result = client.request(request)
```

## Request Body

Use the facade for typical application code:

```python
from flext_api import FlextApi

api = FlextApi()
result = api.post(
    "/users",
    data={"name": "Alice", "email": "alice@example.com"},
    headers={"Content-Type": "application/json"},
)
```

Use `request_kwargs` for query parameters and request options that belong to `m.Api.HttpRequest` normalization.

## Error Handling

Every call returns `p.Result[m.Api.HttpResponse]`.

```python
from flext_api import FlextApi

result = FlextApi().get("/health")
if result.failure:
    raise RuntimeError(result.error or "HTTP request failed")

response = result.value
```

The result contract is the canonical FLEXT railway contract: inspect `success` or `failure`, then use `value`, `error`, `unwrap()`, or higher-order methods such as `map` and `flat_map`.
