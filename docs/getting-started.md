# Getting Started with flext-api

**HTTP and FastAPI Foundation for the FLEXT Ecosystem**

**Version**: 0.9.0 | **Last Updated**: September 17, 2025

This guide will help you get started with flext-api, the HTTP client and FastAPI application foundation for the FLEXT enterprise data integration platform.

---

## 📋 Prerequisites

### **System Requirements**

- **Python**: 3.13+ (required for advanced type features)
- **Poetry**: Latest version for dependency management
- **FLEXT Workspace**: Must be part of the FLEXT ecosystem workspace

### **FLEXT Ecosystem Integration**

flext-api requires integration with the core FLEXT libraries:

- **flext-core**: Foundation patterns and domain services
- **Python 3.13+**: Advanced type system and performance features
- **Poetry environment**: Workspace dependency management

---

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
# Clone the repository
git clone https://github.com/flext-sh/flext-api.git
cd flext-api

# Install dependencies
poetry install

# Verify installation
make validate
```

---

## 🚀 First Steps

### **1. Verify Installation**

```bash
# Run basic validation
make check

# Verify all quality gates pass
make validate

# Check HTTP client functionality
poetry run python -c "
from flext_api import FlextApiClient
print('✅ flext-api installed successfully')
"
```

### **2. Basic HTTP Client Usage**

Create your first HTTP client:

```python
import asyncio
from flext_api import FlextApiClient, FlextApiModels

async def basic_http_example():
    """Basic HTTP client usage with FlextResult error handling."""

    # Create HTTP client
    client = FlextApiClient(
        base_url="https://httpbin.org",
        timeout=30
    )

    # Create HTTP request
    request = FlextApiModels.HttpRequest(
        method="GET",
        url="/get",
        headers={
            "Accept": "application/json",
            "User-Agent": "flext-api/0.9.0"
        }
    )

    # Make request with FlextResult error handling
    try:
        response = await client.request(request)

        if response.status_code == 200:
            print(f"✅ Success: {response.json()}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Request failed: {e}")

    finally:
        await client.close()

# Run the example
asyncio.run(basic_http_example())
```

### **3. FastAPI Application Creation**

Create a basic FastAPI application:

```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

def create_basic_api():
    """Create a basic FastAPI application using flext-api."""

    # Configure application
    config = FlextApiModels.AppConfig(
        title="My API Service",
        app_version="1.0.0",
        description="Basic API using flext-api foundation"
    )

    # Create FastAPI application
    app = create_fastapi_app(config)

    # Add custom endpoint
    @app.get("/api/status")
    async def get_status():
        return {
            "service": "my-api",
            "version": "1.0.0",
            "status": "healthy"
        }

    return app

# Run with: uvicorn main:app --reload
app = create_basic_api()
```

---

## 🔧 Development Environment

### **Essential Commands**

```bash
# Development workflow
make dev                    # Start FastAPI development server
make format                 # Format code with Black and isort
make lint                   # Run Ruff linting
make type-check             # Run MyPy type checking
make test                   # Run test suite
make security               # Run security scans

# Complete validation
make validate               # All quality gates (lint + type + security + test)
make clean                  # Clean build artifacts
```

### **Configuration**

Create a basic configuration file:

```python
# config.py
from flext_api.config import FlextApiConfig

# Development configuration
config = FlextApiConfig(
    base_url="https://api.example.com",
    timeout=30,
    max_retries=3,
    headers={
        "User-Agent": "my-service/1.0.0",
        "Accept": "application/json"
    }
)

# Use with HTTP client
from flext_api import FlextApiClient

async def configured_client():
    client = FlextApiClient(config=config)
    # Use client for requests...
    await client.close()
```

---

## 🧪 Testing Your Setup

### **1. Run Basic Tests**

```bash
# Run test suite
make test

# Run specific test categories
pytest -m unit               # Unit tests
pytest -m integration        # Integration tests
pytest -m api                # FastAPI tests
```

### **2. Test HTTP Client**

```python
import asyncio
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels

async def test_http_client():
    """Test HTTP client with a real API."""

    client = FlextApiClient(base_url="https://httpbin.org")

    try:
        # Test GET request
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="/json"
        )

        response = await client.request(request)
        print(f"GET Response: {response.status_code}")

        # Test POST request
        post_request = FlextApiModels.HttpRequest(
            method="POST",
            url="/post",
            json={"test": "data", "timestamp": "2025-09-17"}
        )

        post_response = await client.request(post_request)
        print(f"POST Response: {post_response.status_code}")

    except Exception as e:
        print(f"Test failed: {e}")

    finally:
        await client.close()

# Run the test
asyncio.run(test_http_client())
```

### **3. Test FastAPI Application**

```bash
# Start development server
make dev

# Test in another terminal
curl -f http://localhost:8000/health
curl -f http://localhost:8000/docs
```

---

## 📚 Next Steps

### **Essential Documentation**

- **[Architecture](architecture.md)** - Understanding flext-api design patterns
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Configuration](configuration.md)** - Advanced configuration options
- **[Development](development.md)** - Development workflows and contribution

### **Integration Guides**

- **FLEXT Ecosystem** - Integrate with other FLEXT projects
- **HTTP Client Patterns** - Advanced HTTP client usage
- **FastAPI Applications** - Building production APIs
- **Authentication** - Security and authentication patterns

### **Example Projects**

- **Basic HTTP Service** - Simple HTTP client service
- **REST API Server** - Complete FastAPI application
- **Integration Service** - Connecting FLEXT services via HTTP

---

## 🆘 Common Issues

### **Installation Issues**

```bash
# Poetry lock issues
poetry lock --no-update

# Dependency conflicts
poetry install --sync

# Clean reinstall
rm -rf .venv poetry.lock
poetry install
```

### **Import Issues**

```python
# Correct imports
from flext_api import FlextApiClient, FlextApiModels
from flext_api.config import FlextApiConfig
from flext_api.app import create_fastapi_app

# Avoid internal imports
# from flext_api.client import ... # Don't use internal imports
```

### **Development Server Issues**

```bash
# Check if port is available
lsof -i :8000

# Use different port
make dev PORT=8080

# Check logs
make dev --log-level debug
```

---

## ✅ Validation Checklist

Before proceeding to advanced usage:

- [ ] Installation completed successfully
- [ ] `make validate` passes all quality gates
- [ ] Basic HTTP client example works
- [ ] FastAPI application starts correctly
- [ ] Test suite runs without errors
- [ ] Development server accessible at <http://localhost:8000>

---

**Next**: Continue to [Architecture Documentation](architecture.md) to understand flext-api design patterns and FLEXT ecosystem integration.
