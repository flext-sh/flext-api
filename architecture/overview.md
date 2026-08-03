# Architecture Overview

Comprehensive architecture guide for FLEXT-API — the HTTP foundation for the
FLEXT enterprise data integration platform.

## Overview

FLEXT-API follows a **layered Clean Architecture** built on top of
`flext-core`. The public surface is exposed through a single facade,
`FlextApi`, and typed settings, models, and protocols.

```text
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│   FlextApi facade, FlextApiClient, and protocol plugins    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│   m.Api.HttpRequest, m.Api.HttpResponse, validation           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Foundation Layer                          │
│   flext-core: c, t, p, m, u, r, s                            │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**

- **Single Facade**: `FlextApi` is the public entry point for all HTTP verbs
- **Railway Pattern**: Every operation returns `p.Result[T]`
- **Settings SSOT**: `FlextApiSettings` owns all HTTP configuration
- **Pydantic v2 Models**: `m.Api.HttpRequest` and `m.Api.HttpResponse` are immutable value models
- **Protocol Plugin Foundation**: `FlextApiProtocolPluginManager` provides a lifecycle contract for future protocols

## Layer Details

### Foundation Layer (Core Primitives)

- `FlextApiClient` — low-level HTTP client; executes `m.Api.HttpRequest`
- `FlextApiSettings` — configuration management for API settings
- `m.Api` — HTTP-specific models and validation
- `u.Api.RequestUtils` — helpers for request normalization

### Domain Layer (HTTP Business Logic)

- **HTTP Models**: Request/response models with validation
- **Protocol Abstractions**: `p.Api` interfaces for HTTP clients and plugins
- **Validation Logic**: Pydantic v2 validation for HTTP operations
- **Error Handling**: `p.Result` and `r` for railway-oriented error handling

### Application Layer (Protocol Implementations)

- **HTTP Protocol**: The only public protocol implemented today
- **Protocol Plugin Manager**: Base for registering future protocol plugins
- **FlextApi**: Public facade exposing `get`, `post`, `put`, `patch`, `delete`, and `request`

## Protocol Plugin System

The protocol plugin system is a foundation for future protocol support. It is
managed by `FlextApiProtocolPluginManager` and typed through
`FlextApiProtocolPluginTypes`.

```python
from __future__ import annotations

from flext_api import FlextApiProtocolPluginManager, FlextApiProtocolPluginTypes, p, r


class HttpPlugin(FlextApiProtocolPluginTypes.Plugin):
    name = "http"
    version = "1.0.0"
    capabilities = {"http_client"}

    def initialize(self) -> p.Result[bool]:
        return r[bool].ok(True)

    def shutdown(self) -> p.Result[bool]:
        return r[bool].ok(True)


manager = FlextApiProtocolPluginManager.Manager()
load_result = manager.load_plugin(HttpPlugin(name="http", version="1.0.0"))
assert load_result.success
assert "http" in manager.list_loaded_plugins()
assert manager.unload_plugin("http").success
```

## HTTP Client Architecture

### FlextApiClient Design

`FlextApiClient` is bound to `FlextApiSettings` and executes validated
`m.Api.HttpRequest` instances through `request(...)`. It does not expose HTTP
verbs directly; those live on `FlextApi`.

```python
from __future__ import annotations

from flext_api import FlextApiClient, FlextApiSettings, c, m, p

settings = FlextApiSettings(base_url="https://api.example.com", timeout=30.0)
client = FlextApiClient(settings=settings)

assert client.base_url == "https://api.example.com"
assert client.timeout == 30.0

request = m.Api.HttpRequest(
    method=c.Api.Method.GET, url="/users", headers={"Accept": "application/json"}
)
result: p.Result[m.Api.HttpResponse] = client.request(request)
if result.success:
    print(result.unwrap().status_code)
else:
    print(result.error)
```

### Request Processing Pipeline

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, c, m, p, r, u


class TracingApi(FlextApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        self.logger.info("request", method="GET", url=url)
        return super().get(url, headers=headers, request_kwargs=request_kwargs)


class FakeApi(TracingApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"endpoint": url},
                headers={"Content-Type": "application/json"},
            )
        )


api = FakeApi(settings=FlextApiSettings(base_url="https://example.com"))
result = api.get("/users")
assert result.success
assert result.unwrap().body["endpoint"] == "/users"
```

## FastAPI Integration Architecture

A FastAPI application factory is **not** currently part of the public API. You can
use `FlextApi` and `FlextApiClient` inside your own FastAPI/Starlette routes
when needed.

## Storage Architecture

Storage, cache, and file abstractions are **not** currently part of the public
API. File-like payloads travel through `m.Api.HttpRequest.body` and
`m.Api.HttpResponse.body`.

## Caching Architecture

Caching is **not** currently part of the public API. Applications can implement
their own caching layer on top of the `FlextApi` facade.

## Security Architecture

Authentication and authorization middleware are **not** currently part of the
public API. Security headers and tokens can be passed through
`FlextApiSettings.default_headers` or per-request `headers`.

## Performance Architecture

Performance monitoring is **not** currently part of the public API. You can add
logging and timing by subclassing `FlextApi`.

## Deployment Architecture

Container and Kubernetes deployment examples are **not** currently part of the
public API. FLEXT-API is a library, not a deployable service.

## Quality Metrics

| Layer                  | Status       | Notes                                    |
| ---------------------- | ------------ | ---------------------------------------- |
| Foundation             | Complete     | HTTP client, settings, and models public |
| Domain Models          | Complete     | Pydantic v2 request/response models      |
| HTTP Facade            | Complete     | `FlextApi` with all verbs                |
| Protocol Plugins       | Foundation   | Plugin manager ready; only HTTP today    |
| Middleware / Storage   | Not Public   | Not exposed in the current API           |
| FastAPI Integration    | Not Public   | No `create_fastapi_app` helper           |

## Extension Points

### Adding New Protocols

Extend the protocol plugin system by subclassing
`FlextApiProtocolPluginTypes.Plugin` and registering it with
`FlextApiProtocolPluginManager.Manager`.

### Custom Middleware

There is no middleware pipeline yet. Use subclassing of `FlextApi` to add
cross-cutting behavior.

## Performance Considerations

- HTTP transport uses `httpx` under the hood
- Settings and client are created lazily by the facade
- Railway results avoid exception creation for expected failures

## Migration Guidelines

### Version Compatibility

FLEXT-API follows semantic versioning. Public facades (`FlextApi`,
`FlextApiClient`, `FlextApiSettings`, `m.Api`, `p.Api`, `u.Api`) are the stable
surface. Internal modules prefixed with `_` may change without notice.

## References

- `docs/guides/http-client.md`
- `api/core.md`
- `architecture/decisions/003-protocol-abstraction.md`
