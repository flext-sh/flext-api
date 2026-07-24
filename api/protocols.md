# Protocols API Reference

<!-- TOC START -->
- [Protocols API Reference](#protocols-api-reference)
  - [Protocol Architecture](#protocol-architecture)
  - [HTTP Protocol Implementation](#http-protocol-implementation)
    - [FlextWebREST Implementation](#flextwebrest-implementation)
    - [HTTP Request/Response Models](#http-requestresponse-models)
  - [GraphQL Protocol Implementation](#graphql-protocol-implementation)
    - [GraphQLQL Support](#graphqlql-support)
    - [GraphQL Operations](#graphql-operations)
  - [WebSocket Protocol Implementation](#websocket-protocol-implementation)
    - [WebSockettime Communication](#websockettime-communication)
  - [Server-Sent Events Protocol](#server-sent-events-protocol)
    - [ServerSentEventay Streaming](#serversenteventay-streaming)
  - [Storage Backend Protocol](#storage-backend-protocol)
    - [StorageBackendObject Storage](#storagebackendobject-storage)
  - [Protocol Stubs](#protocol-stubs)
    - [GRPC Stub - gRPC Protocol Buffers](#grpc-stub---grpc-protocol-buffers)
    - [Protobuf Stub - Binary Serialization](#protobuf-stub---binary-serialization)
  - [Quality Metrics](#quality-metrics)
  - [Usage Examples](#usage-examples)
    - [Multi-Protocol API Client](#multi-protocol-api-client)
    - [Protocol Plugin System](#protocol-plugin-system)
<!-- TOC END -->

This section covers the protocol implementations and stubs that enable FLEXT-API to support multiple communication protocols through a plugin architecture.

## Protocol Architecture

FLEXT-API uses a protocol-based architecture that allows supporting multiple communication protocols (HTTP, GraphQL, WebSocket, etc.) through a unified interface.

```
Protocol Layer
├── Protocol Implementations (protocol_impls/)
│   ├── HTTP (REST APIs)
│   ├── GraphQL (GraphQL APIs)
│   ├── WebSocket (Real-time communication)
│   ├── Server-Sent Events (One-way streaming)
│   └── Storage Backend (File/t.JsonValue storage)
└── Protocol Stubs (protocol_stubs/)
    ├── gRPC (Protocol buffer services)
    └── Protobuf (Binary serialization)
```

## HTTP Protocol Implementation

### FlextWebREST Implementation

Primary protocol implementation for REST APIs and HTTP-based communication.

```python notest
from flext_api import FlextWeb
from flext_cli import u
from flext_core import FlextSettings

# Create HTTP protocol instance
http_protocol = FlextWeb
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"User-Agent": "FLEXT-API/0.9.9"},
)

# Execute HTTP operations
result = http_protocol.execute_request(
    method="GET", path="/users", params={"limit": 10}
)

if result.success:
    response = result.unwrap()
    u.Cli.print(f"Status: {response.status_code}")
    u.Cli.print(f"Data: {response.json()}")
```

**Key Features:**

- Standard HTTP methods (GET, POST, PUT, DELETE, etc.)
- Request/response interceptors
- Automatic retry logic
- Connection pooling
- Header and cookie management

### HTTP Request/Response Models

```python notest
from flext_api import (
    FlextApiModels.HttpRequest,
    FlextApiModels.HttpResponse,
    FlextWebHeaders,
    FlextWebCookies
)

# Create HTTP request
request = FlextApiModels.HttpRequest(
    method="POST",
    url="/users",
    headers={"Content-Type": "application/json"},
    body='{"name": "Alice", "email": "alice@example.com"}'
)

# Execute request
response = http_protocol.execute(request)

# Access response data
if response.success:
    data = response.json()
    headers = response.headers
    cookies = response.cookies
```

## GraphQL Protocol Implementation

### GraphQLQL Support

Protocol implementation for GraphQL APIs with query and mutation support.

```python notest
from flext_api import GraphQL

# Create GraphQL protocol
graphql_protocol = GraphQL
    endpoint="https://api.example.com/graphql",
    headers={"Authorization": "Bearer token123"},
)

# Execute GraphQL query
query = """
    query GetUser($id: ID!) {
        user(id: $id) {
            id
            name
            email
        }
    }
"""

variables = {"id": "user_123"}
result = graphql_protocol.execute_query(query, variables)

if result.success:
    data = result.unwrap()
    user = data["user"]
    u.Cli.print(f"User: {user['name']} ({user['email']})")
```

**Key Features:**

- Query execution with variables
- Mutation support
- Error handling and field validation
- Introspection query support
- Subscription support (when available)

### GraphQL Operations

```python notest
# Query with fragments
fragment_query = """
    query GetUserWithPosts($id: ID!) {
        user(id: $id) {
            ...Useru.Fields
            posts {
                id
                title
            }
        }
    }

    fragment Useru.Fields on User {
        id
        name
        email
    }
"""

# Mutation example
mutation = """
    mutation CreateUser($input: UserInput!) {
        createUser(input: $input) {
            id
            name
            email
        }
    }
"""

mutation_variables = {"input": {"name": "Bob", "email": "bob@example.com"}}

result = graphql_protocol.execute_mutation(mutation, mutation_variables)
```

## WebSocket Protocol Implementation

### WebSockettime Communication

Protocol implementation for WebSocket connections and real-time messaging.

```python notest
from flext_api import WebSocket

# Create WebSocket protocol
websocket_protocol = WebSocket
    url="wss://api.example.com/ws", headers={"Authorization": "Bearer token123"}
)

# Connect to WebSocket
connection_result = websocket_protocol.connect()
if connection_result.success:
    connection = connection_result.unwrap()

    # Send message
    message = {"type": "subscribe", "channel": "notifications"}
    send_result = connection.send(message)

    # Receive messages
    while True:
        message_result = connection.receive()
        if message_result.success:
            message = message_result.unwrap()
            u.Cli.print(f"Received: {message}")

        # Handle connection close
        if connection.is_closed():
            break
```

**Key Features:**

- Connection management
- Message sending/receiving
- Automatic reconnection
- Heartbeat/ping-pong
- Message serialization

## Server-Sent Events Protocol

### ServerSentEventay Streaming

Protocol implementation for Server-Sent Events (SSE) for real-time data streaming.

```python notest
from flext_api import ServerSentEvent

# Create SSE protocol
sse_protocol = ServerSentEvent
    url="https://api.example.com/events", headers={"Authorization": "Bearer token123"}
)

# Connect to event stream
stream_result = sse_protocol.connect()
if stream_result.success:
    stream = stream_result.unwrap()

    # Listen for events
    for event in stream:
        if event.success:
            sse_event = event.unwrap()
            u.Cli.print(f"Event: {sse_event.event_type}")
            u.Cli.print(f"Data: {sse_event.data}")

        # Handle stream end
        if stream.is_closed():
            break
```

**Key Features:**

- Event stream connection
- Automatic reconnection on errors
- Event type filtering
- Last-Event-ID support
- Connection retry logic

## Storage Backend Protocol

### StorageBackendObject Storage

Protocol implementation for various storage backends (local filesystem, cloud storage, etc.).

```python notest
from flext_api import StorageBackend

# Create storage protocol
storage_protocol = StorageBackend
    backend_type="s3",  # or "local", "gcs", "azure"
    settings={
        "bucket": "my-bucket",
        "region": "us-east-1",
        "access_key": "...",
        "secret_key": "...",
    },
)

# File operations
upload_result = storage_protocol.upload_file(
    local_path="/path/to/file.txt", remote_path="uploads/file.txt"
)

if upload_result.success:
    # File uploaded successfully
    remote_url = upload_result.unwrap()

# Download file
download_result = storage_protocol.download_file(
    remote_path="uploads/file.txt", local_path="/tmp/downloaded_file.txt"
)

# List files
list_result = storage_protocol.list_files("uploads/")
if list_result.success:
    files = list_result.unwrap()
    for file in files:
        u.Cli.print(f"File: {file.name} ({file.size} bytes)")
```

**Key Features:**

- Multiple storage backend support
- File upload/download operations
- Directory listing and management
- Metadata handling
- Access control integration

## Protocol Stubs

### GRPC Stub - gRPC Protocol Buffers

Stub implementation for gRPC services using Protocol Buffers.

```python notest
from flext_api import GrpcStub

# Create gRPC stub
grpc_stub = GrpcStub(
    target="localhost:50051",
    credentials=None,  # or ssl_channel_credentials()
    options=[("grpc.max_receive_message_size", 1024 * 1024 * 100)],
)

# Call gRPC methods
request = user_pb2.GetUserRequest(user_id="user_123")
response = grpc_stub.call_unary(
    service="UserService",
    method="GetUser",
    request=request,
    response_type=user_pb2.UserResponse,
)

if response.success:
    user = response.unwrap()
    u.Cli.print(f"User: {user.name} ({user.email})")
```

### Protobuf Stub - Binary Serialization

Stub for Protocol Buffer serialization/deserialization.

```python notest
from flext_api import ProtobufStub

# Create protobuf stub
protobuf_stub = ProtobufStub()

# Serialize data
user_data = {"id": "user_123", "name": "Alice", "email": "alice@example.com"}
serialized = protobuf_stub.serialize(user_data, message_type="User")

# Deserialize data
deserialized = protobuf_stub.deserialize(serialized, message_type="User")
```

## Quality Metrics

| Module                              | Coverage | Status    | Description                          |
| ----------------------------------- | -------- | --------- | ------------------------------------ |
| `protocol_impls/http.py`            | 90%      | ✅ Stable | HTTP/REST implementation             |
| `protocol_impls/graphql.py`         | 85%      | ✅ Good   | GraphQL query/mutation support       |
| `protocol_impls/websocket.py`       | 88%      | ✅ Good   | WebSocket real-time communication    |
| `protocol_impls/sse.py`             | 82%      | ✅ Good   | Server-sent events streaming         |
| `protocol_impls/storage_backend.py` | 87%      | ✅ Good   | File/t.JsonValue storage abstraction |
| `protocol_stubs/grpc_stub.py`       | 80%      | ✅ Good   | gRPC protocol buffer support         |
| `protocol_stubs/protobuf_stub.py`   | 85%      | ✅ Good   | Binary serialization                 |

## Usage Examples

### Multi-Protocol API Client

```python notest
from flext_api import FlextApiClient
from flext_api import FlextWeb
from flext_api import GraphQL
from flext_api import WebSocket



class MultiProtocolClient:
    """Client supporting multiple protocols."""

    def __init__(self):
        self.http = FlextWebl="https://api.example.com")
        self.graphql = GraphQLt="https://api.example.com/graphql")
        self.websocket = WebSockets://api.example.com/ws")

    def get_user_http(self, user_id: str) -> t.JsonMapping:
        """Get user via REST API."""
        result = self.http.execute_request("GET", f"/users/{user_id}")
        return result.unwrap().json() if result.success else None

    def get_user_graphql(self, user_id: str) -> t.JsonMapping:
        """Get user via GraphQL."""
        query = """
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    name
                    email
                    posts {
                        id
                        title
                    }
                }
            }
        """
        result = self.graphql.execute_query(query, {"id": user_id})
        return result.unwrap() if result.success else None

    def subscribe_to_notifications(self, callback):
        """Subscribe to real-time notifications."""
        connection = self.websocket.connect().unwrap()

        # Send subscription message
        connection.send({"type": "subscribe", "channel": "notifications"})

        # Listen for messages
        while not connection.is_closed():
            message = connection.receive().unwrap()
            callback(message)


# Usage
client = MultiProtocolClient()

# Get user data via different protocols
user_rest = client.get_user_http("user_123")
user_graphql = client.get_user_graphql("user_123")

u.Cli.print(f"REST user: {user_rest['name']}")
u.Cli.print(f"GraphQL user: {user_graphql['name']}")
```

### Protocol Plugin System

```python notest
from flext_api import ProtocolRegistry
from flext_api import FlextWeb
from flext_api import GraphQL

# Register protocols
registry = ProtocolRegistry()
registry.register("http", FlextWeb
registry.register("graphql", GraphQL

# Use protocols dynamically
http_protocol = registry.get_protocol("http")
graphql_protocol = registry.get_protocol("graphql")


# Configure based on requirements
def create_api_client(protocol_name: str, settings: dict):
    """Create API client with specified protocol."""
    protocol_class = registry.get_protocol(protocol_name)
    return protocol_class(**settings)


# Create clients for different services
user_api = create_api_client("http", {"base_url": "https://user-api.com"})
content_api = create_api_client(
    "graphql", {"endpoint": "https://content-api.com/graphql"}
)
```

This protocol-based architecture provides a flexible foundation for supporting multiple communication patterns while maintaining consistent error handling and type safety across all protocols.
