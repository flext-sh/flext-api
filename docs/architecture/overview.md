# Architecture Overview

Comprehensive architecture guide for FLEXT-API - the HTTP client and FastAPI integration foundation for the FLEXT enterprise data integration platform.

## Overview

FLEXT-API follows a **Protocol-Based Clean Architecture** with clear separation of concerns across multiple layers, designed for extensibility and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│   (HTTP clients, FastAPI apps, protocol implementations)    │
│   FlextApiClient, create_fastapi_app, Protocol Classes      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│   (HTTP models, business logic, validation)                 │
│   FlextApiModels, HTTP-specific domain services             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Foundation Layer                          │
│   (Core patterns from flext-core)                           │
│   FlextResult, FlextContainer, FlextService, FlextModels   │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**

- **Protocol Abstraction**: Plugin architecture for multiple protocols
- **Railway Pattern**: All operations return `FlextResult[T]` for type-safe error handling
- **Dependency Injection**: `FlextContainer` for service management
- **Domain-Driven Design**: `FlextModels` for HTTP-specific entities

## Layer Details

### Foundation Layer (Core Primitives)

**Purpose**: Provide HTTP-specific abstractions built on FLEXT-Core foundation.

**Key Components:**

- **FlextApiClient**: HTTP client with railway pattern integration
- **FlextApiConfig**: Configuration management for API settings
- **FlextApiModels**: HTTP-specific models and validation
- **FlextApiUtilities**: HTTP utility functions and helpers

**Integration with FLEXT-Core:**

- Extends `FlextService` for domain service patterns
- Uses `FlextResult[T]` for error handling
- Integrates with `FlextContainer` for dependency injection
- Leverages `FlextModels` for entity modeling

### Domain Layer (HTTP Business Logic)

**Purpose**: Implement HTTP-specific business logic and domain models.

**Key Components:**

- **HTTP Models**: Request/response models with validation
- **Protocol Abstractions**: Abstract interfaces for different protocols
- **Validation Logic**: Business rule validation for HTTP operations
- **Error Handling**: HTTP-specific error types and handling

**Domain Patterns:**

```python
# HTTP-specific entity
class FlextWebEndpoint(FlextModels.Entity):
    """HTTP endpoint with routing and validation."""
    path: str
    method: str
    response_model: Type[BaseModel]
    middleware: List[Middleware]

# HTTP-specific domain service
class EndpointService(FlextService):
    """Domain service for HTTP endpoint management."""

    def validate_endpoint(self, endpoint: FlextWebEndpoint) -> FlextResult[None]:
        """Validate HTTP endpoint configuration."""
        if not endpoint.path.startswith("/"):
            return FlextResult[None].fail("Path must start with /")

        if endpoint.method not in ["GET", "POST", "PUT", "DELETE"]:
            return FlextResult[None].fail("Invalid HTTP method")

        return FlextResult[None].ok(None)
```

### Application Layer (Protocol Implementations)

**Purpose**: Implement specific protocols and coordinate between domain and infrastructure.

**Protocol Architecture:**

```
Protocol Layer
├── HTTP/REST (Primary)
│   ├── REST APIs
│   ├── CRUD operations
│   └── Standard HTTP methods
├── GraphQL (Query/Mutation)
│   ├── Query execution
│   ├── Schema validation
│   └── Variable handling
├── WebSocket (Real-time)
│   ├── Connection management
│   ├── Message routing
│   └── Heartbeat handling
├── Server-Sent Events (Streaming)
│   ├── Event streaming
│   └── Connection management
└── Storage Backend (File/Object)
    ├── Upload/download
    ├── Multiple backends
    └── Metadata management
```

**Key Components:**

- **FlextApiClient**: Main HTTP client implementation
- **create_fastapi_app()**: FastAPI application factory
- **Protocol Implementations**: HTTP, GraphQL, WebSocket, SSE, Storage
- **Middleware Pipeline**: Request/response processing chain

## Protocol Plugin System

### Protocol Registry

FLEXT-API uses a plugin system for protocol extensibility.

