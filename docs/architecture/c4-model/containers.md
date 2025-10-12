# C4 Model - Containers

## Overview

This document describes the **Container** level of the C4 model for FLEXT-API, showing the high-level technology choices and how responsibilities are distributed across containers.

## Container Diagram

```plantuml
@startuml FLEXT-API Containers
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title FLEXT-API Container Diagram

Person(developer, "Application Developer", "Python developer using FLEXT-API")
Person(end_user, "End User", "Uses FLEXT-API based applications")

System_Boundary(flext_api_system, "FLEXT-API System") {
    Container(api_client, "HTTP Client Container", "Python/FastAPI", "Enterprise HTTP client with connection pooling, retry logic, and railway error handling")
    Container(fastapi_app, "FastAPI Application Container", "Python/FastAPI", "Web API server with middleware, routing, and request processing")
    Container(protocol_layer, "Protocol Layer Container", "Python", "Protocol abstractions for HTTP, GraphQL, WebSocket, SSE, and custom protocols")
    Container(storage_layer, "Storage Layer Container", "Python", "Multi-backend file storage with S3, GCS, Azure, and local filesystem support")
    Container(config_layer, "Configuration Layer", "Python/Pydantic", "Environment-aware configuration management with validation")
}

System_Boundary(flext_core_system, "FLEXT-Core Foundation") {
    Container(flext_core, "FLEXT-Core Library", "Python", "Foundation patterns: FlextCore.Result, FlextCore.Container, FlextCore.Models, FlextCore.Logger")
}

System_Ext(httpx_lib, "HTTPX Library", "Python HTTP library")
System_Ext(fastapi_lib, "FastAPI Framework", "Python web framework")
System_Ext(pydantic_lib, "Pydantic Library", "Python data validation")
System_Ext(orjson_lib, "orjson Library", "Python JSON processing")
System_Ext(websockets_lib, "websockets Library", "Python WebSocket library")

System_Ext(ldap_server, "LDAP Directory", "User authentication")
System_Ext(database, "Database", "Data persistence")
System_Ext(message_queue, "Message Queue", "Async communication")
System_Ext(storage_backend, "Storage Backend", "File/object storage")
System_Ext(external_api, "External API", "Third-party services")

Rel(developer, api_client, "Configures and uses", "Python imports")
Rel(developer, fastapi_app, "Deploys and configures", "Python code")
Rel(end_user, fastapi_app, "Makes HTTP requests", "REST/HTTP")

Rel(api_client, flext_core, "Uses patterns from", "imports")
Rel(fastapi_app, flext_core, "Uses patterns from", "imports")
Rel(protocol_layer, flext_core, "Extends patterns", "inheritance")
Rel(storage_layer, flext_core, "Uses patterns from", "imports")
Rel(config_layer, flext_core, "Uses patterns from", "imports")

Rel(api_client, httpx_lib, "Uses for HTTP", "library calls")
Rel(fastapi_app, fastapi_lib, "Built on", "framework")
Rel(config_layer, pydantic_lib, "Uses for validation", "library calls")
Rel(fastapi_app, orjson_lib, "Uses for JSON", "serialization")
Rel(protocol_layer, websockets_lib, "Uses for WebSocket", "protocol")

Rel(api_client, ldap_server, "Authenticates", "LDAP")
Rel(api_client, database, "Queries", "SQL/JDBC")
Rel(api_client, message_queue, "Publishes/subscribes", "AMQP")
Rel(api_client, storage_backend, "Uploads/downloads", "HTTP/S3")
Rel(api_client, external_api, "Makes requests", "REST")

Rel(fastapi_app, api_client, "Uses internally", "library calls")
Rel(fastapi_app, protocol_layer, "Routes to", "protocol dispatch")
Rel(fastapi_app, storage_layer, "Handles files", "storage operations")
Rel(fastapi_app, config_layer, "Reads configuration", "config loading")

@enduml
```

## Container Descriptions

### HTTP Client Container

**Technology**: Python with HTTPX and FastAPI
**Responsibilities**:

- Enterprise-grade HTTP client operations
- Connection pooling and lifecycle management
- Automatic retry logic with exponential backoff
- Request/response transformation and validation
- Authentication and authorization handling
- Error handling with railway pattern

**Key Interfaces**:

- `FlextApiClient` - Main HTTP client class
- Request/response model validation
- Connection pool management
- Retry and timeout configuration

### FastAPI Application Container

**Technology**: Python with FastAPI framework
**Responsibilities**:

- Web API server with automatic OpenAPI generation
- Request routing and middleware processing
- Response serialization and formatting
- Health check and metrics endpoints
- CORS and security headers management

**Key Interfaces**:

