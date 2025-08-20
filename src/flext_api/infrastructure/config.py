"""FLEXT API Infrastructure Configuration Management.

This module provides comprehensive configuration management for the FLEXT API
infrastructure layer, implementing Clean Architecture patterns with environment
variable support, validation, type safety, and secret management.

## Module Role in Architecture

This configuration module serves as the foundation for all infrastructure
components, providing:

- **Environment Variables**: Automatic loading and validation from environment
- **Type Safety**: Pydantic-based models with comprehensive validation
- **Secret Management**: Secure handling of sensitive configuration data
- **Multi-environment**: Support for development, staging, and production environments
- **Validation**: Business rule validation and configuration consistency checks

## Core Design Patterns

The configuration system follows these architectural patterns:

- **Builder Pattern**: For constructing complex configuration objects
- **Factory Pattern**: For creating environment-specific configurations
- **Validation Pattern**: Multi-layer validation with detailed error reporting
- **Dependency Injection**: Integration with flext-core container patterns

## Configuration Architecture

### Environment Variables
Configuration automatically loads from environment variables with the `FLEXT_API_` prefix:

- `FLEXT_API_HOST`: API server host (default: localhost)
- `FLEXT_API_PORT`: API server port (default: 8000)
- `FLEXT_API_DEBUG`: Debug mode flag
- `FLEXT_API_DATABASE_URL`: Database connection string
- `FLEXT_API_SECRET_KEY`: Application secret key

### Multi-environment Support
The system supports multiple deployment environments:

- **development**: Local development with relaxed validation
- **staging**: Pre-production environment with production-like settings
- **production**: Production environment with strict validation
- **test**: Testing environment with isolated configuration

### Type Safety
All configuration fields are strongly typed using Pydantic models:

```python
from flext_api.infrastructure.config import FlextApiSettings

# Type-safe configuration creation
settings = FlextApiSettings(
    api_host="0.0.0.0",
    api_port=8000,
    debug=False
)
```

## Development Status

This configuration system is under ACTIVE DEVELOPMENT with ongoing Enhancement
to support additional configuration sources, improved validation, and enhanced
Type Safety. While the core functionality is Production Ready, advanced features
are still being developed.

## Usage Patterns

### Basic Configuration Loading

```python
from flext_api.infrastructure.config import FlextApiSettings, create_api_settings

# Automatic environment loading
settings_result = create_api_settings()
if settings_result.success:
    settings = settings_result.data
```

### Configuration Examples

```python
# Development configuration
dev_config = FlextApiSettings(
    environment="development",
    debug=True,
    log_level="DEBUG"
)

# Production configuration with validation
prod_result = FlextApiSettings.create_with_validation({
    "environment": "production",
    "secret_key": "your-secret-key",
    "database_url": "postgresql://..."
})
```

### Validation
Configuration validation occurs at multiple levels:

```python
# Field-level validation (automatic)
settings = FlextApiSettings(api_port=8000)  # Validates port range

# Business rule validation (explicit)
validation_result = settings.validate_business_rules()
if validation_result.is_failure:
    print(f"Validation failed: {validation_result.error}")
```

## Integration Points

### flext-core Integration
This module integrates with flext-core patterns:

- **FlextResult**: All operations return FlextResult for consistent error handling
- **FlextBaseConfigModel**: Extends base configuration patterns
- **Dependency Injection**: Integrates with the global service container

### Application Layer Integration
Configuration is injected into application services:

```python
from flext_core import get_flext_container

container = get_flext_container()
container.register_singleton("config", settings)
```

### External Services Integration
Configuration provides connection details for:

- **Database**: Connection URLs, pool sizes, timeouts
- **Cache**: Redis connections, TTL settings
- **HTTP**: Client timeouts, retry policies
- **Security**: JWT settings, CORS origins

## Error Handling Philosophy

Configuration errors are handled using FlextResult patterns:

- **Validation Errors**: Detailed field-level error messages
- **Environment Errors**: Missing or invalid environment variables
- **Business Rule Errors**: Configuration inconsistencies
- **Type Errors**: Invalid data types with clear error messages

## Performance Characteristics

The configuration system is optimized for:

- **Fast configuration loading**: Minimal startup time
- **Memory-efficient**: Lazy loading of optional components
- **Hot-reload**: Development-time configuration updates
- **Caching**: Parsed configuration caching for performance

## Quality Standards

All configuration components follow FLEXT standards:

- **Comprehensive Documentation**: Detailed usage examples and patterns
- **Type Safety**: Full type annotations and validation
- **Error Handling**: FlextResult patterns for all operations
- **Testing**: 100% test coverage with edge case validation
- **Security**: Secure handling of sensitive configuration data

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Re-export configuration components from main config module
from flext_api.config import (
    FlextApiSettings,
    create_api_settings,
    load_configuration,
    validate_configuration,
)

__all__ = [
    "FlextApiSettings",
    "create_api_settings", 
    "load_configuration",
    "validate_configuration",
]