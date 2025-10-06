# Getting Started with FLEXT-API

**HTTP and FastAPI Foundation for the FLEXT Ecosystem**

**Version**: 0.9.9 | **Last Updated**: October 5, 2025

This guide will help you get started with FLEXT-API, the HTTP client and FastAPI application foundation for the FLEXT enterprise data integration platform.

## 📋 Prerequisites

### **System Requirements**

- **Python**: 3.13+ (required for advanced type features)
- **Poetry**: Latest version for dependency management
- **FLEXT Workspace**: Must be part of the FLEXT ecosystem workspace

### **FLEXT Ecosystem Integration**

FLEXT-API requires integration with the core FLEXT libraries:

- **flext-core**: Foundation patterns and domain services
- **Python 3.13+**: Advanced type system and performance features
- **Poetry environment**: Workspace dependency management

## ⚙️ Installation

### **Option 1: FLEXT Workspace Setup (Recommended)**

If you're working within the FLEXT ecosystem:

```bash
# Navigate to flext-api directory
cd flext/flext-api

# Install with all development dependencies
poetry install --with dev,test,typings,security

# Set up development environment
make setup
```

### **Option 2: Standalone Installation**

For standalone usage:

```bash
# Install from PyPI
pip install flext-api

# Or install from source
git clone https://github.com/flext-sh/flext-api.git
cd flext-api
pip install -e .
```

### **Verification**

```bash
# Quick verification
python -c "from flext_api import FlextApiClient; print('✅ FLEXT-API ready')"

# Check version
python -c "from flext_api import __version__; print(f'FLEXT-API {__version__}')"
```

## 🚀 Quick Start

### 1. HTTP Client Usage

```python
from flext_api import FlextApiClient
from flext_core import FlextResult

# Create HTTP client
client = FlextApiClient(
    base_url="https://jsonplaceholder.typicode.com",
    timeout=10.0,
    headers={"User-Agent": "FLEXT-API/0.9.9"}
)

# Make HTTP requests with railway pattern
result = client.get("/users")
if result.is_success:
    users = result.unwrap()
    print(f"Found {len(users)} users")
else:
    print(f"Error: {result.error}")

# POST request
user_data = {"name": "John Doe", "email": "john@example.com"}
result = client.post("/users", json=user_data)
if result.is_success:
    new_user = result.unwrap()
    print(f"Created user: {new_user['name']}")
```

### 2. FastAPI Application

```python
from flext_api import create_fastapi_app, FlextApiConfig
from fastapi import FastAPI

# Create configuration
config = FlextApiConfig(
    title="My API",
    version="1.0.0",
    description="My awesome API built with FLEXT-API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create FastAPI application
app = create_fastapi_app(config=config)

# Define routes
@app.get("/users")
async def get_users():
    """Get list of users."""
    return {"users": [], "total": 0}

@app.post("/users")
async def create_user(user_data: dict):
    """Create new user."""
    return {"id": "user_123", **user_data}

# Run application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. Protocol-Based Architecture

FLEXT-API supports multiple protocols through a plugin architecture:

```python
# HTTP/REST APIs
from flext_api.protocol_impls.http import HttpProtocol

# GraphQL APIs
from flext_api.protocol_impls.graphql import GraphQLProtocol

# WebSocket connections
from flext_api.protocol_impls.websocket import WebSocketProtocol

# Server-sent events
from flext_api.protocol_impls.sse import ServerSentEventProtocol

# File storage
from flext_api.protocol_impls.storage_backend import StorageBackendProtocol
```

## 🏗️ Architecture Overview

FLEXT-API follows a clean, layered architecture with clear separation of concerns:

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

- **Railway Pattern**: All operations return `FlextResult[T]` for type-safe error handling
- **Dependency Injection**: `FlextContainer` for service management
- **Domain-Driven Design**: `FlextModels` for HTTP-specific entities
- **Protocol Abstraction**: Plugin architecture for multiple protocols

## 🔧 Configuration

### Environment-Based Configuration

FLEXT-API supports configuration through multiple sources:

```python
from flext_api import FlextApiConfig

# Create configuration for different environments
dev_config = FlextApiConfig.create_for_environment("development")
prod_config = FlextApiConfig.create_for_environment("production")

