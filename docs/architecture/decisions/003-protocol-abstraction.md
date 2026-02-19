# 003. Protocol Plugin Architecture

<!-- TOC START -->

- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
  - [Risks](#risks)
- [Alternatives Considered](#alternatives-considered)
  - [Option 1: Monolithic Client](#option-1-monolithic-client)
  - [Option 2: Inheritance Hierarchy](#option-2-inheritance-hierarchy)
  - [Option 3: Facade Pattern Only](#option-3-facade-pattern-only)
- [Implementation Architecture](#implementation-architecture)
  - [Protocol Interface](#protocol-interface)
  - [Protocol Registry](#protocol-registry)
  - [Unified Client Interface](#unified-client-interface)
- [Protocol Implementations](#protocol-implementations)
  - [HTTP Protocol](#http-protocol)
  - [GraphQL Protocol](#graphql-protocol)
- [Usage Examples](#usage-examples)
  - [HTTP Usage](#http-usage)
  - [GraphQL Usage](#graphql-usage)
  - [WebSocket Usage](#websocket-usage)
- [Testing Strategy](#testing-strategy)
  - [Protocol Isolation Testing](#protocol-isolation-testing)
  - [Integration Testing](#integration-testing)
- [Performance Considerations](#performance-considerations)
  - [Connection Pooling](#connection-pooling)
  - [Request Batching](#request-batching)
  - [Resource Management](#resource-management)
- [Extension Points](#extension-points)
  - [Adding New Protocols](#adding-new-protocols)
- [Monitoring and Observability](#monitoring-and-observability)
  - [Protocol Metrics](#protocol-metrics)
  - [Health Checks](#health-checks)
- [Migration Strategy](#migration-strategy)
  - [Phase 1: Core Architecture](#phase-1-core-architecture)
  - [Phase 2: Additional Protocols](#phase-2-additional-protocols)
  - [Phase 3: Ecosystem Integration](#phase-3-ecosystem-integration)
- [References](#references)

<!-- TOC END -->

Date: 2025-01-01

## Status

Accepted

## Context

Modern applications need to communicate with various APIs using different protocols (HTTP/REST, GraphQL, WebSocket, gRPC, etc.). Each protocol has different connection patterns, message formats, and error handling. The challenge was to create a unified interface that:

1. Supports multiple protocols through a consistent API
1. Allows easy addition of new protocols
1. Maintains protocol-specific optimizations and features
1. Provides unified error handling and monitoring
1. Enables protocol negotiation and fallback

Key considerations:

- Enterprise applications use diverse protocols (REST, GraphQL, WebSocket, SSE)
- Protocol implementations have different connection models and APIs
- Need to maintain high performance for each protocol
- Error handling and monitoring should be consistent across protocols
- Future protocols (gRPC, MQTT, etc.) should be easily addable

## Decision

FLEXT-API will implement a **Protocol Plugin Architecture** with:

1. **Abstract Base Protocol**: Common interface for all protocols
1. **Protocol Registry**: Dynamic protocol discovery and instantiation
1. **Protocol-Specific Implementations**: Optimized implementations for each protocol
1. **Unified Client Interface**: Single client interface that delegates to protocol implementations

## Consequences

### Positive

- **Extensibility**: New protocols can be added without changing core API
- **Performance**: Each protocol can be optimized for its specific use case
- **Consistency**: Unified error handling and monitoring across all protocols
- **Testability**: Protocol implementations can be tested and mocked independently
- **Maintainability**: Protocol-specific code is isolated and easier to maintain
- **Future-Proof**: Easy to add new protocols as they emerge

### Negative

- **Complexity**: Additional abstraction layer increases complexity
- **Indirection**: Method calls go through multiple layers of abstraction
- **Learning Curve**: Developers need to understand both generic and protocol-specific APIs
- **Testing Overhead**: Each protocol needs comprehensive testing

### Risks

- **Performance Overhead**: Abstraction layer could impact performance-critical operations
- **Inconsistent Implementations**: Different protocols might have slightly different behaviors
- **Maintenance Burden**: Multiple protocol implementations increase maintenance complexity

## Alternatives Considered

### Option 1: Monolithic Client

- **Description**: Single client class with conditional logic for different protocols
- **Pros**: Simple implementation, direct performance
- **Cons**: Hard to maintain, difficult to add new protocols, protocol coupling
- **Rejected**: Violates open/closed principle, becomes unmaintainable

### Option 2: Inheritance Hierarchy

- **Description**: Base client class with protocol-specific subclasses
- **Pros**: Object-oriented approach, shared functionality
- **Cons**: Tight coupling, inflexible for dynamic protocol selection
- **Rejected**: Doesn't support runtime protocol selection well

### Option 3: Facade Pattern Only

- **Description**: Simple facade that delegates to protocol-specific functions
- **Pros**: Simple, minimal abstraction
- **Cons**: No common interface, inconsistent error handling, harder to test
- **Rejected**: Doesn't provide enough structure for enterprise use

## Implementation Architecture

### Protocol Interface

```python
class BaseProtocol(ABC):
    """Abstract base class for all protocol implementations."""

    @abstractmethod
    def create_client(self, config: Dict[str, object]) -> object:
        """Create protocol-specific client instance."""
        pass

    @abstractmethod
    async def execute_request(self, request: object) -> FlextResult[object]:
        """Execute request using protocol-specific logic."""
        pass

    @abstractmethod
    def get_capabilities(self) -> ProtocolCapabilities:
        """Get protocol capabilities and features."""
        pass

    @abstractmethod
    async def health_check(self) -> FlextResult[bool]:
        """Check protocol connectivity and health."""
        pass
```

### Protocol Registry

```python
class ProtocolRegistry:
    """Registry for protocol implementations with discovery."""

    def __init__(self):
        self._protocols: Dict[str, Type[BaseProtocol]] = {}
        self._capabilities: Dict[str, ProtocolCapabilities] = {}

    def register(self, name: str, protocol_class: Type[BaseProtocol]):
        """Register a protocol implementation."""
        self._protocols[name] = protocol_class
        # Cache capabilities for performance
        self._capabilities[name] = protocol_class().get_capabilities()

    def get_protocol(self, name: str) -> BaseProtocol:
        """Get protocol instance by name."""
        if name not in self._protocols:
            raise ValueError(f"Protocol '{name}' not registered")
        return self._protocols[name]()

    def list_protocols(self) -> t.StringList:
        """List all registered protocol names."""
        return list(self._protocols.keys())

    def get_capabilities(self, name: str) -> ProtocolCapabilities:
        """Get cached protocol capabilities."""
        return self._capabilities.get(name)
```

### Unified Client Interface

```python
class FlextApiClient(FlextService[None]):
    """Unified client that delegates to protocol implementations."""

    def __init__(self, protocol: str = "http", **config):
        super().__init__()
        self._protocol_name = protocol
        self._config = config
        self._protocol_instance = None

    async def _get_protocol_instance(self) -> BaseProtocol:
        """Lazy initialization of protocol instance."""
        if self._protocol_instance is None:
            registry = ProtocolRegistry()
            self._protocol_instance = registry.get_protocol(self._protocol_name)
        return self._protocol_instance

    async def request(self, method: str, url: str, **kwargs) -> FlextResult[object]:
        """Unified request method that delegates to protocol."""
        protocol = await self._get_protocol_instance()

        # Convert unified request to protocol-specific format
        protocol_request = self._convert_to_protocol_request(method, url, kwargs)

        # Execute using protocol implementation
        result = await protocol.execute_request(protocol_request)

        # Convert back to unified response format
        return self._convert_from_protocol_response(result)

    def _convert_to_protocol_request(self, method: str, url: str, kwargs) -> object:
        """Convert unified request to protocol-specific format."""
        if self._protocol_name == "http":
            return FlextApiModels.HttpRequest(method=method, url=url, **kwargs)
        elif self._protocol_name == "graphql":
            return GraphQLRequest(query=kwargs.get("query"), variables=kwargs.get("variables"))
        # ... other protocol conversions

    def _convert_from_protocol_response(self, result: FlextResult[object]) -> FlextResult[object]:
        """Convert protocol-specific response to unified format."""
        # Standardize response format across protocols
        return result
```

## Protocol Implementations

### HTTP Protocol

```python
class FlextWebProtocol(BaseProtocol):
    """HTTP/REST protocol implementation."""

    def create_client(self, config: Dict[str, object]) -> httpx.AsyncClient:
        return httpx.AsyncClient(**config)

    async def execute_request(self, request: FlextApiModels.HttpRequest) -> FlextResult[FlextApiModels.HttpResponse]:
        client = self.create_client(request.config)

        try:
            response = await client.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                content=request.body,
                timeout=request.timeout
            )

            return FlextResult.ok(FlextApiModels.HttpResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                response_time=response.elapsed.total_seconds()
            ))
        except Exception as e:
            return FlextResult.fail(f"HTTP request failed: {e}")
        finally:
            await client.aclose()

    def get_capabilities(self) -> ProtocolCapabilities:
        return ProtocolCapabilities(
            supports_streaming=True,
            supports_binary=True,
            supports_compression=True,
            max_request_size=100 * 1024 * 1024,  # 100MB
            timeout_range=(1, 300)  # 1 second to 5 minutes
        )
```

### GraphQL Protocol

```python
class GraphQLProtocol(BaseProtocol):
    """GraphQL protocol implementation."""

    def create_client(self, config: Dict[str, object]) -> gql.Client:
        transport = AIOHTTPTransport(url=config["url"])
        return gql.Client(transport=transport, execute_timeout=config.get("timeout", 30))

    async def execute_request(self, request: GraphQLRequest) -> FlextResult[GraphQLResponse]:
        client = self.create_client(request.config)

        try:
            result = await client.execute_async(
                gql.gql(request.query),
                variable_values=request.variables
            )

            return FlextResult.ok(GraphQLResponse(data=result))
        except Exception as e:
            return FlextResult.fail(f"GraphQL request failed: {e}")

    def get_capabilities(self) -> ProtocolCapabilities:
        return ProtocolCapabilities(
            supports_streaming=False,
            supports_binary=False,
            supports_compression=True,
            supports_introspection=True,
            query_complexity_limit=1000
        )
```

## Usage Examples

### HTTP Usage

```python
from flext_api import FlextApiClient

# HTTP client (default protocol)
client = FlextApiClient(protocol="http", base_url="https://api.example.com")
result = await client.get("/users/123")
```

### GraphQL Usage

```python
# GraphQL client
client = FlextApiClient(protocol="graphql", url="https://api.example.com/graphql")

query = """
    query GetUser($id: ID!) {
        user(id: $id) {
            name
            email
        }
    }
"""

result = await client.request("query", query, variables={"id": "123"})
```

### WebSocket Usage

```python
# WebSocket client
client = FlextApiClient(protocol="websocket", url="wss://api.example.com/ws")
await client.connect()
await client.send({"type": "subscribe", "channel": "updates"})
```

## Testing Strategy

### Protocol Isolation Testing

```python
@pytest.fixture
def http_protocol():
    return FlextWebProtocol()

@pytest.mark.asyncio
async def test_http_request_success(http_protocol):
    # Mock httpx client
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = '{"success": true}'
        mock_response.elapsed = timedelta(seconds=0.5)

        mock_client.return_value.request.return_value = mock_response

        request = FlextApiModels.HttpRequest(method="GET", url="https://api.example.com/test")
        result = await http_protocol.execute_request(request)

        assert result.is_success
        assert result.unwrap().status_code == 200
```

### Integration Testing

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_protocol_registry_integration():
    registry = ProtocolRegistry()

    # Test protocol registration
    registry.register("test", TestProtocol)
    assert "test" in registry.list_protocols()

    # Test protocol instantiation
    protocol = registry.get_protocol("test")
    assert isinstance(protocol, TestProtocol)

    # Test capabilities caching
    capabilities = registry.get_capabilities("test")
    assert capabilities.supports_streaming is True
```

## Performance Considerations

### Connection Pooling

- HTTP protocol uses httpx connection pooling
- GraphQL maintains persistent connections
- WebSocket implements connection reuse

### Request Batching

- GraphQL supports query batching
- HTTP can batch requests using HTTP/2 multiplexing
- Protocol-specific optimizations maintained

### Resource Management

- Automatic cleanup of protocol resources
- Connection limits and health monitoring
- Memory-efficient request processing

## Extension Points

### Adding New Protocols

1. **Implement Protocol Class**:

```python
class CustomProtocol(BaseProtocol):
    def create_client(self, config: Dict[str, object]):
        return CustomClient(**config)

    async def execute_request(self, request):
        # Custom protocol logic
        pass

    def get_capabilities(self):
        return ProtocolCapabilities(...)
```

2. **Register Protocol**:

```python
registry = ProtocolRegistry()
registry.register("custom", CustomProtocol)
```

3. **Use in Client**:

```python
client = FlextApiClient(protocol="custom", **config)
```

## Monitoring and Observability

### Protocol Metrics

- Request count and latency by protocol
- Error rates and failure patterns
- Connection pool utilization
- Protocol-specific performance metrics

### Health Checks

- Protocol connectivity verification
- Capability validation
- Resource usage monitoring
- Automatic failover detection

## Migration Strategy

### Phase 1: Core Architecture

- [x] Implement protocol abstraction interfaces
- [x] Create protocol registry system
- [x] Implement HTTP protocol (primary use case)

### Phase 2: Additional Protocols

- [x] Implement GraphQL protocol
- [ ] Implement WebSocket protocol
- [ ] Implement Server-Sent Events protocol

### Phase 3: Ecosystem Integration

- [ ] Update documentation with protocol examples
- [ ] Create protocol selection guidelines
- [ ] Provide migration utilities for existing code
- [ ] Establish protocol testing standards

## References

- [Protocol Abstraction Pattern](https://martinfowler.com/eaaCatalog/plugin.html)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Dependency Injection in Python](https://github.com/google/guice)
- GitHub Issue: #234 - Protocol Plugin Architecture
