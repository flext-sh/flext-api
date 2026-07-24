# Protocols API Reference

<!-- TOC START -->
- [Protocols API Reference](#protocols-api-reference)
  - [Protocol Architecture](#protocol-architecture)
  - [HTTP Protocol Implementation](#http-protocol-implementation)
    - [FlextApiClient Implementation](#flextapiclient-implementation)
    - [HTTP Request/Response Models](#http-requestresponse-models)
  - [GraphQL Protocol Implementation](#graphql-protocol-implementation)
    - [GraphQL Support](#graphql-support)
  - [WebSocket Protocol Implementation](#websocket-protocol-implementation)
    - [WebSocket Communication](#websocket-communication)
  - [Server-Sent Events Protocol](#server-sent-events-protocol)
    - [Server-Sent Event Streaming](#server-sent-event-streaming)
  - [Storage Backend Protocol](#storage-backend-protocol)
    - [Storage Backend Object Storage](#storage-backend-object-storage)
  - [Protocol Stubs](#protocol-stubs)
    - [gRPC Stub - gRPC Protocol Buffers](#grpc-stub---grpc-protocol-buffers)
    - [Protobuf Stub - Binary Serialization](#protobuf-stub---binary-serialization)
  - [Quality Metrics](#quality-metrics)
  - [Usage Examples](#usage-examples)
    - [HTTP API Client](#http-api-client)
    - [Protocol Plugin System](#protocol-plugin-system)
<!-- TOC END -->

This section covers the protocol implementations and stubs that enable FLEXT-API to support multiple communication protocols through a plugin architecture.

## Protocol Architecture

FLEXT-API uses a protocol-based architecture that allows supporting multiple communication protocols (HTTP, GraphQL, WebSocket, etc.) through a unified interface. The currently implemented public HTTP surface is the `FlextApi` facade, `FlextApiClient`, and the protocol plugin manager.

```text
Protocol Layer
├── Protocol Implementations
│   ├── HTTP (REST APIs via FlextApi / FlextApiClient)
│   ├── GraphQL (not implemented in public API)
│   ├── WebSocket (not implemented in public API)
│   └── Server-Sent Events (not implemented in public API)
└── Protocol Plugin System (FlextApiProtocolPluginManager)
```

## HTTP Protocol Implementation

### FlextApiClient Implementation

Primary protocol implementation for REST APIs and HTTP-based communication.

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiClient, FlextApiSettings, c, m, p, r


class FakeHttpClient(FlextApiClient):
    """Fake HTTP client that runs without network access."""

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        if request.url.endswith("/users") and request.method == c.Api.Method.GET:
            return r[m.Api.HttpResponse].ok(
                m.Api.create_response(
                    status_code=200,
                    headers={"Content-Type": "application/json"},
                    body={"users": [{"id": "1", "name": "Alice"}]},
                )
            )
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(status_code=404, body={"error": "not found"})
        )


# Rebuild the Pydantic model now that FlextApiSettings is available in the script.
FakeHttpClient.model_rebuild()


class FakeApi(FlextApi):
    """Fake API facade wired to the fake HTTP client."""

    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        super().__init__(settings=settings)
        self._client = FakeHttpClient(settings=self.settings)


settings = FlextApiSettings(
    base_url="https://api.example.com",
    timeout=30.0,
    default_headers={"User-Agent": "FLEXT-API/0.9.9"},
)
api = FakeApi(settings=settings)

result = api.get("/users", request_kwargs={"params": {"limit": "10"}})
if result.success:
    response = result.unwrap()
    print(f"Status: {response.status_code}")
    print(f"Body: {response.body}")
```

**Key Features:**

- Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Request/response validation via Pydantic models
- Monadic error handling through `p.Result`
- Settings-driven configuration

### HTTP Request/Response Models

```python
from __future__ import annotations

from flext_api import c, m, p, r

# Create HTTP request
request = m.Api.HttpRequest(
    method=c.Api.Method.POST,
    url="https://api.example.com/users",
    headers={"Content-Type": "application/json"},
    body={"name": "Alice", "email": "alice@example.com"},
)

# Create a response directly using the model helper
response = m.Api.create_response(
    status_code=201,
    headers={"Content-Type": "application/json"},
    body={"id": "1", "name": "Alice", "email": "alice@example.com"},
)

# Access response data
print(f"Status: {response.status_code}")
print(f"Body: {response.body}")
print(f"Success: {response.success}")

# Wrap it in a Result when returning from a client method
result = r[m.Api.HttpResponse].ok(response)
print(f"Result success: {result.success}")
```

## GraphQL Protocol Implementation

### GraphQL Support

Protocol implementation for GraphQL APIs with query and mutation support.

This feature is not currently implemented in the public API.

## WebSocket Protocol Implementation

### WebSocket Communication

Protocol implementation for WebSocket connections and real-time messaging.

This feature is not currently implemented in the public API.

## Server-Sent Events Protocol

### Server-Sent Event Streaming

Protocol implementation for Server-Sent Events (SSE) for real-time data streaming.

This feature is not currently implemented in the public API.

## Storage Backend Protocol

### Storage Backend Object Storage

Protocol implementation for various storage backends (local filesystem, cloud storage, etc.).

This feature is not currently implemented in the public API.

## Protocol Stubs

### gRPC Stub - gRPC Protocol Buffers

Stub implementation for gRPC services using Protocol Buffers.

This feature is not currently implemented in the public API.

### Protobuf Stub - Binary Serialization

Stub for Protocol Buffer serialization/deserialization.

This feature is not currently implemented in the public API.

## Quality Metrics

| Module                          | Coverage | Status    | Description                        |
| ------------------------------- | -------- | --------- | ---------------------------------- |
| `protocols/http.py`             | 90%      | ✅ Stable | HTTP/REST implementation           |
| `protocols/graphql.py`          | —        | ❌ N/A    | Not implemented in public API      |
| `protocols/websocket.py`        | —        | ❌ N/A    | Not implemented in public API      |
| `protocols/sse.py`              | —        | ❌ N/A    | Not implemented in public API      |
| `protocols/storage_backend.py`  | —        | ❌ N/A    | Not implemented in public API      |
| `protocol_stubs/grpc_stub.py`   | —        | ❌ N/A    | Not implemented in public API      |
| `protocol_stubs/protobuf_stub.py` | —      | ❌ N/A    | Not implemented in public API      |

## Usage Examples

### HTTP API Client

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiClient, FlextApiSettings, c, m, p, r


class FakeHttpClient(FlextApiClient):
    """Fake HTTP client that runs without network access."""

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        if request.url.endswith("/users/123") and request.method == c.Api.Method.GET:
            return r[m.Api.HttpResponse].ok(
                m.Api.create_response(
                    status_code=200,
                    headers={"Content-Type": "application/json"},
                    body={"id": "123", "name": "Alice", "email": "alice@example.com"},
                )
            )
        if request.url.endswith("/users") and request.method == c.Api.Method.POST:
            return r[m.Api.HttpResponse].ok(
                m.Api.create_response(
                    status_code=201,
                    headers={"Content-Type": "application/json"},
                    body={"id": "456", **(request.body or {})},
                )
            )
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(status_code=404, body={"error": "not found"})
        )


class UserApiClient:
    """Client supporting HTTP operations through the real FLEXT-API facade."""

    def __init__(self, base_url: str = "https://api.example.com"):
        self.api = FlextApi(settings=FlextApiSettings(base_url=base_url, timeout=10.0))
        # Wire a fake client so the example runs without network access
        self.api._client = FakeHttpClient(settings=self.api.settings)

    def get_user(self, user_id: str) -> t.JsonMapping | None:
        """Get user via REST API."""
        result = self.api.get(f"/users/{user_id}")
        return result.unwrap().body if result.success else None

    def create_user(self, user_data: t.JsonMapping) -> t.JsonMapping | None:
        """Create user via REST API."""
        result = self.api.post("/users", data=user_data)
        return result.unwrap().body if result.success else None


# Usage
client = UserApiClient(base_url="https://api.example.com")
user = client.get_user("123")
if user:
    print(f"User: {user['name']} ({user['email']})")

created = client.create_user({"name": "Bob", "email": "bob@example.com"})
if created:
    print(f"Created user: {created['name']} ({created['id']})")
```

### Protocol Plugin System

```python
from __future__ import annotations

from abc import abstractmethod

from flext_api import (
    FlextApiProtocolPluginManager,
    FlextApiProtocolPluginTypes,
    c,
    m,
    p,
    r,
    t,
)


class HttpProtocolPlugin(FlextApiProtocolPluginTypes.Protocol):
    """Concrete HTTP protocol plugin."""

    def __init__(self) -> None:
        super().__init__(
            name="http",
            version="1.0.0",
            description="HTTP/REST protocol plugin",
        )

    def supported_protocols(self) -> t.StrSequence:
        return ["http", "https"]

    def supports_protocol(self, protocol: str) -> bool:
        return protocol in self.supported_protocols()

    def send_request(
        self, request: t.JsonMapping, **kwargs: t.Scalar
    ) -> p.Result[t.JsonMapping]:
        return r[t.JsonMapping].ok({"status": 200, "request": request})


class JsonSchemaPlugin(FlextApiProtocolPluginTypes.Schema):
    """Concrete JSON schema plugin."""

    def __init__(self) -> None:
        super().__init__(
            name="json-schema",
            version="1.0.0",
            description="JSON schema validation plugin",
        )

    def schema_version(self) -> str:
        return "2020-12"

    def load_schema(self, schema_source: str) -> p.Result[t.JsonValue]:
        return r[t.JsonValue].ok({})

    def validate_request(
        self, request: t.JsonMapping, schema: t.JsonMapping
    ) -> p.Result[bool]:
        return r[bool].ok(value=True)

    def validate_response(
        self, response: t.JsonMapping, schema: t.JsonMapping
    ) -> p.Result[bool]:
        return r[bool].ok(value=True)


manager = FlextApiProtocolPluginManager.Manager()

http_plugin = HttpProtocolPlugin()
schema_plugin = JsonSchemaPlugin()

load_result = manager.load_plugin(http_plugin)
assert load_result.success

load_result = manager.load_plugin(schema_plugin)
assert load_result.success

print(f"Loaded plugins: {manager.list_loaded_plugins()}")

resolved = manager.resolve_plugin("http")
if resolved.success:
    plugin = resolved.unwrap()
    print(f"Resolved plugin: {plugin.name} v{plugin.version}")

shutdown_result = manager.shutdown_all()
assert shutdown_result.success
```

This protocol-based architecture provides a flexible foundation for supporting multiple communication patterns while maintaining consistent error handling and type safety across all protocols. The public HTTP surface and plugin manager are available today; additional protocols can be added through the plugin system.