# Custom configuration
custom_config = FlextApiConfig(
    title="Custom API",
    version="2.0.0",
    debug=True,
    cors_origins=["http://localhost:3000"]
)
```

### Configuration Options

| Option         | Type | Default     | Description                 |
| -------------- | ---- | ----------- | --------------------------- |
| `title`        | str  | "FLEXT API" | API title for documentation |
| `version`      | str  | "0.9.9"     | API version                 |
| `description`  | str  | ""          | API description             |
| `docs_url`     | str  | "/docs"     | OpenAPI docs URL            |
| `redoc_url`    | str  | "/redoc"    | ReDoc URL                   |
| `cors_origins` | list | []          | CORS allowed origins        |
| `rate_limit`   | int  | 100         | Requests per minute limit   |

## 📚 Core Concepts

### Railway Pattern Integration

All FLEXT-API operations use the railway pattern for error handling:

```python
# HTTP operations always return FlextResult
result = client.get("/users/123")

# Type-safe success/failure handling
if result.is_success:
    user = result.unwrap()  # Safe extraction
    print(f"User: {user['name']}")
else:
    error = result.error    # Structured error information
    print(f"Failed: {error.message}")

# Railway composition for complex operations
def get_user_with_posts(user_id: str) -> FlextResult[dict]:
    return (
        client.get(f"/users/{user_id}")
        .flat_map(lambda user: client.get(f"/users/{user_id}/posts"))
        .map(lambda posts: {"user": user, "posts": posts})
        .map_error(lambda e: f"Failed to get user data: {e}")
    )
```

### Protocol Plugin System

FLEXT-API uses a protocol-based architecture for extensibility:

```python
from flext_api.protocols import ProtocolRegistry

# Register custom protocols
registry = ProtocolRegistry()
registry.register("my_protocol", MyCustomProtocol)

# Use protocols dynamically
protocol = registry.get_protocol("http")
client = protocol.create_client({"base_url": "https://api.example.com"})
```

## 🧪 Testing

### Testing HTTP Applications

FLEXT-API provides comprehensive testing utilities:

```python
import pytest
from flext_api.testing import FlextApiTestClient
from flext_core import FlextResult

class TestUserAPI:
    def setup_method(self):
        self.client = FlextApiTestClient(app)

    def test_get_users(self):
        """Test GET /users endpoint."""
        result = self.client.get("/users")

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 200

    def test_create_user(self):
        """Test POST /users endpoint."""
        user_data = {"name": "Test User", "email": "test@example.com"}
        result = self.client.post("/users", json=user_data)

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 201
        assert "id" in response.json()
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-e2e         # End-to-end tests only

# Run with coverage
make test-coverage

# Specific test files
pytest tests/unit/test_client.py -v
```

## 🔍 Debugging and Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Ensure flext-core is available
python -c "from flext_core import FlextResult; print('✅ Core available')"

# Check Python version
python --version  # Should be 3.13+
```

**2. Configuration Issues**

```bash
# Validate configuration loading
python -c "
from flext_api import FlextApiConfig
config = FlextApiConfig.create_for_environment('development')
print(f'Config loaded: {config.title}')
"
```

**3. HTTP Connection Issues**

```python
# Test connectivity
client = FlextApiClient(base_url="https://httpbin.org")
result = client.get("/get")

if result.is_failure:
    error = result.error
    print(f"Connection failed: {error.message}")
    print(f"Error code: {error.code}")
```

### Logging

FLEXT-API integrates with FLEXT-Core's structured logging:

```python
from flext_core import FlextLogger

logger = FlextLogger("flext_api_example")

# Log HTTP operations
logger.info("Making HTTP request", extra={
    "method": "GET",
    "url": "/users",
    "user_id": "user_123"
})

# Log errors with context
logger.error("HTTP request failed", extra={
    "error_code": "CONNECTION_TIMEOUT",
    "url": "/api/users",
    "timeout": 30.0
})
```

## 🚀 Next Steps

1. **Explore Examples**: Check `examples/` directory for working examples
2. **API Reference**: See [API Reference](../api-reference/) for complete documentation
3. **Protocol Guide**: Learn about supported protocols in [Protocols](../api-reference/protocols.md)
4. **Testing Guide**: See [Testing Guide](./testing.md) for comprehensive testing strategies
5. **Contributing**: See [Development Guide](../development/contributing.md) for contribution guidelines

## 📖 Related Documentation

- **[FLEXT-Core Documentation](../../flext-core/docs/)**: Foundation library documentation
- **[HTTP Client Guide](./http-client.md)**: Detailed HTTP client usage
- **[FastAPI Guide](./fastapi-apps.md)**: FastAPI application development
- **[Configuration Guide](./configuration.md)**: Configuration management
- **[Testing Guide](./testing.md)**: Testing strategies and patterns

---

**Ready to build HTTP applications with FLEXT-API!** 🚀
