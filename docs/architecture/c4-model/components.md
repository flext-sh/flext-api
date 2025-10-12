# C4 Model - Components

## Overview

This document describes the **Component** level of the C4 model for FLEXT-API, showing the key components within each container and their relationships.

## Component Diagram

```plantuml
@startuml FLEXT-API Components
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title FLEXT-API Component Diagram

Container_Boundary(api_client, "HTTP Client Container") {
    Component(client_core, "HTTP Client Core", "Python", "Main client orchestrator with connection management")
    Component(request_builder, "Request Builder", "Python", "Request construction and validation")
    Component(response_handler, "Response Handler", "Python", "Response processing and transformation")
    Component(connection_pool, "Connection Pool", "httpx", "HTTP connection pooling and reuse")
    Component(retry_logic, "Retry Logic", "Python", "Exponential backoff retry mechanism")
    Component(auth_handler, "Authentication Handler", "Python", "Auth token and credential management")
}

Container_Boundary(fastapi_app, "FastAPI Application Container") {
    Component(app_factory, "Application Factory", "Python", "FastAPI app creation and configuration")
    Component(route_registry, "Route Registry", "Python", "API route registration and validation")
    Component(middleware_stack, "Middleware Stack", "Python", "Request/response processing pipeline")
    Component(error_formatter, "Error Formatter", "Python", "Error response formatting and logging")
    Component(health_checker, "Health Checker", "Python", "System health and readiness endpoints")
}

Container_Boundary(protocol_layer, "Protocol Layer Container") {
    Component(protocol_registry, "Protocol Registry", "Python", "Protocol discovery and instantiation")
    Component(http_protocol, "HTTP Protocol", "Python", "REST API protocol implementation")
    Component(graphql_protocol, "GraphQL Protocol", "Python", "GraphQL query/mutation handling")
    Component(websocket_protocol, "WebSocket Protocol", "Python", "Real-time WebSocket communication")
    Component(sse_protocol, "SSE Protocol", "Python", "Server-Sent Events streaming")
}

Container_Boundary(storage_layer, "Storage Layer Container") {
    Component(storage_router, "Storage Router", "Python", "Backend selection and load balancing")
    Component(s3_backend, "S3 Backend", "boto3", "Amazon S3 storage operations")
    Component(gcs_backend, "GCS Backend", "google-cloud-storage", "Google Cloud Storage operations")
    Component(azure_backend, "Azure Backend", "azure-storage-blob", "Azure Blob Storage operations")
    Component(local_backend, "Local Backend", "Python", "Local filesystem operations")
}

Container_Boundary(config_layer, "Configuration Layer") {
    Component(config_loader, "Config Loader", "Python", "Environment and file configuration loading")
    Component(config_validator, "Config Validator", "Pydantic", "Configuration validation and type checking")
    Component(secret_manager, "Secret Manager", "Python", "Secure credential and secret handling")
    Component(config_watcher, "Config Watcher", "Python", "Configuration change monitoring")
}

Container_Boundary(flext_core, "FLEXT-Core Foundation") {
    Component(flext_result, "FlextCore.Result[T]", "Python", "Railway-oriented error handling")
    Component(flext_container, "FlextCore.Container", "Python", "Dependency injection and service management")
    Component(flext_models, "FlextCore.Models", "Python", "Domain modeling with Pydantic")
    Component(flext_logger, "FlextCore.Logger", "Python", "Structured logging with correlation")
}

Rel(client_core, request_builder, "Uses", "builds requests")
Rel(client_core, response_handler, "Uses", "processes responses")
Rel(client_core, connection_pool, "Uses", "manages connections")
Rel(client_core, retry_logic, "Uses", "handles retries")
Rel(client_core, auth_handler, "Uses", "manages auth")

Rel(request_builder, flext_models, "Uses", "request models")
Rel(response_handler, flext_result, "Returns", "FlextCore.Result")
Rel(auth_handler, flext_container, "Uses", "credential storage")

Rel(app_factory, route_registry, "Configures", "route setup")
Rel(app_factory, middleware_stack, "Configures", "middleware pipeline")
Rel(app_factory, error_formatter, "Uses", "error handling")
Rel(app_factory, health_checker, "Includes", "health endpoints")

Rel(route_registry, protocol_registry, "Routes to", "protocol dispatch")
Rel(middleware_stack, flext_logger, "Uses", "request logging")

Rel(protocol_registry, http_protocol, "Instantiates", "HTTP clients")
Rel(protocol_registry, graphql_protocol, "Instantiates", "GraphQL clients")
Rel(protocol_registry, websocket_protocol, "Instantiates", "WebSocket clients")
Rel(protocol_registry, sse_protocol, "Instantiates", "SSE clients")

Rel(storage_router, s3_backend, "Routes to", "S3 operations")
Rel(storage_router, gcs_backend, "Routes to", "GCS operations")
Rel(storage_router, azure_backend, "Routes to", "Azure operations")
Rel(storage_router, local_backend, "Routes to", "local operations")

Rel(config_loader, config_validator, "Validates", "config data")
Rel(config_validator, flext_models, "Uses", "validation models")
Rel(config_loader, secret_manager, "Loads", "secure credentials")
Rel(secret_manager, flext_container, "Stores", "encrypted secrets")

@enduml
```

