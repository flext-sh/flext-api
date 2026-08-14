# 003. Protocol Plugin Architecture

<!-- TOC START -->
- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
- [Implementation Examples](#implementation-examples)
  - [Protocol Plugin Manager](#protocol-plugin-manager)
  - [HTTP Protocol Facade](#http-protocol-facade)
- [What Is Not Implemented](#what-is-not-implemented)
- [References](#references)
<!-- TOC END -->

Date: 2025-01-01

## Status

Accepted

## Context

Enterprise applications consume diverse APIs, but `flext-api` currently focuses
on HTTP/REST. The architecture keeps the HTTP surface clean while leaving room
for future protocol support through a plugin-style boundary.

## Decision

`flext-api` exposes a single HTTP-focused facade (`FlextApi`) and a typed
protocol layer (`p.Api`) for HTTP operations. Protocol plugins are managed by
the exported `FlextApiProtocolPluginManager` and `FlextApiProtocolPluginTypes`
shards, which provide a railway result-oriented lifecycle contract.

## Consequences

### Positive

- Extensibility without changing `FlextApi`
- Unified `p.Result` error handling across boundaries
- Plugin and HTTP clients can be tested independently

### Negative

- Only HTTP is implemented today
- Plugin lifecycle adds a small amount of boilerplate

## Implementation Examples

### Protocol Plugin Manager

```python
from __future__ import annotations

from flext_api import FlextApiProtocolPluginManager, FlextApiProtocolPluginTypes, p, r


class JsonSchemaPlugin(FlextApiProtocolPluginTypes.Plugin):
    """Example plugin implementing the lifecycle contract."""

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

assert "json-schema" in manager.list_loaded_plugins()

resolve_result = manager.resolve_plugin("json-schema")
assert resolve_result.success
assert resolve_result.unwrap().version == "1.0.0"

assert manager.unload_plugin("json-schema").success```
### HTTP Protocol Facade

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class HttpOnlyApi(FlextApi):
    def health_check(self) -> p.Result[m.Api.HttpResponse]:
        return self.get("/health")


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
assert result.unwrap().body["status"] == "healthy"```
## What Is Not Implemented

The following protocols are **not** currently exposed by `flext-api`:

- GraphQL
- WebSocket
- Server-Sent Events (SSE)
- gRPC / Protocol Buffers
- MQTT

If a future release adds support for additional protocols, this page will be
updated with real, runnable examples.

## References

- GitHub Issue: #159 - Protocol Plugin Architecture