```python
from flext_api.protocols import ProtocolRegistry

# Register protocols
registry = ProtocolRegistry()
registry.register("http", FlextWebProtocol)
registry.register("graphql", GraphQLProtocol)
registry.register("websocket", WebSocketProtocol)

# Use protocols dynamically
http_protocol = registry.get_protocol("http")
client = http_protocol.create_client({"base_url": "https://api.example.com"})

# Add custom protocol
class CustomProtocol:
    def create_client(self, config: dict):
        return CustomClient(config)

registry.register("custom", CustomProtocol)
```

### Protocol Interface

```python
from abc import ABC, abstractmethod
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

class BaseProtocol(ABC):
    """Base protocol interface."""

    @abstractmethod
    def create_client(self, config: dict) -> object:
        """Create protocol-specific client."""
        pass

    @abstractmethod
    async def execute_request(self, request: object) -> FlextResult[object]:
        """Execute protocol-specific request."""
        pass

class FlextWebProtocol(BaseProtocol):
    """HTTP protocol implementation."""

    def create_client(self, config: dict) -> FlextApiClient:
        return FlextApiClient(**config)

    async def execute_request(self, request: FlextApiModels.HttpRequest) -> FlextResult[FlextApiModels.HttpResponse]:
        # HTTP-specific implementation
        pass
```

## HTTP Client Architecture

### FlextApiClient Design

The HTTP client follows a layered architecture for maximum flexibility and testability.

```
FlextApiClient
├── Request/Response Layer
│   ├── Request building
│   ├── Response parsing
│   └── Error handling
├── Transport Layer
│   ├── HTTP/1.1, HTTP/2
│   ├── Connection pooling
│   └── SSL/TLS handling
├── Authentication Layer
│   ├── JWT, API keys
│   ├── OAuth, Basic auth
│   └── Custom auth schemes
├── Middleware Layer
│   ├── Request interceptors
│   ├── Response processors
│   └── Error transformers
└── Protocol Layer
    ├── HTTP method dispatch
    ├── Content negotiation
    └── Header management
```

### Request Processing Pipeline

```python
# Request processing flow
@app.middleware("http")
async def request_pipeline(request, call_next):
    # 1. Authentication middleware
    auth_result = await auth_middleware.process_request(request)

    # 2. Validation middleware
    validation_result = await validation_middleware.process_request(request)

    # 3. Rate limiting middleware
    rate_limit_result = await rate_limit_middleware.process_request(request)

    # 4. Execute main handler
    response = await call_next(request)

    # 5. Response processing (reverse order)
    response = await rate_limit_middleware.process_response(request, response)
    response = await validation_middleware.process_response(request, response)
    response = await auth_middleware.process_response(request, response)

    return response
```

## FastAPI Integration Architecture

### Application Factory Pattern

```python
def create_fastapi_app(config: FlextApiConfig = None) -> FastAPI:
    """Create FastAPI application with FLEXT patterns."""


    # 2. Create FastAPI app
    app = FastAPI(
        title=config.title,
        version=config.version,
        description=config.description,
        docs_url=config.docs_url,
        redoc_url=config.redoc_url
    )

    # 3. Configure CORS
    if config.cors_origins:
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=config.cors_credentials,
            allow_methods=config.cors_methods,
            allow_headers=config.cors_headers,
        )

    # 4. Add FLEXT middleware
    app.add_middleware(LoggingMiddleware())
    app.add_middleware(AuthenticationMiddleware())
    app.add_middleware(ErrorHandlingMiddleware())

    # 5. Register routes
    register_health_routes(app)
    register_api_routes(app)

    return app
```

### Route Registration

```python
def register_api_routes(app: FastAPI):
    """Register API routes with FLEXT patterns."""

    # User routes
    @app.get("/users", response_model=List[UserResponse])
    async def list_users(
        limit: int = 10,
        offset: int = 0,
        current_user: dict[str, object] = Depends(get_current_user)
    ) -> List[UserResponse]:
        """List users with pagination."""
        result = await user_service.get_users(limit=limit, offset=offset)

        if result.is_failure:
            raise HTTPException(status_code=500, detail=result.error)

        users = result.unwrap()
        return [UserResponse.from_entity(user) for user in users]

    # Error handling
    @app.exception_handler(FlextException)
    async def flext_exception_handler(request: Request, exc: FlextException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        )
```