## Component Descriptions

### HTTP Client Components

#### HTTP Client Core
**Responsibilities**:
- Main client orchestration and lifecycle management
- Request routing to appropriate handlers
- Response aggregation and final result preparation
- Client configuration and initialization

**Key Classes**:
- `FlextApiClient` - Main client class
- `ClientLifecycleManager` - Client startup/shutdown
- `RequestDispatcher` - Request routing logic

#### Request Builder
**Responsibilities**:
- HTTP request construction from user parameters
- Request validation and normalization
- Header management and authentication token injection
- Request body serialization and content-type handling

**Key Classes**:
- `HttpRequestBuilder` - Request construction
- `RequestValidator` - Input validation
- `HeaderManager` - HTTP header handling

#### Response Handler
**Responsibilities**:
- HTTP response parsing and deserialization
- Response validation against expected schemas
- Error response handling and user-friendly error messages
- Response transformation and data extraction

**Key Classes**:
- `HttpResponseHandler` - Response processing
- `ResponseValidator` - Output validation
- `ErrorTranslator` - Error message formatting

#### Connection Pool
**Responsibilities**:
- HTTP connection lifecycle management
- Connection reuse and pooling optimization
- SSL/TLS connection handling
- Connection health monitoring and cleanup

**Key Classes**:
- `ConnectionPoolManager` - Pool management
- `SSLContextManager` - SSL configuration
- `ConnectionHealthChecker` - Health monitoring

#### Retry Logic
**Responsibilities**:
- Transient failure detection and retry decisions
- Exponential backoff calculation and timing
- Retry limit enforcement and circuit breaker patterns
- Retry metrics collection and monitoring

**Key Classes**:
- `RetryManager` - Retry orchestration
- `BackoffCalculator` - Timing calculations
- `CircuitBreaker` - Failure protection

#### Authentication Handler
**Responsibilities**:
- Authentication credential management and caching
- Token refresh and renewal automation
- Multi-authentication scheme support (JWT, API keys, OAuth)
- Authentication error handling and recovery

**Key Classes**:
- `AuthTokenManager` - Token lifecycle
- `CredentialStore` - Secure credential storage
- `AuthSchemeSelector` - Authentication method selection

### FastAPI Application Components

#### Application Factory
**Responsibilities**:
- FastAPI application instance creation and configuration
- Middleware stack assembly and ordering
- Route registration and validation
- Application lifecycle event handling

**Key Classes**:
- `FastApiAppFactory` - Application creation
- `MiddlewareAssembler` - Middleware configuration
- `RouteRegistrar` - Route registration

#### Route Registry
**Responsibilities**:
- API endpoint registration and metadata management
- Route validation and conflict detection
- OpenAPI specification generation
- Route performance monitoring and metrics

**Key Classes**:
- `RouteRegistry` - Route management
- `OpenApiGenerator` - API documentation
- `RouteValidator` - Route validation

#### Middleware Stack
**Responsibilities**:
- Request/response processing pipeline management
- Middleware ordering and dependency resolution
- Middleware configuration and parameter passing
- Pipeline performance monitoring

**Key Classes**:
- `MiddlewarePipeline` - Pipeline management
- `MiddlewareLoader` - Dynamic loading
- `PipelineMonitor` - Performance tracking

#### Error Formatter
**Responsibilities**:
- Exception catching and error response generation
- Error message sanitization and user-friendly formatting
- Error logging with appropriate detail levels
- Error response HTTP status code mapping

**Key Classes**:
- `ErrorResponseFormatter` - Response formatting
- `ExceptionHandler` - Exception processing
- `ErrorLogger` - Error logging

#### Health Checker
**Responsibilities**:
- Application health status assessment
- Dependency health checking (database, cache, external services)
- Readiness and liveness probe implementation
- Health metrics collection and reporting

**Key Classes**:
- `HealthCheckManager` - Health orchestration
- `DependencyChecker` - External dependency monitoring
- `MetricsCollector` - Health metrics

### Protocol Layer Components

#### Protocol Registry
**Responsibilities**:
- Protocol implementation discovery and registration
- Protocol capability negotiation and feature detection
- Protocol-specific client factory management
- Protocol performance monitoring and optimization

**Key Classes**:
- `ProtocolRegistry` - Registry management
- `ProtocolFactory` - Client creation
- `CapabilityNegotiator` - Feature negotiation

#### HTTP Protocol
**Responsibilities**:
- REST API client implementation with HTTP methods
- Content negotiation and media type handling
- HTTP status code interpretation and error mapping
- Request/response body serialization

**Key Classes**:
- `HttpProtocolClient` - HTTP operations
- `ContentNegotiator` - Media type handling
- `StatusCodeMapper` - HTTP status mapping

#### GraphQL Protocol
**Responsibilities**:
- GraphQL query and mutation execution
- Schema introspection and validation
- Variable binding and parameter handling
- Subscription support for real-time updates

