# FLEXT-API Documentation

**Professional Documentation | Status: Production Ready | Version: 0.9.9 | Last Updated: 2025-10-05**

This comprehensive documentation covers FLEXT-API, the HTTP client and FastAPI integration foundation for the FLEXT enterprise data integration platform.

## Documentation Structure

```
docs/
├── README.md                 # This file - documentation overview
├── api-reference/           # Complete API reference
│   ├── core.md             # Core HTTP client and server classes
│   ├── protocols.md        # Protocol implementations and stubs
│   ├── schemas.md          # OpenAPI, AsyncAPI, and JSON Schema
│   ├── middleware.md       # HTTP middleware and handlers
│   └── storage.md          # HTTP storage and caching
├── guides/                 # User and developer guides
│   ├── getting-started.md  # Installation and quick start
│   ├── http-client.md      # HTTP client usage patterns
│   ├── fastapi-apps.md     # FastAPI application development
│   ├── configuration.md    # Configuration management
│   ├── testing.md          # Testing HTTP applications
│   └── troubleshooting.md  # Common issues and solutions
├── architecture/           # Architecture and design
│   ├── overview.md         # High-level architecture
│   ├── http-patterns.md    # HTTP design patterns
│   ├── integration.md      # FLEXT ecosystem integration
│   └── decisions.md        # Architecture decision records
├── development/            # Development workflow
│   ├── contributing.md     # How to contribute
│   ├── standards.md        # Development standards
│   ├── workflow.md         # Development workflow
│   └── quality.md          # Quality assurance processes
└── standards/              # Standards and guidelines
    ├── http.md             # HTTP API standards
    ├── fastapi.md          # FastAPI development standards
    └── integration.md      # Integration standards
```

## Quick Start

### Installation

```bash
# Clone and setup (recommended)
git clone https://github.com/flext-sh/flext-api.git
cd flext-api
make setup

# Or install from PyPI
pip install flext-api

# Verify installation
python -c "from flext_api import FlextApiClient; print('✅ FLEXT-API ready')"
```

### Basic Usage

```python
from flext_api import FlextApiClient
from flext_core import FlextResult

# Create HTTP client
client = FlextApiClient(base_url="https://api.example.com")

# Make requests with railway pattern
result = client.get("/users")
if result.is_success:
    users = result.unwrap()
    print(f"Found {len(users)} users")
else:
    print(f"Error: {result.error}")

# Create FastAPI application
from flext_api import create_fastapi_app

app = create_fastapi_app(
    title="My API",
    version="1.0.0",
    description="My awesome API"
)
```

## Core Concepts

### 1. HTTP Client with Railway Pattern

FLEXT-API provides type-safe HTTP operations with error handling:

```python
# HTTP client with automatic error handling
client = FlextApiClient()

# All operations return FlextResult[T]
result = client.post("/users", json={"name": "Alice", "email": "alice@example.com"})

if result.is_success:
    user = result.unwrap()
    print(f"Created user: {user['name']}")
else:
    print(f"Failed: {result.error}")
```

### 2. FastAPI Application Factory

Create FastAPI applications with FLEXT patterns:

```python
from flext_api import create_fastapi_app, FlextApiConfig

# Configure your API
config = FlextApiConfig(
    title="Enterprise API",
    version="2.0.0",
    description="Enterprise-grade REST API"
)

# Create application
app = create_fastapi_app(config=config)

# Add routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

### 3. Protocol-Based Architecture

Multiple protocol support through plugin architecture:

```python
# HTTP/REST APIs
from flext_api.protocol_impls.http import HttpProtocol

# GraphQL APIs
from flext_api.protocol_impls.graphql import GraphQLProtocol

# WebSocket connections
from flext_api.protocol_impls.websocket import WebSocketProtocol

# Server-sent events
from flext_api.protocol_impls.sse import ServerSentEventProtocol
```

## Quality Standards

- **Zero Ruff Violations**: Code quality enforced
- **Zero MyPy Errors**: Type safety guaranteed
- **100% Test Coverage**: Comprehensive testing
- **Python 3.13+**: Modern Python features
- **FLEXT-Core Integration**: Consistent patterns across ecosystem

## Getting Help

- **[API Reference](./api-reference/)**: Complete API documentation
- **[GitHub Issues](https://github.com/flext-sh/flext-api/issues)**: Report bugs or request features
- **[GitHub Discussions](https://github.com/flext-sh/flext-api/discussions)**: Ask questions and share ideas

## Contributing

See [Contributing Guide](./development/contributing.md) for development guidelines and workflow.

---

**FLEXT-API v0.9.9** - HTTP client and FastAPI integration foundation for enterprise Python applications.
