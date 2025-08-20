"""FLEXT API Infrastructure Layer.

This module provides the infrastructure layer components for the FLEXT API,
implementing Clean Architecture patterns with a focus on dependency injection,
configuration management, external service integration, and cross-cutting concerns.

## Module Role in Architecture

The Infrastructure layer provides concrete implementations that the
Application/Domain layers depend on via abstractions. Key responsibilities include:

- **Dependency Injection**: Service Container for service registration, resolution,
  and Lifecycle management
- **Configuration Management**: Environment Variables, multi-environment overrides,
  validation, Type Safety, and Secret Management
- **External Service Integration**: HTTP, gRPC, Database, Cache adapters with
  proper Error Handling patterns
- **Cross-Cutting Concerns**: Logging, monitoring, observability, metrics, tracing

## Core Design Patterns

The infrastructure layer follows these core patterns:

- **Adapter Pattern**: For external service integration
- **Dependency Injection**: Type-safe service container patterns
- **Configuration Architecture**: Environment-based configuration with validation
- **Factory Pattern**: For creating configured service instances

## Development Status

This infrastructure layer is under ACTIVE DEVELOPMENT with iterative
Enhancement. While many components are production-hardened, the overall system
is not yet fully Production Ready.

## Usage Patterns

Common usage patterns include:

### ServiceContainer Registration

```python
from flext_api.infrastructure import config
from flext_core import get_flext_container

# Get the ServiceContainer instance
container = get_flext_container()
container.register("api_client", FlextApiClient)
client = container.resolve("api_client")
```

### Configuration Examples

```python
from flext_api.infrastructure.config import FlextApiSettings

settings = FlextApiSettings()
config = settings.create_with_validation()
```

## Configuration Architecture

The configuration system supports:

- Environment Variables loading
- Multi-environment support (development, staging, production)
- Type Safety through Pydantic models
- Validation at multiple levels
- Secret Management integration

## Integration Points

Key integration points include:

- **flext-core**: Foundation patterns and base configuration
- **Application Layer**: Service resolution and configuration injection
- **External Services**: HTTP clients, databases, caches
- **Dependency Injection**: Centralized service container

## Error Handling Philosophy

All infrastructure components follow FlextResult patterns for:

- Consistent error propagation
- Type-safe error handling
- Detailed error context
- Graceful failure modes

## Performance Characteristics

The infrastructure layer is designed for:

- Fast configuration loading
- Memory-efficient service containers
- Hot-reload capabilities for development
- Minimal performance overhead in production

## Quality Standards

All infrastructure components must:

- Follow FLEXT ecosystem patterns
- Implement comprehensive error handling
- Provide detailed documentation
- Support both sync and async operations
- Include comprehensive test coverage

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Re-export key infrastructure components
from flext_api.infrastructure_config import *

__all__ = [
    # Configuration will be populated by config module exports
]