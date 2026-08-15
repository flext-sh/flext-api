# FLEXT-API

<!-- TOC START -->
- [Overview](#overview)
  - [Core Features](#core-features)
  - [Integration with the FLEXT Ecosystem](#integration-with-the-flext-ecosystem)
- [Current Source Structure](#current-source-structure)
  - [Key Architectural Patterns](#key-architectural-patterns)
- [Documentation Structure](#documentation-structure)
  - [Architecture & Design](#architecture-design)
  - [Development & Integration](#development-integration)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Basic HTTP Client Usage](#basic-http-client-usage)
  - [Settings-Driven Configuration](#settings-driven-configuration)
  - [FastAPI Application Setup](#fastapi-application-setup)
- [Testing](#testing)
- [Current Status](#current-status)
  - [Production Readiness](#production-readiness)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
  - [Immediate (Next Release)](#immediate-next-release)
  - [Short-term (Next Month)](#short-term-next-month)
  - [Long-term (Next Quarter)](#long-term-next-quarter)
<!-- TOC END -->

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Current](https://img.shields.io/badge/status-production--ready-brightgreen.svg)](#)
[![HTTP Foundation](https://img.shields.io/badge/http-foundation-green.svg)](#)
[![Documentation](https://img.shields.io/badge/docs-organized-blue.svg)](../)

**HTTP client foundation** for the FLEXT enterprise data integration platform.
FLEXT-API provides a typed HTTP facade (`FlextApi`), a low-level client
(`FlextApiClient`), Pydantic v2 request/response models, and railway-oriented
error handling through `p.Result`.

> **STATUS**: Version 0.12.0-dev — public HTTP facade, settings, and model
> layer implemented. Additional protocols, middleware, and schema generation are
> not yet part of the public API.

______________________________________________________________________

## Overview

FLEXT-API serves as the **HTTP foundation** for FLEXT's enterprise data
integration platform. It eliminates HTTP implementation duplication while
maintaining enterprise-grade patterns: typed settings, validated request/response
models, and `p.Result`/`r` error handling.

### Core Features

- **HTTP Client Foundation** — `FlextApi` facade with `get/post/put/patch/delete`
- **Typed Settings** — `FlextApiSettings` with env-var support (`FLEXT_API_*`)
- **Pydantic v2 Models** — `m.Api.HttpRequest` and `m.Api.HttpResponse`
- **Railway Pattern** — `p.Result` error handling for every operation
- **Protocol Plugin Foundation** — `FlextApiProtocolPluginManager` for future protocols

### Integration with the FLEXT Ecosystem

- **flext-core** → Foundation patterns (`c`, `t`, `p`, `m`, `u`, `r`, `s`)
- **FLEXT Data Platform** → HTTP operations for data pipeline orchestration
- **FLEXT Projects** → Shared HTTP facade preventing duplicate implementations

______________________________________________________________________

## Current Source Structure

```text
src/flext_api/
├── __init__.py              # Public facade exports
├── __version__.py           # Version management
├── api.py                   # FlextApi public facade
├── base.py                  # FlextApiServiceBase
├── _config.py               # Config integration
├── _settings.py             # FlextApiSettings
├── constants.py             # Public constants facade
├── _constants/              # Constant implementations
├── models.py                # Public models facade
├── _models/                 # Model implementations (request, response, client, storage, webhook)
├── protocols.py             # Public protocols facade
├── _protocols/              # Protocol implementations (HTTP, plugins, transports, etc.)
├── typings.py               # Public typings facade
├── _typings/                # Typing implementations
├── utilities.py             # Public utilities facade
├── _utilities/              # Utility implementations (client, request utils, serializers, etc.)
├── _settings.py             # Settings singleton
└── py.typed                 # Type checking marker
```

### Key Architectural Patterns

- **Clean Architecture** — Clear separation between public facades and private implementations
- **Railway Pattern** — `p.Result` error handling through every HTTP path
- **MRO Composition** — Facades composed via mixin classes
- **Plugin Architecture** — Protocol plugin manager ready for future protocols
- **Configuration SSOT** — `config/*.yaml` and `FlextApiSettings` as the single source of truth

______________________________________________________________________

## Documentation Structure

### Architecture & Design

- **[Architecture Overview](architecture/overview.md)** — System design and patterns
- **[API Reference](api/)** — Core API, protocols, middleware, schemas, and storage docs

### Development & Integration

- **[Getting Started](guides/getting-started.md)** — Installation and setup guide
- **[Configuration Guide](guides/configuration.md)** — Configuration patterns and best practices
- **[HTTP Client Guide](guides/http-client.md)** — HTTP client usage and patterns
- **[Testing Guide](guides/testing.md)** — Testing strategies and examples
- **[Troubleshooting](guides/troubleshooting.md)** — Common issues and solutions

______________________________________________________________________

## Quick Start

### Installation

```bash
# From the FLEXT workspace (recommended for development)
make boot

# Install flext-api specifically
uv sync --package flext-api
```

### Basic HTTP Client Usage

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings

settings = FlextApiSettings(base_url="https://api.example.com", timeout=30)
api = FlextApi(settings=settings)

result = api.get("/users")
if result.success:
    response = result.unwrap()
    print(f"Status: {response.status_code}")
    print(f"Body: {response.body}")
else:
    print(f"Error: {result.error}")```
### Settings-Driven Configuration

```python
from __future__ import annotations

from flext_api import FlextApiSettings

settings = FlextApiSettings(
    base_url="https://api.example.com",
    timeout=30.0,
    max_retries=3,
    default_headers={"User-Agent": "flext-api"},
)

print(settings.Api.base_url)
print(settings.Api.timeout)```
### FastAPI Application Setup

A FastAPI application factory is **not** currently part of the public API. Use
`FlextApi` and `FlextApiClient` directly in your own FastAPI/Starlette
application if needed.

______________________________________________________________________

## Testing

```bash
# Run the flext-api test suite
make test PROJECT=flext-api

# Run markdown documentation examples
uv run pytest --markdown-docs -q

# Run specific test categories
uv run pytest tests/unit/        # Unit tests
uv run pytest tests/integration/ # Integration tests
uv run pytest tests/e2e/          # End-to-end tests```
______________________________________________________________________

## Current Status

| Metric                 | Status       | Details                                          |
| ---------------------- | ------------ | ------------------------------------------------ |
| **Core Functionality** | Complete     | HTTP client facade and settings implemented        |
| **Test Coverage**      | In progress  | Markdown examples validated; package tests growing |
| **Type Safety**        | Strict       | FLEXT pattern compliance and Pydantic v2 models  |
| **Code Quality**       | In progress  | Ruff / Pyrefly gates enforced via `make check`   |
| **FLEXT Integration**  | Active       | Full flext-core facade integration               |

### Production Readiness

- **Enterprise Patterns**: `r`, `s`, and MRO composition integrated
- **Error Handling**: Railway-oriented error management on every HTTP path
- **Configuration**: Environment-aware settings with validation
- **Documentation**: User-facing guides and API reference updated to the real API
- **Testing**: Markdown examples run under `uv run pytest --markdown-docs`

______________________________________________________________________

## Contributing

1. **Code Standards**: Follow FLEXT patterns (facades `c/t/p/m/u/r`, MRO, Pydantic v2)
2. **Testing**: Add tests that exercise the public facade and real models
3. **Documentation**: Update relevant guides when changing public APIs
4. **Quality Gates**: Run `make check` before opening a PR

______________________________________________________________________

## Roadmap

### Immediate (Next Release)

- **Documentation Cleanup**: Finish aligning all markdown examples with the real API
- **HTTP Client Hardening**: Timeouts, retries, and error classification improvements
- **Settings Coverage**: Env-var and nested-namespace validation tests

### Short-term (Next Month)

- **Authentication Helpers**: Settings-driven auth headers and credentials
- **Observability Integration**: Structured logging through the existing logger
- **Plugin Ecosystem**: Extend protocol plugin manager examples

### Long-term (Next Quarter)

- **Additional Protocols**: GraphQL, WebSocket, SSE (when the surface is ready)
- **Middleware API**: First-class request/response interception (if added)
- **Schema Generation**: OpenAPI/JSON Schema helpers from public models (if added)

______________________________________________________________________

**FLEXT-API** — Enterprise HTTP Foundation | Built for reliability and scale
