# FLEXT-API

<!-- TOC START -->

- [🚀 Overview](#overview)
  - [🎯 Core Features](#core-features)
  - [🏢 Integration with FLEXT Ecosystem](#integration-with-flext-ecosystem)
- [🏗️ Current Source Structure](#current-source-structure)
  - [🎯 Key Architectural Patterns](#key-architectural-patterns)
- [📚 Documentation Structure](#documentation-structure)
  - [🏗️ Architecture & Design](#architecture-design)
  - [🔧 Development & Integration](#development-integration)
- [🚀 Quick Start](#quick-start)
  - [Installation](#installation)
  - [Basic HTTP Client Usage](#basic-http-client-usage)
  - [FastAPI Application Setup](#fastapi-application-setup)
- [🧪 Testing](#testing)
- [📈 Current Status](#current-status)
  - [🎯 Production Readiness](#production-readiness)
- [🤝 Contributing](#contributing)
- [📋 Roadmap](#roadmap)
  - [Immediate (Next Release)](#immediate-next-release)
  - [Short-term (Next Month)](#short-term-next-month)
  - [Long-term (Next Quarter)](#long-term-next-quarter)

<!-- TOC END -->

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Production Ready](https://img.shields.io/badge/status-production--ready-brightgreen.svg)](#)
[![HTTP Foundation](https://img.shields.io/badge/http-foundation-green.svg)](#)
[![Documentation](https://img.shields.io/badge/docs-organized-blue.svg)](../)

**HTTP client and FastAPI integration foundation** for the FLEXT enterprise data integration platform, providing HTTP operations with FlextResult patterns and synchronous architecture.

> **✅ STATUS**: Version 0.9.9 - Production foundation implemented, comprehensive test coverage, ready for 1.0.0 release

______________________________________________________________________

## 🚀 Overview

FLEXT-API serves as the **HTTP foundation** for FLEXT's enterprise data integration platform, providing HTTP client functionality and FastAPI application creation across 33+ FLEXT ecosystem projects. This library eliminates HTTP implementation duplication while maintaining enterprise-grade patterns.

### 🎯 Core Features

- **🔗 HTTP Client Foundation** - Comprehensive client wrapper with FlextResult patterns
- **🌐 FastAPI Integration** - Application factory patterns for web services
- **📊 Domain Models** - Pydantic v2 validation and business logic
- **⚙️ Configuration Management** - Environment-aware settings and validation
- **🔧 HTTP Utilities** - Helper functions and transformations
- **📡 Protocol Support** - Multiple protocols (HTTP, GraphQL, WebSocket, SSE)

### 🏢 Integration with FLEXT Ecosystem

- **flext-core** → Foundation patterns (FlextResult, FlextService, FlextModels)
- **FLEXT Data Platform** → HTTP operations for data pipeline orchestration
- **33+ FLEXT Projects** → Unified HTTP client preventing duplicate implementations
- **Enterprise APIs** → REST API patterns and FastAPI application hosting

______________________________________________________________________

## 🏗️ Current Source Structure

FLEXT-API follows a **Clean Architecture** pattern with clear separation of concerns:

```
src/flext_api/
├── __init__.py              # Public API exports
├── __version__.py           # Version management
├── api.py                   # Main API interface
├── app.py                   # FastAPI application factory
├── client.py                # HTTP client implementation (605 lines)
├── config.py                # Configuration management (187 lines)
├── constants.py             # Configuration constants
├── exceptions.py            # HTTP-specific exceptions
├── handlers.py              # Request/response handlers
├── middleware.py            # HTTP middleware implementations
├── models.py                # Pydantic models (409 lines)
├── plugins.py               # Plugin system
├── protocol_impls/          # Protocol implementations
│   ├── graphql.py          # GraphQL protocol support
│   ├── http_client.py      # HTTP client protocol
│   ├── http.py             # HTTP protocol implementation
│   ├── logger.py           # Logging protocol
│   ├── sse.py              # Server-Sent Events
│   ├── storage_backend.py  # Storage protocol
│   └── websocket.py        # WebSocket protocol
├── protocol_stubs/          # Protocol stubs
│   ├── grpc_stub.py        # gRPC stub implementation
│   └── protobuf_stub.py    # Protocol buffer stub
├── protocols.py             # Protocol definitions
├── py.typed                 # Type checking marker
├── registry.py              # Component registry
├── schemas/                 # Schema definitions
│   ├── asyncapi.py         # AsyncAPI schema support
│   ├── jsonschema.py       # JSON Schema support
│   └── openapi.py          # OpenAPI schema support
├── serializers.py           # Data serialization
├── server.py                # Server implementation
├── storage.py               # Storage abstraction
├── transports.py            # Transport layer
├── typings.py               # Type definitions
├── utilities.py             # HTTP utilities (414 lines)
└── webhook.py               # Webhook handling
```

### 🎯 Key Architectural Patterns

- **Clean Architecture** - Clear separation between domain, use cases, and infrastructure
- **Railway Pattern** - Error handling with FlextResult (90% implementation)
- **Factory Pattern** - Application and client factory methods
- **Plugin Architecture** - Extensible protocol implementations
- **Configuration Management** - Environment-aware settings with validation

______________________________________________________________________

## 📚 Documentation Structure

### 🏗️ Architecture & Design

- **[Architecture Overview](architecture/overview.md)** - System design and patterns
- **[API Reference](api/)** - Complete API documentation
  - **[Core API](api/core.md)** - Main API interface
  - **[Middleware](api/middleware.md)** - HTTP middleware implementations
  - **[Protocols](api/protocols.md)** - Protocol implementations
  - **[Schemas](api/schemas.md)** - Schema definitions
  - **[Storage](api/storage.md)** - Storage abstraction

### 🔧 Development & Integration

- **[Getting Started](guides/getting-started.md)** - Installation and setup guide
- **[Configuration Guide](guides/configuration.md)** - Configuration patterns and best practices
- **[HTTP Client Guide](guides/http-client.md)** - HTTP client usage and patterns
- **[Testing Guide](guides/testing.md)** - Testing strategies and examples
- **[Troubleshooting](guides/troubleshooting.md)** - Common issues and solutions

______________________________________________________________________

## 🚀 Quick Start

### Installation

```bash
# From source (recommended for development)
git clone <flext-api-repo>
cd flext-api
poetry install

# Or via pip (when available)
pip install flext-api
```

### Basic HTTP Client Usage

```python
from flext_api import FlextApiClient
from flext_api import FlextApiSettings

# Configure client
config = FlextApiSettings(base_url="https://api.example.com")
client = FlextApiClient(config)

# Make requests with automatic error handling
result = client.get("/users")
if result.is_success():
    users = result.unwrap()
    print(f"Found {len(users)} users")
else:
    error = result.unwrap_failure()
    print(f"Error: {error}")
```

### FastAPI Application Setup

```python
from flext_api import create_fastapi_app
from flext_api import FlextApiSettings

# Create FastAPI application
config = FlextApiSettings(title="My API", version="1.0.0")
app = create_fastapi_app(config)


# Add your routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

______________________________________________________________________

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flext_api --cov-report=html

# Run specific test categories
pytest tests/unit/        # Unit tests
pytest tests/integration/ # Integration tests
pytest tests/e2e/         # End-to-end tests
```

**Current Coverage**: 100% test pass rate, MyPy strict mode passes

______________________________________________________________________

## 📈 Current Status

| Metric                 | Status        | Details                                     |
| ---------------------- | ------------- | ------------------------------------------- |
| **Core Functionality** | ✅ Complete   | HTTP client and FastAPI integration working |
| **Test Coverage**      | ✅ 100%       | All tests passing, comprehensive coverage   |
| **Type Safety**        | ✅ Strict     | MyPy strict mode passes                     |
| **Code Quality**       | ✅ Production | Enterprise-grade implementation             |
| **FLEXT Integration**  | 🟢 85%        | Full flext-core pattern integration         |

### 🎯 Production Readiness

- **Enterprise Patterns**: Complete FlextResult, FlextService integration
- **Error Handling**: Comprehensive railway-oriented error management
- **Configuration**: Environment-aware settings with validation
- **Documentation**: Complete API reference and guides
- **Testing**: 100% test coverage with integration tests

______________________________________________________________________

## 🤝 Contributing

1. **Code Standards**: Follow FLEXT patterns and Clean Architecture principles
1. **Testing**: Maintain 100% test coverage with comprehensive test suites
1. **Documentation**: Update relevant guides for new features
1. **Quality Gates**: All code must pass MyPy strict mode and comprehensive tests

______________________________________________________________________

## 📋 Roadmap

### Immediate (Next Release)

- **Protocol Expansion**: Enhanced GraphQL and WebSocket support
- **Performance Optimization**: HTTP client performance improvements
- **Middleware Enhancement**: Additional middleware implementations

### Short-term (Next Month)

- **Authentication Integration**: Built-in auth support for HTTP clients
- **Monitoring Integration**: flext-observability integration
- **Plugin Ecosystem**: Enhanced plugin architecture

### Long-term (Next Quarter)

- **Microservices Support**: Enhanced support for microservice architectures
- **API Gateway Features**: Rate limiting, caching, and routing
- **Advanced Protocols**: gRPC-Web, HTTP/2, and QUIC support

______________________________________________________________________

**FLEXT-API** - Enterprise HTTP Foundation | Built with ❤️ for reliability and scale