## Storage Architecture

### Multi-Backend Storage

FLEXT-API supports multiple storage backends through a unified interface.

```
Storage Layer
├── Local Filesystem
│   ├── File upload/download
│   ├── Directory management
│   └── Metadata handling
├── Amazon S3
│   ├── Bucket operations
│   ├── CDN integration
│   └── Access control
├── Google Cloud Storage
│   ├── Project integration
│   └── Service account auth
├── Azure Blob Storage
│   ├── Container management
│   └── SAS token auth
└── Multi-Backend Strategy
    ├── Failover support
    ├── Load balancing
    └── Health monitoring
```

### Storage Interface

```python
class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    async def upload_file(self, file: object, path: str, metadata: dict[str, object] = None) -> FlextResult[str]:
        """Upload file to storage."""
        pass

    @abstractmethod
    async def download_file(self, path: str) -> FlextResult[bytes]:
        """Download file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> FlextResult[None]:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def list_files(self, prefix: str = "") -> FlextResult[List[FileInfo]]:
        """List files in storage."""
        pass

class S3StorageBackend(StorageBackend):
    """Amazon S3 storage implementation."""

    def __init__(self, config: dict):
        self.client = boto3.client("s3", **config)

    async def upload_file(self, file: object, path: str, metadata: dict[str, object] = None) -> FlextResult[str]:
        """Upload file to S3."""
        try:
            # S3 upload implementation
            self.client.upload_fileobj(file, self.bucket, path, ExtraArgs={
                'Metadata': metadata or {}
            })
            return FlextResult[str].ok(f"s3://{self.bucket}/{path}")
        except Exception as e:
            return FlextResult[str].fail(f"S3 upload failed: {e}")
```

## Caching Architecture

### Multi-Level Caching

FLEXT-API implements multi-level caching for optimal performance.

```
Caching Strategy
├── Application Cache (FastAPI)
│   ├── Response caching
│   ├── Template caching
│   └── Session storage
├── HTTP Cache (httpx)
│   ├── Connection reuse
│   ├── Response caching
│   └── ETag/Last-Modified
├── External Cache (Redis/Memcached)
│   ├── API response caching
│   ├── Database query results
│   └── Static asset caching
└── CDN Cache (CloudFront/CloudFlare)
    ├── Static asset delivery
    ├── Edge caching
    └── Global distribution
```

### Cache Configuration

```python
from flext_api.storage import FlextApiCache

# Redis cache configuration
redis_cache = FlextApiCache(
    backend="redis",
    config={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": os.getenv("REDIS_PASSWORD"),
        "decode_responses": True
    }
)

# Memory cache for development
memory_cache = FlextApiCache(
    backend="memory",
    config={
        "max_size": 1000,  # Max cached items
        "ttl": 300         # Default TTL in seconds
    }
)

# File-based cache for persistence
file_cache = FlextApiCache(
    backend="filesystem",
    config={
        "cache_dir": "/tmp/flext-cache",
        "max_size": 100 * 1024 * 1024,  # 100MB
        "cleanup_interval": 3600        # Cleanup every hour
    }
)
```

## Security Architecture

### Authentication and Authorization

FLEXT-API implements comprehensive security measures.

```
Security Layer
├── Authentication
│   ├── JWT tokens
│   ├── API keys
│   ├── OAuth 2.0
│   └── Custom schemes
├── Authorization
│   ├── Role-based access
│   ├── Permission-based access
│   └── Resource-based access
├── Input Validation
│   ├── Schema validation
│   ├── SQL injection prevention
│   └── XSS protection
├── Transport Security
│   ├── TLS/SSL encryption
│   ├── Certificate validation
│   └── Secure headers
└── Audit Logging
    ├── Request/response logging
    ├── Security event logging
    └── Compliance reporting
```

### Security Middleware

