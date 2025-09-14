# Getting Started with flext-api

**HTTP client and FastAPI integration library** for the FLEXT ecosystem providing unified HTTP operations using FlextResult patterns.

> **Status**: Version 0.9.0 under development - Working HTTP foundation with 78% test pass rate

---

## 🚀 Quick Setup

### Installation

```bash
# Clone the FLEXT workspace
git clone https://github.com/flext-sh/flext.git
cd flext/flext-api

# Install dependencies
poetry install --with dev,test,typings,security

# Verify installation
make validate
```

### Development Environment

```bash
# Run all quality checks
make validate           # Complete pipeline (lint + type + test)
make lint              # Code quality check
make type-check        # MyPy type safety
make test              # Run test suite
```

---

## 🔧 Basic Usage

### HTTP Client

```python
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels
import asyncio

async def basic_http_example():
    # Create HTTP client
    client = FlextApiClient(
        base_url="https://httpbin.org",
        timeout=30
    )

    # Create request
    request = FlextApiModels.HttpRequest(
        method="GET",
        url="/get",
        headers={"User-Agent": "flext-api/0.9.0"}
    )

    # Execute request
    response = await client.request(request)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Error:", response.status_code)

# Run the example
asyncio.run(basic_http_example())
```

### FastAPI Application

```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

# Create application configuration
config = FlextApiModels.AppConfig(
    title="My API",
    app_version="1.0.0",  # Note: use app_version, not version
    description="FastAPI application built with flext-api"
)

# Create FastAPI app
app = create_fastapi_app(config)

# The app includes a health endpoint at /health
# Run with: uvicorn main:app --reload
```

---

## 📋 Core Components

### Available Exports

```python
from flext_api import (
    FlextApi,              # Main HTTP facade
    FlextApiClient,        # HTTP client
    FlextApiConfig,        # Configuration
    FlextApiConstants,     # Constants
    FlextApiModels,        # Domain models
    FlextApiUtilities,     # Utilities
    create_flext_api,      # Client factory
)

# FastAPI app factory (separate import)
from flext_api.app import create_fastapi_app
```

### Configuration

```python
from flext_api.models import FlextApiModels

# Client configuration
client_config = FlextApiModels.ClientConfig(
    base_url="https://api.example.com",
    timeout=30.0,
    max_retries=3,
    headers={"Authorization": "Bearer token"}
)

client = FlextApiClient(**client_config.dict())
```

---

## 🧪 Testing Your Setup

### Basic Test

```python
# test_setup.py
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels
from flext_api.app import create_fastapi_app

def test_http_client():
    client = FlextApiClient(base_url="https://httpbin.org")
    assert client is not None
    print("✅ HTTP client created successfully")

def test_fastapi_app():
    config = FlextApiModels.AppConfig(
        title="Test API",
        app_version="1.0.0"
    )
    app = create_fastapi_app(config)
    assert app is not None
    print("✅ FastAPI app created successfully")

if __name__ == "__main__":
    test_http_client()
    test_fastapi_app()
    print("✅ All tests passed!")
```

### Run Tests

```bash
# Run your test
python test_setup.py

# Run project tests
make test

# Check specific test results
pytest tests/unit/test_models.py -v
```

---

## 📚 Next Steps

### Learn More

1. **[API Reference](api-reference.md)** - Complete API documentation
2. **[Architecture](architecture.md)** - Design patterns and structure
3. **[Configuration](configuration.md)** - Advanced settings and options

### Development Workflow

```bash
# Development cycle
make lint              # Check code quality
make type-check        # Verify type safety
make test              # Run tests
make format            # Auto-format code

# Before committing
make validate          # Complete validation pipeline
```

### Current Implementation Status

- **HTTP Client**: ✅ Working (httpx-based async client)
- **FastAPI Integration**: ✅ Working (application factory)
- **Domain Models**: ✅ Working (Pydantic v2 models)
- **Configuration**: ✅ Working (environment-aware settings)
- **Testing**: ⚠️ 78% pass rate (261/334 tests passing)

---

## ⚠️ Known Issues

### Test Failures

Currently 59 tests are failing, primarily due to:

- Missing `HttpMethods` constant in some test expectations
- Pydantic validation being stricter than test assumptions
- Some fixture configuration issues

### Working Around Issues

```python
# If you encounter import issues with create_fastapi_app
from flext_api.app import create_fastapi_app  # Direct import

# If HttpMethods is not found, use string literals
request = FlextApiModels.HttpRequest(
    method="GET",  # Use string instead of HttpMethods.GET
    url="/api/data"
)
```

---

## 🆘 Getting Help

### Documentation

- **[README.md](../README.md)** - Project overview and status
- **[Architecture](architecture.md)** - System design
- **[Troubleshooting](troubleshooting.md)** - Common issues

### Development

- **Make Commands**: Run `make help` to see all available commands
- **Test Results**: Check `pytest.log` for detailed test output
- **Type Checking**: MyPy and PyRight both pass for src/ directory

---

**Version**: 0.9.0
**Last Updated**: September 17, 2025
**Test Status**: 78% pass rate (261/334 tests)