# Architecture Overview







<!-- TOC START -->
- [Overview](#overview)
- [Layer Details](#layer-details)
  - [Foundation Layer (Core Primitives)](#foundation-layer-core-primitives)
  - [Domain Layer (HTTP Business Logic)](#domain-layer-http-business-logic)
- [Protocol Plugin System](#protocol-plugin-system)
  - [Protocol Registry](#protocol-registry)
  - [Request Processing Pipeline](#request-processing-pipeline)
  - [Storage Interface](#storage-interface)
  - [Cache Configuration](#cache-configuration)
  - [Security Middleware](#security-middleware)
  - [Performance Monitoring](#performance-monitoring)
  - [Deployment Configuration](#deployment-configuration)
  - [Kubernetes Deployment](#kubernetes-deployment)
- [Quality Metrics](#quality-metrics)
  - [Current State (v0.12.0-dev)](#current-state-v0120-dev)
  - [Coverage by Layer](#coverage-by-layer)
- [Extension Points](#extension-points)
  - [Adding New Protocols](#adding-new-protocols)
  - [Custom Middleware](#custom-middleware)
- [Performance Considerations](#performance-considerations)
  - [Bottlenecks and Optimization](#bottlenecks-and-optimization)
  - [Monitoring and Optimization](#monitoring-and-optimization)
- [Migration Guidelines](#migration-guidelines)
  - [Version Compatibility](#version-compatibility)
- [References](#references)
<!-- TOC END -->

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
│   r, FlextContainer, s, FlextModels   │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**

- **Protocol Abstraction**: Plugin architecture for multiple protocols
- **Railway Pattern**: All operations return `r[T]` for type-safe error handling
- **Dependency Injection**: `FlextContainer` for service management
- **Domain-Driven Design**: `FlextModels` for HTTP-specific entities

## Layer Details

### Foundation Layer (Core Primitives)

**Purpose**: Provide HTTP-specific abstractions built on FLEXT-Core foundation.

**Key Components:**

- **FlextApiClient**: HTTP client with railway pattern integration
- **FlextApiSettings**: Configuration management for API settings
- **FlextApiModels**: HTTP-specific models and validation
- **FlextApiUtilities**: HTTP utility functions and helpers

**Integration with FLEXT-Core:**

- Extends `s` for domain service patterns
- Uses `r[T]` for error handling
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
```

### Request Processing Pipeline

```python
```

### Storage Interface

```python
```

### Cache Configuration

```python
```

### Security Middleware

```python
```

### Performance Monitoring

```python
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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]```
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
            periodSeconds: 5```
## Quality Metrics

### Current State (v0.12.0-dev)

| Metric              | Value | Target (1.0.0) | Status        |
| ------------------- | ----- | -------------- | ------------- |
| **Test Coverage**   | 85%   | 90%+           | 🔄 Improving   |
| **Total Tests**     | 334   | 400+           | 🔄 In Progress |
| **Ruff Violations** | 0     | 0              | ✅ Complete    |
| **Type Errors**     | 0     | 0              | ✅ Complete    |
| **Modules**         | 25    | 25 (stable)    | ✅ Complete    |

### Coverage by Layer

| Layer           | Coverage | Status      | Description                    |
| --------------- | -------- | ----------- | ------------------------------ |
| **Foundation**  | 90%+     | ✅ Excellent | Core HTTP client and utilities |
| **Domain**      | 80-85%   | ✅ Good      | HTTP models and validation     |
| **Application** | 85-90%   | ✅ Good      | Protocol implementations       |
| **Storage**     | 80-85%   | ✅ Good      | File storage and caching       |

## Extension Points

### Adding New Protocols

```python
from flext_api import Base


class CustomBase
    """Custom protocol implementation."""

    def create_client(self, settings: dict):
        """Create protocol-specific client."""
        return CustomClient(**settings)

    async def execute_request(self, request) -> p.Result[t.JsonValue]:
        """Execute protocol-specific request."""
        # Custom protocol implementation
        pass


# Register new protocol
registry = ProtocolRegistry()
registry.register("custom", Custom```
### Custom Middleware

```python
from flext_api import FlextApiMiddleware


class CustomBusinessMiddleware(FlextApiMiddleware):
    """Custom middleware for business logic."""

    async def process_request(self, request) -> p.Result[dict]:
        """Add business context to request."""
        # Add business-specific headers
        request.business_context = {
            "tenant_id": request.headers.get("X-Tenant-ID"),
            "user_role": request.headers.get("X-User-Role"),
        }

        return r[dict].ok({})


# Register middleware
app.add_middleware(CustomBusinessMiddleware())```
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
    metrics.setup(namespace="flext_api", subsystem="http")

    # Setup tracing
    tracer.setup(service_name="flext-api")


# Performance metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(content=metrics.generate_latest(), media_type="text/plain")```
## Migration Guidelines

### Version Compatibility

FLEXT-API maintains backward compatibility through semantic versioning.

**Breaking Changes Process:**

1. Mark as deprecated in current version
1. Provide migration guide and warnings
1. Remove in next major version (2.0.0)
1. Update ecosystem documentation

**Migration Example:**

```python
# Old API (deprecated in 0.9.x)
@deprecated("Use create_fastapi_app() instead")
def create_app(settings: dict) -> FastAPI:
    # Legacy implementation

# New API (introduced in 0.9.x)
def create_fastapi_app(settings: FlextApiSettings = None) -> FastAPI:
    """Create FastAPI application with FLEXT patterns."""
    # New implementation```
## References

- **FLEXT-Core Documentation**: Foundation patterns and infrastructure
- **Clean Architecture**: Robert C. Martin architectural principles
- **FastAPI Documentation**: Web framework patterns and best practices
- **HTTP Specifications**: RFC standards for HTTP/1.1 and HTTP/2

______________________________________________________________________

**FLEXT-API Architecture** - Protocol-based, extensible HTTP foundation for enterprise applications.