```python
from flext_api.middleware import SecurityMiddleware

class ComprehensiveSecurityMiddleware(SecurityMiddleware):
    """Comprehensive security middleware."""

    async def process_request(self, request) -> FlextResult[dict]:
        """Apply security checks to request."""

        # 1. Rate limiting
        rate_limit_result = await self.check_rate_limit(request)
        if rate_limit_result.is_failure:
            return rate_limit_result

        # 2. Input validation
        validation_result = await self.validate_request(request)
        if validation_result.is_failure:
            return validation_result

        # 3. Authentication
        auth_result = await self.authenticate_request(request)
        if auth_result.is_failure:
            return auth_result

        # 4. Authorization
        authz_result = await self.authorize_request(request)
        if authz_result.is_failure:
            return authz_result

        return FlextResult[dict].ok({})

    async def check_rate_limit(self, request) -> FlextResult[dict]:
        """Check rate limiting."""
        client_ip = self.get_client_ip(request)
        endpoint = f"{request.method} {request.path}"

        # Check rate limit for this client/endpoint
        current_count = self.rate_limiter.get_count(client_ip, endpoint)

        if current_count > self.max_requests_per_minute:
            return FlextResult[dict].fail("Rate limit exceeded")

        return FlextResult[dict].ok({})

    async def validate_request(self, request) -> FlextResult[dict]:
        """Validate request data."""
        # Validate request size
        if self.get_request_size(request) > self.max_request_size:
            return FlextResult[dict].fail("Request too large")

        # Validate content type
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            if not self.is_valid_content_type(content_type):
                return FlextResult[dict].fail("Invalid content type")

        return FlextResult[dict].ok({})
```

## Performance Architecture

### Performance Optimization Strategies

FLEXT-API implements multiple performance optimization techniques.

```
Performance Layer
├── Connection Optimization
│   ├── HTTP/2 support
│   ├── Connection pooling
│   └── Keep-alive handling
├── Caching Strategy
│   ├── Response caching
│   ├── Static asset caching
│   └── Database query caching
├── Async Processing
│   ├── Async HTTP clients
│   ├── Background tasks
│   └── Event-driven processing
├── Resource Management
│   ├── Memory pooling
│   ├── File handle management
│   └── Database connection pooling
└── Monitoring
    ├── Performance metrics
    ├── Error tracking
    └── Health checks
```

### Performance Monitoring

```python
from flext_api.middleware import PerformanceMonitoringMiddleware

class DetailedPerformanceMiddleware(PerformanceMonitoringMiddleware):
    """Detailed performance monitoring."""

    def __init__(self, metrics_client):
        self.metrics_client = metrics_client

    async def process_request(self, request) -> FlextResult[dict]:
        """Start performance monitoring."""
        request.start_time = time.time()
        request.request_id = str(uuid.uuid4())

        # Record request start
        self.metrics_client.record_request_start(
            request_id=request.request_id,
            method=request.method,
            path=request.path,
            user_agent=request.headers.get("User-Agent")
        )

        return FlextResult[dict].ok({})

    async def process_response(self, request, response) -> FlextResult[dict]:
        """Record performance metrics."""
        duration_ms = (time.time() - request.start_time) * 1000

        # Record request completion
        self.metrics_client.record_request_complete(
            request_id=request.request_id,
            status_code=response.status_code,
            duration_ms=duration_ms,
            response_size=len(response.content) if response.content else 0
        )

        # Add performance headers
        response.headers.update({
            "X-Response-Time": f"{duration_ms:.2f}ms",
            "X-Request-ID": request.request_id
        })

        # Check for slow requests
        if duration_ms > 1000:  # 1 second threshold
            self.logger.warning("Slow request detected", extra={
                "request_id": request.request_id,
                "duration_ms": duration_ms,
                "path": request.path,
                "method": request.method
            })

        return FlextResult[dict].ok({})
```

## Deployment Architecture

### Container Architecture

FLEXT-API applications are designed for containerized deployment.

```
Container Layer
├── Application Container
│   ├── FastAPI application
│   ├── HTTP client instances
│   └── Configuration management
├── Sidecar Containers
│   ├── Redis cache
│   ├── Database proxy
│   └── Monitoring agent
├── Infrastructure
│   ├── Load balancer
│   ├── Service mesh
│   └── Ingress controller
└── External Services
    ├── Database clusters
    ├── Message queues
    └── Monitoring systems
```

### Deployment Configuration

