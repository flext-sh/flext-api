# flext-api Documentation

**HTTP client and FastAPI integration library** for the FLEXT ecosystem providing unified HTTP operations using FlextResult patterns.

> **Status**: Version 0.9.0 - Working HTTP foundation with 78% test pass rate (261/334 tests passing)

---

## 📚 Documentation Index

### Getting Started
- **[Getting Started](getting-started.md)** - Installation, setup, and basic usage patterns
- **[API Reference](api-reference.md)** - Complete API documentation with examples

### Architecture & Design
- **[Architecture](architecture.md)** - System design, patterns, and component structure
- **[Configuration](configuration.md)** - Settings and environment configuration

### Development
- **[Development](development.md)** - Development workflow and contributing guidelines
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

### Integration
- **[Integration](integration.md)** - FLEXT ecosystem integration patterns

---

## 🔧 Core Components

### HTTP Client
```python
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels

client = FlextApiClient(base_url="https://api.example.com")
request = FlextApiModels.HttpRequest(method="GET", url="/data")
response = await client.request(request)
```

### FastAPI Integration
```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

config = FlextApiModels.AppConfig(
    title="My API",
    app_version="1.0.0"
)
app = create_fastapi_app(config)
```

---

## 📊 Current Status

### Working Features ✅
- **HTTP Client**: FlextApiClient with async operations
- **FastAPI Factory**: create_fastapi_app with health endpoints
- **Domain Models**: Pydantic v2 models with validation
- **Type Safety**: Complete MyPy strict mode compliance
- **Quality Gates**: Ruff linting and Bandit security pass

### Test Results
- **Total Tests**: 334
- **Passing**: 261 (78%)
- **Failing**: 59 (model validation, missing constants)
- **Errors**: 14 (fixture configuration)

### Quality Metrics
- **Linting**: ✅ Zero Ruff violations
- **Type Checking**: ✅ MyPy strict mode passes
- **Security**: ✅ No critical vulnerabilities
- **Architecture**: Mixed-quality foundation (6.5/10)

---

## 🛠️ Available Exports

```python
from flext_api import (
    FlextApi,              # HTTP facade
    FlextApiClient,        # HTTP client
    FlextApiConfig,        # Configuration
    FlextApiModels,        # Domain models
    FlextApiConstants,     # HTTP constants
    FlextApiUtilities,     # Helper functions
    FlextApiStorage,       # Storage abstraction
    FlextApiExceptions,    # Exception hierarchy
    create_flext_api,      # Client factory
)

# FastAPI integration (separate import)
from flext_api.app import create_fastapi_app
```

---

## 🚧 Known Issues

### Test Failures (59/334)
- Missing `HttpMethods` constant expected by some tests
- Stricter Pydantic validation than test assumptions
- Some fixture configuration incomplete

### Missing Export
- `create_fastapi_app` not exported from `__init__.py`
- Requires direct import: `from flext_api.app import create_fastapi_app`

### API Mismatch
- `AppConfig` requires `app_version` field, not `version`
- Tests and docs assume different field name

---

## 📋 Quick Reference

### Essential Commands
```bash
make validate           # Complete pipeline (lint + type + test)
make lint              # Code quality check
make type-check        # MyPy type safety
make test              # Run test suite
```

### Basic HTTP Client
```python
import asyncio
from flext_api import FlextApiClient

async def example():
    client = FlextApiClient(base_url="https://httpbin.org")
    response = await client.get("/json")
    return response.status_code

asyncio.run(example())
```

### FastAPI Application
```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

config = FlextApiModels.AppConfig(
    title="Test API",
    app_version="1.0.0"  # Note: app_version, not version
)

app = create_fastapi_app(config)
# Health endpoint available at /health
```

---

## 🆘 Support

- **Issues**: Report problems with specific test failures or API mismatches
- **Documentation**: All docs reflect actual src/ implementation
- **Quality**: Current focus on improving 78% test pass rate

---

**Version**: 0.9.0
**Last Updated**: September 17, 2025
**Status**: Working HTTP foundation with mixed-quality implementation