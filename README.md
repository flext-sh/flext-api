# FLEXT-API


<!-- TOC START -->
- [🚀 Key Features](#-key-features)
- [📦 Installation](#-installation)
- [🛠️ Usage](#-usage)
  - [HTTP Client](#http-client)
  - [FastAPI Application Factory](#fastapi-application-factory)
- [🏗️ Architecture](#-architecture)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
<!-- TOC END -->

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**FLEXT-API** provides the core HTTP foundation for the FLEXT ecosystem, offering a unified, type-safe HTTP client and a robust factory pattern for building FastAPI applications. It integrates seamless railway-oriented error handling and strictly typed domain models to ensure reliability across enterprise services.

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext/flext) ecosystem.

## 🚀 Key Features

- **Unified HTTP Client**: A robust wrapper around `httpx` with built-in `FlextResult` support for safe, predictable HTTP operations.
- **FastAPI Integration**: Application factory patterns for consistent microservice initialization, including middleware and exception handling.
- **Protocol Support**: Extensible architecture supporting multiple protocols including HTTP, GraphQL, WebSocket, and SSE.
- **Type-Safe Models**: Pydantic v2 models for strict request and response validation.
- **Enterprise Configuration**: Environment-aware settings management designed for containerized deployments.
- **Railway-Oriented**: All network operations return `FlextResult[T]`, eliminating the need for try/except blocks in business logic.

## 📦 Installation

To install `flext-api`:

```bash
pip install flext-api
```

Or with Poetry:

```bash
poetry add flext-api
```

## 🛠️ Usage

### HTTP Client

Perform type-safe HTTP requests with automatic error handling.

```python
from flext_api import FlextApiClient, FlextApiModels
from flext_core import FlextResult as r

# 1. Initialize Client
client = FlextApiClient(base_url="https://api.example.com")

# 2. execute Request
def get_users() -> r[list[dict]]:
    request = FlextApiModels.HttpRequest(
        method="GET",
        url="/users",
        headers={"Accept": "application/json"}
    )
    
    return client.request(request).map(lambda res: res.body)

# 3. Handle Result
result = get_users()
if result.is_success:
    users = result.unwrap()
    print(f"Fetched {len(users)} users")
else:
    print(f"Failed: {result.error}")
```

### FastAPI Application Factory

Create consistent, production-ready FastAPI applications.

```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

# Configure the application
config = FlextApiModels.AppConfig(
    title="My Microservice",
    version="1.0.0",
    debug=False
)

# Create the app instance
app = create_fastapi_app(config)

@app.get("/status")
def status():
    return {"status": "operational"}
```

## 🏗️ Architecture

FLEXT-API is built to enforce consistency across distributed systems:

- **Client Layer**: Abstracts underlying transport libraries (httpx) to provide a stable, result-oriented API.
- **Server Layer**: Standardizes FastAPI setup, ensuring all services share common middleware, logging, and error handling patterns.
- **Domain Layer**: Shared Pydantic models ensure that data contracts are honored across boundaries.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development/contributing.md) for details on setting up your environment and submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