**Key Classes**:
- `GraphQLClient` - Query execution
- `SchemaValidator` - Schema validation
- `SubscriptionManager` - Real-time subscriptions

#### WebSocket Protocol
**Responsibilities**:
- WebSocket connection establishment and management
- Message framing and encoding/decoding
- Heartbeat and ping/pong handling
- Connection lifecycle and error recovery

**Key Classes**:
- `WebSocketClient` - Connection management
- `MessageFramer` - Message processing
- `HeartbeatManager` - Connection health

#### SSE Protocol
**Responsibilities**:
- Server-Sent Events connection management
- Event stream parsing and event extraction
- Reconnection logic and failure recovery
- Event filtering and routing

**Key Classes**:
- `SSEClient` - Event stream handling
- `EventParser` - Event processing
- `ReconnectionManager` - Connection recovery

### Storage Layer Components

#### Storage Router
**Responsibilities**:
- Storage backend selection based on configuration and requirements
- Load balancing across multiple backend instances
- Failover handling and backend health monitoring
- Storage operation routing and optimization

**Key Classes**:
- `StorageRouter` - Backend routing
- `LoadBalancer` - Load distribution
- `HealthMonitor` - Backend monitoring

#### Cloud Storage Backends
**Responsibilities**:
- Cloud-specific API integration and authentication
- Object upload/download with multipart support
- Metadata management and tagging
- Access control and permission handling

**Key Classes**:
- `S3Backend` - AWS S3 operations
- `GCSBackend` - Google Cloud Storage
- `AzureBackend` - Azure Blob Storage

#### Local Backend
**Responsibilities**:
- Local filesystem operations with security constraints
- File permission management and access control
- Directory structure management and traversal
- Local file streaming and buffering

**Key Classes**:
- `LocalFileSystem` - Local operations
- `PermissionManager` - Access control
- `DirectoryManager` - Structure handling

### Configuration Layer Components

#### Config Loader
**Responsibilities**:
- Multi-source configuration loading (environment, files, secrets)
- Configuration format support (YAML, JSON, TOML, environment variables)
- Configuration precedence and override handling
- Configuration change detection and reloading

**Key Classes**:
- `ConfigFileLoader` - File-based loading
- `EnvironmentLoader` - Environment variables
- `SecretLoader` - Secure credential loading

#### Config Validator
**Responsibilities**:
- Configuration schema validation and type checking
- Cross-field validation and business rule enforcement
- Configuration completeness checking
- Validation error reporting and suggestions

**Key Classes**:
- `SchemaValidator` - Structure validation
- `BusinessRuleValidator` - Business logic validation
- `CompletenessChecker` - Required field validation

#### Secret Manager
**Responsibilities**:
- Secure credential storage and retrieval
- Encryption/decryption of sensitive configuration
- Secret rotation and expiration handling
- Integration with external secret management systems

**Key Classes**:
- `SecretStore` - Secure storage
- `EncryptionManager` - Data encryption
- `RotationManager` - Secret lifecycle

#### Config Watcher
**Responsibilities**:
- Configuration file change monitoring
- Hot-reload capability for configuration updates
- Configuration validation before applying changes
- Change notification and event emission

**Key Classes**:
- `FileWatcher` - File monitoring
- `ConfigReloader` - Hot reload logic
- `ChangeNotifier` - Event notification

## Component Interactions

### Request Processing Flow
1. **Client Core** receives user request
2. **Request Builder** validates and constructs HTTP request
3. **Authentication Handler** adds authentication credentials
4. **Connection Pool** provides connection for request
5. **Retry Logic** handles transient failures
6. **Response Handler** processes and validates response
7. **Client Core** returns final `FlextCore.Result[T]`

### Application Startup Flow
1. **Application Factory** creates FastAPI instance
2. **Config Layer** loads and validates configuration
3. **Route Registry** registers API endpoints
4. **Middleware Stack** configures processing pipeline
5. **Health Checker** sets up monitoring endpoints
6. **Application Factory** returns configured FastAPI app

### Storage Operation Flow
1. **Storage Router** selects appropriate backend
2. **Backend Component** executes storage operation
3. **Error handling** wraps operation in `FlextCore.Result[T]`
4. **Metrics collection** records operation performance
5. **Result** returned to calling component

## Quality Attributes Mapping

### Performance
- **Connection Pool**: Optimizes connection reuse and reduces latency
- **Retry Logic**: Implements efficient backoff strategies
- **Storage Router**: Enables load balancing and backend optimization

### Reliability
- **Error Formatter**: Provides consistent error handling across all operations
- **Health Checker**: Enables proactive failure detection and recovery
- **Retry Logic**: Implements resilient failure recovery patterns

### Security
- **Authentication Handler**: Centralizes secure credential management
- **Secret Manager**: Provides secure configuration handling
- **Config Validator**: Prevents misconfigurations that could create security issues

### Maintainability
- **Protocol Registry**: Enables easy addition of new protocol implementations
- **Middleware Stack**: Provides clean separation of cross-cutting concerns
- **Config Watcher**: Supports zero-downtime configuration updates

---

**Next Level**: [Code Diagram](code.md) - Implementation details and relationships