- `create_fastapi_app()` - Application factory function
- Middleware pipeline integration
- Route registration and validation
- Error response formatting

### Protocol Layer Container

**Technology**: Python with protocol abstractions
**Responsibilities**:

- Multi-protocol support (HTTP, GraphQL, WebSocket, SSE)
- Protocol-specific client implementations
- Message format translation and validation
- Protocol negotiation and capability detection

**Key Interfaces**:

- Protocol registry and discovery
- Protocol-specific client factories
- Message serialization/deserialization
- Protocol capability negotiation

### Storage Layer Container

**Technology**: Python with multi-backend support
**Responsibilities**:

- Multi-cloud storage abstraction (S3, GCS, Azure)
- Local filesystem operations
- File upload/download with streaming
- Metadata management and validation
- Storage backend failover and load balancing

**Key Interfaces**:

- Storage backend registry
- File operation abstractions
- Upload/download progress tracking
- Storage configuration validation

### Configuration Layer Container

**Technology**: Python with Pydantic validation
**Responsibilities**:

- Environment-aware configuration loading
- Configuration validation and type safety
- Secret management integration
- Configuration hot-reloading support

**Key Interfaces**:

- Configuration model definitions
- Environment variable parsing
- Configuration validation rules
- Runtime configuration updates

## Technology Choices

### Core Technologies

| Component           | Technology  | Justification                                        |
| ------------------- | ----------- | ---------------------------------------------------- |
| **HTTP Client**     | HTTPX       | Modern async HTTP client with excellent performance  |
| **Web Framework**   | FastAPI     | High-performance async API framework with auto-docs  |
| **Data Validation** | Pydantic v2 | Type-safe data validation with excellent performance |
| **JSON Processing** | orjson      | Fastest JSON library for Python                      |
| **WebSocket**       | websockets  | Mature WebSocket library for real-time communication |
| **GraphQL**         | gql         | Comprehensive GraphQL client library                 |

### Infrastructure Dependencies

| Dependency     | Purpose             | Version Constraint |
| -------------- | ------------------- | ------------------ |
| **flext-core** | Foundation patterns | file:../flext-core |
| **httpx**      | HTTP client         | >=0.28.1           |
| **fastapi**    | Web framework       | >=0.116.0          |
| **pydantic**   | Data validation     | >=2.10.0           |
| **websockets** | WebSocket protocol  | >=15.0.1           |
| **gql**        | GraphQL client      | >=4.0.0            |

## Deployment Considerations

### Container Packaging

```dockerfile
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false
RUN poetry install --only=main --no-dev

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from flext_api import FlextApiClient; print('OK')"

# Start application
CMD ["python", "-m", "flext_api.app"]
```

### Environment Configuration

```yaml
# Production configuration
environment: production
log_level: WARNING

# HTTP client configuration
http_client:
  timeout: 30.0
  max_connections: 100
  retry_attempts: 3

# FastAPI configuration
fastapi:
  host: 0.0.0.0
  port: 8000
  workers: 4

# Storage configuration
storage:
  backend: s3
  bucket: flext-api-storage
  region: us-east-1

# Database configuration
database:
  url: postgresql://user:pass@host:5432/db
  pool_size: 10
  max_overflow: 20
```

## Quality Attributes

### Performance

- **HTTP Client**: Connection pooling, HTTP/2 support, async operations
- **FastAPI**: Async request handling, optimized serialization
- **Storage**: Streaming uploads/downloads, CDN integration

### Reliability

- **Error Handling**: Railway pattern throughout all operations
- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breakers**: Protection against cascading failures
- **Health Checks**: Comprehensive system health monitoring

### Security

- **Authentication**: JWT, API keys, OAuth support
- **Authorization**: Role-based and permission-based access control
- **Transport Security**: TLS/SSL encryption, certificate validation
- **Input Validation**: Comprehensive request/response validation

### Maintainability

- **Clean Architecture**: Clear separation of concerns
- **Type Safety**: Full type annotations with runtime checking
- **Documentation**: Comprehensive API and architecture documentation
- **Testing**: High test coverage with automated testing

## Monitoring and Observability

### Metrics Collection

- **HTTP Metrics**: Request count, latency, error rates
- **Performance Metrics**: Memory usage, CPU utilization, response times
- **Business Metrics**: API usage patterns, user behavior
- **System Metrics**: Disk usage, network I/O, database connections

### Logging Strategy

- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging with search capabilities
- **Security Logging**: Audit trails for sensitive operations

### Health Checks

- **Application Health**: Service availability and responsiveness
- **Dependency Health**: Database, cache, external service connectivity
- **Performance Health**: Response time thresholds and error rates
- **Business Health**: Critical business logic validation

---

**Next Level**: [Component Diagram](components.md) - Detailed component relationships
