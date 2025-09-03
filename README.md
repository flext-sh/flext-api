# flext-api - HTTP Foundation Library

**Type**: Library | **Status**: Active Development | **Version**: 0.9.0

HTTP client and FastAPI integration library for the FLEXT ecosystem, providing unified HTTP client functionality, query builders, and FastAPI integration patterns.

## Project Status

**Current State**: Stable foundation with ongoing improvements

- **Test Coverage**: 85% (684 tests passing)
- **Code Quality**: PyRight/MyPy compliant with minimal warnings
- **Architecture**: Clean Architecture patterns with FlextResult error handling
- **HTTP Client**: Production-ready with plugin system (caching, retry, circuit breaker)
- **FastAPI Integration**: Complete with middleware, health checks, and OpenAPI docs

## Quick Start

### Installation

```bash
# Install dependencies
poetry install

# Install with development tools
poetry install --with dev,test,typings,security
```

### Basic Usage

```bash
# Basic HTTP client test
python -c "from flext_api import create_flext_api; api = create_flext_api(); print('✅ HTTP Client Ready')"

# Start development server
make dev
# Server available at http://localhost:8000

# Run quality checks
make validate  # Full validation (lint + type + security + test)
make test      # Run test suite with coverage
```

## Core Features

### HTTP Client System

- **Modern Async Client**: Built on httpx/aiohttp with comprehensive error handling
- **Plugin Architecture**: Extensible with caching, retry, circuit breaker, and custom plugins
- **FlextResult Integration**: Type-safe error handling throughout HTTP operations
- **Request/Response Pipeline**: Configurable pre/post processing with middleware support

### FastAPI Integration

- **Production-Ready App**: Complete FastAPI application with health checks
- **Middleware Stack**: Request ID, error handling, CORS, and compression
- **API Documentation**: Automatic OpenAPI generation with ReDoc/Swagger UI
- **Configuration Management**: Environment-based settings with validation

### Query & Response Builders

- **Fluent Interface**: Chainable query builders for complex API requests
- **Type Safety**: Full Pydantic model validation for all data structures
- **Response Standardization**: Consistent response formats across all endpoints

## Architecture

### Design Patterns

- **Clean Architecture**: Clear separation between domain, application, and infrastructure layers
- **Railway-Oriented Programming**: FlextResult pattern for comprehensive error handling
- **Composition over Inheritance**: Modular design with clear component boundaries
- **Plugin System**: Extensible architecture for custom functionality

### Key Components

```python
from flext_api import (
    create_flext_api,           # Main API factory
    create_client,              # HTTP client factory
    create_flext_api_app,       # FastAPI app factory
    FlextApiClient,             # HTTP client class
    FlextApiBuilder,            # Query/response builders
)

# Create API instance
api = create_flext_api()

# Create HTTP client with plugins
client = create_client({
    "base_url": "https://api.example.com",
    "timeout": 30,
    "max_retries": 3
})

# Create FastAPI application
app = create_flext_api_app()
```

## Development

### Quality Standards

- **Test Coverage**: Minimum 85% with comprehensive unit and integration tests
- **Type Safety**: Full MyPy strict mode compliance with discriminated unions
- **Code Quality**: Ruff linting with zero tolerance for errors
- **Security**: Bandit scanning for security vulnerabilities

### Essential Commands

```bash
# Development workflow
make test              # Run test suite (684 tests)
make lint              # Code quality checks
make type-check        # Type safety validation
make validate          # Complete quality pipeline

# Development server
make dev               # Start server with hot reload
make serve             # Alias for dev

# Testing variants
make test-unit         # Unit tests only (fast)
make test-integration  # Integration tests
make test-api          # API endpoint tests
make coverage-html     # Generate HTML coverage report
```

### Project Structure

```
src/flext_api/
├── api.py                   # Main FlextApi class with composition patterns
├── api_app.py               # FastAPI application factory and configuration
├── api_client.py            # HTTP client system with plugins
├── api_config.py            # Configuration management
├── api_models.py            # Pydantic models and data structures
├── base_service.py          # Base service patterns
├── builder.py               # Query/response builders with fluent interfaces
├── client.py                # Legacy HTTP client compatibility
├── config.py                # Legacy configuration compatibility
├── constants.py             # Project constants and enums
├── main.py                  # FastAPI application entry point
└── ...                      # Additional components and utilities
```

## Integration

### FLEXT Ecosystem

**For complete FLEXT ecosystem overview, see [FLEXT README.md](../README.md)**

This library integrates with:

- **flext-core**: Foundation patterns, FlextResult, dependency injection
- **FlexCore**: Go runtime service HTTP communication (port 8080)
- **FLEXT Service**: Data platform service integration (port 8081)
- **flext-auth**: Authentication over HTTP protocols
- **flext-observability**: Metrics collection via REST APIs

See [FLEXT Architecture Documentation](../docs/architecture/) for detailed integration patterns.

### External Dependencies

- **FastAPI 0.116+**: Modern async web framework
- **Pydantic 2.10+**: Data validation and serialization
- **httpx 0.28+**: Modern HTTP client
- **aiohttp 3.12+**: Alternative async HTTP client

## API Reference

### Health Endpoints

- `GET /health` - Comprehensive health check with service status
- `GET /health/live` - Liveness probe for Kubernetes
- `GET /health/ready` - Readiness probe for Kubernetes
- `GET /` - API information and version
- `GET /info` - Detailed API and environment information

### Documentation

- `/docs` - Interactive Swagger UI (development mode)
- `/redoc` - ReDoc documentation (development mode)
- `/openapi.json` - OpenAPI schema

## Performance

- **Request Throughput**: Optimized async handling with connection pooling
- **Memory Efficiency**: Minimal memory footprint with streaming support
- **Caching**: Built-in response caching with configurable TTL
- **Circuit Breaker**: Automatic failure detection and recovery

## Contributing

1. **Setup**: `poetry install --with dev,test`
2. **Quality Gates**: Run `make validate` before committing
3. **Testing**: Add comprehensive tests for new features
4. **Documentation**: Update docstrings and examples

## License

MIT License - see LICENSE file for details.

---

**FLEXT API v0.9.0** - Enterprise-grade HTTP foundation library for distributed data integration platform. Part of the [FLEXT Ecosystem](../README.md).
