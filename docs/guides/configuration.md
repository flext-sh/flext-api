<!-- TOC START -->
- [Overview](#overview)
- [Configuration Sources](#configuration-sources)
- [Basic Configuration](#basic-configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration Files](#configuration-files)
  - [Programmatic Configuration](#programmatic-configuration)
- [Configuration Validation](#configuration-validation)
- [Configuration Inheritance](#configuration-inheritance)
- [Best Practices](#best-practices)
  - [1. Use Environment Variables for Secrets](#1-use-environment-variables-for-secrets)
  - [2. Validate Configuration Early](#2-validate-configuration-early)
  - [3. Use Configuration Classes](#3-use-configuration-classes)
  - [4. Document Configuration Options](#4-document-configuration-options)
- [Troubleshooting](#troubleshooting)
  - [Common Configuration Issues](#common-configuration-issues)
  - [Debug Configuration](#debug-configuration)
- [Examples](#examples)
  - [Complete Configuration Example](#complete-configuration-example)
- [Reference](#reference)
<!-- TOC END -->

<!-- Generated from docs/guides/configuration.md for flext-api. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-api - FLEXT Configuration Guide

> Project profile: `flext-api`

This guide covers how to configure FLEXT for your specific environment and requirements.

## Overview

FLEXT uses a hierarchical configuration system that supports environment variables, configuration files,
and programmatic configuration. All configuration is validated using Pydantic v2 models for type safety and validation.

## Configuration Sources

FLEXT loads configuration in the following order (later sources override earlier ones):

1. **Default values** in Pydantic models
1. **Environment variables** (prefixed with `FLEXT_`)
1. **Configuration files** (YAML, JSON, or TOML)
1. **Programmatic configuration** in code

## Basic Configuration

### Environment Variables

Set configuration using environment variables with the `FLEXT_` prefix:

```bash
# Core configuration
export FLEXT_LOG_LEVEL=INFO
export FLEXT_DEBUG=false
export FLEXT_ENVIRONMENT=production

# LDIF processing
export FLEXT_LDIF_DEFAULT_ENCODING=utf-8
export FLEXT_LDIF_STRICT_VALIDATION=true
export FLEXT_LDIF_SERVERS_ENABLED=true

# API configuration
export FLEXT_API_BASE_URL=https://api.example.com
export FLEXT_API_TIMEOUT=30
```

### Configuration Files

Create configuration files in YAML, JSON, or TOML format:

**settings.YAML:**

```yaml
# FLEXT Configuration
log_level: INFO
debug: false
environment: production

# LDIF Processing
ldif:
  default_encoding: utf-8
  strict_validation: true
  servers_enabled: true
  batch_size: 1000

# API Configuration
api:
  base_url: https://api.example.com
  timeout: 30
  retry_attempts: 3
```

### Programmatic Configuration

Configure FLEXT programmatically in your code:

```python
```

## Configuration Validation

All configuration is validated using Pydantic v2 models:

```python
from flext_core import FlextSettings, e

try:
    settings = FlextSettings(
        log_level="INVALID_LEVEL"  # This will raise ValidationError
    )
except c.ValidationError as e:
    print(f"Configuration error: {e}")```
## Configuration Inheritance

FLEXT supports configuration inheritance for complex setups:

```python
from flext_core import FlextSettings

# Base configuration
base_config = FlextSettings(log_level="INFO", environment="production")

# Extended configuration
extended_config = FlextSettings(
    **base_config.dict(),
    debug=True,  # Override for development
    custom_setting="value",
)```
## Best Practices

### 1. Use Environment Variables for Secrets

```bash
# Never put secrets in configuration files
export FLEXT_DATABASE_PASSWORD=secret_password
export FLEXT_API_KEY=your_api_key```
### 2. Validate Configuration Early

```python
from flext_core import FlextSettings


def main():
    # Validate configuration at startup
    settings = FlextSettings()

    if not settings.is_valid():
        print("Invalid configuration")
        return 1

    # Continue with application logic
    return 0```
### 3. Use Configuration Classes

```python
from flext_core import FlextSettings, u


class MyAppConfig(FlextSettings):
    custom_setting: str = "default_value"
    another_setting: int = 42

    @u.field_validator("another_setting")
    @classmethod
    def validate_another_setting(cls, v):
        if v < 0:
            raise ValueError("another_setting must be positive")
        return v```
### 4. Document Configuration Options

```python
class FlextLdifSettings(m.BaseModel):
    """Configuration for LDIF processing."""

    default_encoding: str = u.Field(
        default="utf-8", description="Default encoding for LDIF files"
    )

    strict_validation: bool = u.Field(
        default=True, description="Enable strict RFC validation"
    )```
## Troubleshooting

### Common Configuration Issues

1. **Environment Variables Not Loading**

   - Ensure variables are prefixed with `FLEXT_`
   - Check for typos in variable names
   - Verify environment is set before running application

1. **Configuration File Not Found**

   - Check file path is correct
   - Ensure file has proper permissions
   - Verify file format (YAML, JSON, or TOML)

1. **Validation Errors**

   - Check Pydantic model field types
   - Verify required fields are provided
   - Review field validators for constraints

### Debug Configuration

```python
from flext_core import FlextSettings

# Enable debug logging
settings = FlextSettings(debug=True)

# Print configuration
print(settings.dict())

# Validate configuration
if settings.is_valid():
    print("Configuration is valid")
else:
    print("Configuration has errors")```
## Examples

### Complete Configuration Example

```python
#!/usr/bin/env python3
"""Complete FLEXT configuration example."""

import os

from flext_ldif import FlextLdifSettings

from flext_api import FlextApiSettings
from flext_core import (
    FlextSettings,
)


def main():
    # Load configuration from environment
    settings = FlextSettings()

    # Configure LDIF processing
    ldif_config = FlextLdifSettings(
        source_server=os.getenv("FLEXT_SOURCE_SERVER", "oid"),
        target_server=os.getenv("FLEXT_TARGET_SERVER", "oud"),
        batch_size=int(os.getenv("FLEXT_BATCH_SIZE", "1000")),
    )

    # Configure API client
    api_config = FlextApiSettings(
        base_url=os.getenv("FLEXT_API_URL", "http://localhost:8000"),
        timeout=int(os.getenv("FLEXT_API_TIMEOUT", "30")),
    )

    print("Configuration loaded successfully")
    print(f"Log level: {settings.log_level}")
    print(f"LDIF batch size: {ldif_config.batch_size}")
    print(f"API base URL: {api_config.base_url}")


if __name__ == "__main__":
    main()```
## Reference

- FLEXT Core Configuration
- Environment Variables
- [Pydantic v2 Documentation](https://docs.pydantic.dev/2.0/)
- Configuration Best Practices
