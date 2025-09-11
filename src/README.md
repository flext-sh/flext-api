# Source Code

**Source code organization for FLEXT API library**

## Directory Structure

```
src/flext_api/
├── __init__.py              # Public API exports
├── api.py                   # Main FlextApi service class
├── app.py                   # FastAPI application factory
├── builder.py               # Query/response builders
├── client.py                # HTTP client with plugins
├── config.py                # Configuration management
├── constants.py             # Project constants
├── exceptions.py            # Custom exceptions
├── fields.py                # Field definitions
├── main.py                  # Application entry point
├── storage.py               # Storage utilities
├── types.py
├── py.typed
├── domain/                  # Domain layer
│   ├── __init__.py
│   ├── entities.py         # Domain entities
│   └── value_objects.py    # Value objects
└── infrastructure/         # Infrastructure layer
    ├── __init__.py
    └── config.py           # Infrastructure config
```

## Main Components

### Core Services

- **api.py** - Main service class with HTTP client composition
- **client.py** - HTTP client with plugin architecture
- **app.py** - FastAPI application factory
- **main.py** - Application entry point

### Data Components

- **builder.py** - Query and response builders with fluent interfaces
- **storage.py** - Simple in-memory storage implementation
- **config.py** - Configuration settings management

### Supporting Modules

- **types.py** - Type definitions and generic types
- **constants.py** - Project constants and enumerations
- **exceptions.py** - Custom exception classes
- **fields.py** - Field validation and definitions

### Architecture Layers

- **domain/** - Domain entities and value objects
- **infrastructure/** - External concerns and configuration

## Development

See project root documentation for development guidelines, testing procedures, and API usage examples.