```python
# Docker configuration
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flext-api
  template:
    metadata:
      labels:
        app: flext-api
    spec:
      containers:
        - name: flext-api
          image: flext-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: url
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

## Quality Metrics

### Current State (v0.9.9)

| Metric              | Value | Target (1.0.0) | Status         |
| ------------------- | ----- | -------------- | -------------- |
| **Test Coverage**   | 85%   | 90%+           | 🔄 Improving   |
| **Total Tests**     | 334   | 400+           | 🔄 In Progress |
| **Ruff Violations** | 0     | 0              | ✅ Complete    |
| **Type Errors**     | 0     | 0              | ✅ Complete    |
| **Modules**         | 25    | 25 (stable)    | ✅ Complete    |

### Coverage by Layer

| Layer           | Coverage | Status       | Description                    |
| --------------- | -------- | ------------ | ------------------------------ |
| **Foundation**  | 90%+     | ✅ Excellent | Core HTTP client and utilities |
| **Domain**      | 80-85%   | ✅ Good      | HTTP models and validation     |
| **Application** | 85-90%   | ✅ Good      | Protocol implementations       |
| **Storage**     | 80-85%   | ✅ Good      | File storage and caching       |

## Extension Points

### Adding New Protocols

```python
from flext_api.protocols import BaseProtocol

class CustomProtocol(BaseProtocol):
    """Custom protocol implementation."""

    def create_client(self, config: dict) -> object:
        """Create protocol-specific client."""
        return CustomClient(**config)

    async def execute_request(self, request: object) -> FlextResult[object]:
        """Execute protocol-specific request."""
        # Custom protocol implementation
        pass

# Register new protocol
registry = ProtocolRegistry()
registry.register("custom", CustomProtocol)
```

### Custom Middleware

```python
from flext_api.middleware import FlextApiMiddleware

class CustomBusinessMiddleware(FlextApiMiddleware):
    """Custom middleware for business logic."""

    async def process_request(self, request) -> FlextResult[dict]:
        """Add business context to request."""
        # Add business-specific headers
        request.business_context = {
            "tenant_id": request.headers.get("X-Tenant-ID"),
            "user_role": request.headers.get("X-User-Role")
        }

        return FlextResult[dict].ok({})

# Register middleware
app.add_middleware(CustomBusinessMiddleware())
```

## Performance Considerations

### Bottlenecks and Optimization

**1. HTTP Client Performance**

- Connection pooling (httpx default: 100 connections)
- HTTP/2 support for multiplexing
- Request/response compression
- DNS caching

**2. FastAPI Performance**

- Async request handling
- Pydantic model validation optimization
- Response serialization caching
- Middleware pipeline efficiency

**3. Storage Performance**

- CDN integration for static assets
- Database connection pooling
- File upload streaming
- Cache hit rate optimization

### Monitoring and Optimization

```python
# Performance monitoring setup
@app.on_event("startup")
async def setup_monitoring():
    # Setup metrics collection
    metrics.setup(
        namespace="flext_api",
        subsystem="http"
    )

    # Setup tracing
    tracer.setup(service_name="flext-api")

# Performance metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=metrics.generate_latest(),
        media_type="text/plain"
    )
```

## Migration Guidelines

### Version Compatibility

FLEXT-API maintains backward compatibility through semantic versioning.

**Breaking Changes Process:**

1. Mark as deprecated in current version
2. Provide migration guide and warnings
3. Remove in next major version (2.0.0)
4. Update ecosystem documentation

**Migration Example:**

```python
# Old API (deprecated in 0.9.x)
@deprecated("Use create_fastapi_app() instead")
def create_app(config: dict) -> FastAPI:
    # Legacy implementation

# New API (introduced in 0.9.x)
def create_fastapi_app(config: FlextApiConfig = None) -> FastAPI:
    """Create FastAPI application with FLEXT patterns."""
    # New implementation
```

## References

- **FLEXT-Core Documentation**: Foundation patterns and infrastructure
- **Clean Architecture**: Robert C. Martin architectural principles
- **FastAPI Documentation**: Web framework patterns and best practices
- **HTTP Specifications**: RFC standards for HTTP/1.1 and HTTP/2

---

**FLEXT-API Architecture** - Protocol-based, extensible HTTP foundation for enterprise applications.
