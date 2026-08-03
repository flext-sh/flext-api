# 003. Protocol Plugin Architecture

<!-- TOC START -->
- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
- [Implementation Architecture](#implementation-architecture)
  - [Protocol Plugin Manager](#protocol-plugin-manager)
  - [HTTP Protocol](#http-protocol)
- [Usage Examples](#usage-examples)
  - [HTTP Usage](#http-usage)
- [Testing Strategy](#testing-strategy)
- [References](#references)
<!-- TOC END -->

Date: 2025-01-01

## Status

Accepted

## Context

Enterprise applications consume diverse APIs, but `flext-api` currently focuses on
HTTP/REST. The architecture needs to keep the HTTP surface clean while leaving
room for future protocol support through a plugin-style boundary.

## Decision

`flext-api` exposes a single HTTP-focused facade (`FlextApi`) and a typed
protocol layer (`p.Api`) for HTTP operations. Protocol plugins are managed by
the exported `FlextApiProtocolPluginManager` and `FlextApiProtocolPluginTypes`
shards, which provide a railway result-oriented lifecycle contract.

## Consequences

### Positive

- **Extensibility**: New protocols can be added later without changing `FlextApi`
- **Consistency**: Unified error handling and `p.Result` typing across boundaries
- **Testability**: Protocol plugins and HTTP clients can be tested independently

### Negative

- **Scope**: Only HTTP is implemented today; other protocols are not available
- **Abstraction Cost**: Plugin lifecycle adds a small amount of boilerplate

## Implementation Architecture

### Protocol Plugin Manager

The public plugin manager is exported from `flext_api` and can be used as a
base for future protocol discovery:

```python
from __future__ import annotations

from flext_api import FlextApiProtocolPluginManager, FlextApiProtocolPluginTypes, p, r


class JsonSchemaPlugin(FlextApiProtocolPluginTypes.Plugin):
    """Example plugin implementing the plugin lifecycle contract."""

    name = "json-schema"
    version = "1.0.0"
    capabilities = {"schema_validation", "serialization"}

    def initialize(self) -> p.Result[bool]:
        print(f"{self.name} initialized")
        return r[bool].ok(True)

    def shutdown(self) -> p.Result[bool]:
        print(f"{self.name} shutdown")
        return r[bool].ok(True)


manager = FlextApiProtocolPluginManager.Manager()
load_result = manager.load_plugin(JsonSchemaPlugin(name="json-schema", version="1.0.0"))
assert load_result.success

plugins = manager.list_loaded_plugins()
assert "json-schema" in plugins

resolve_result = manager.resolve_plugin("json-schema")
assert resolve_result.success
assert resolve_result.unwrap().version == "1.0.0"

unload_result = manager.unload_plugin("json-schema")
assert unload_result.success
```

### HTTP Protocol

The only public protocol implementation today is the HTTP client protocol used
by `FlextApiClient` and `FlextApi`:

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, c, m, p, r


class HttpOnlyApi(FlextApi):
    """Concrete HTTP API facade."""

    def health_check(self) -> p.Result[m.Api.HttpResponse]:
        return self.get("/health")


# Example without network access using a fake subclass.
class FakeHttpApi(HttpOnlyApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        if url.endswith("/health"):
            return r[m.Api.HttpResponse].ok(
                m.Api.create_response(
                    status_code=200,
                    body={"status": "healthy"},
                    headers={"Content-Type": "application/json"},
                )
            )
        return r[m.Api.HttpResponse].ok(m.Api.create_response(status_code=404, body={}))


api = FakeHttpApi(settings=FlextApiSettings(base_url="https://example.com"))
result = api.health_check()
assert result.success
assert result.unwrap().body["status"] == "healthy"
```

## Usage Examples

### HTTP Usage

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings

settings = FlextApiSettings(base_url="https://api.example.com", timeout=30)
api = FlextApi(settings=settings)

assert callable(api.get)
assert callable(api.post)
assert callable(api.put)
assert callable(api.delete)
assert callable(api.patch)
assert callable(api.request)
```

## Testing Strategy

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, c, m, p, r, r


class FakeHttpProtocol(FlextApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"protocol": "http", "endpoint": url},
                headers={"Content-Type": "application/json"},
            )
        )


def test_http_protocol():
    api = FakeHttpProtocol(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/test")
    assert result.success
    assert result.unwrap().body["protocol"] == "http"


test_http_protocol()
```

## What Is Not Implemented

The following protocols are **not** currently exposed by `flext-api` and are
therefore not documented as executable examples:

- GraphQL
- WebSocket
- Server-Sent Events (SSE)
- gRPC / Protocol Buffers
- MQTT

If a future release adds support for additional protocols, this page will be
updated with real, runnable examples.

## References

- GitHub Issue: #159 - Protocol Plugin Architecture
- `flext_api.protocols` module
