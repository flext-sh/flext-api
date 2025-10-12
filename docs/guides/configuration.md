# Configuration Guide

Comprehensive guide for configuring FLEXT-API applications with environment variables, configuration files, and runtime settings.

## Configuration Sources

FLEXT-API supports multiple configuration sources that are merged together:

1. **Environment Variables** (highest priority)
2. **Configuration Files** (.env, .toml, .YAML, .JSON)
3. **Default Values** (lowest priority)

## Environment-Based Configuration

### Environment Variables

```bash
# Set environment variables
export FLEXT_API_TITLE="My API"
export FLEXT_API_VERSION="1.0.0"
export FLEXT_API_DEBUG="true"
export FLEXT_API_CORS_ORIGINS='["http://localhost:3000", "https://app.company.com"]'
export FLEXT_API_RATE_LIMIT="1000"
```

### Configuration File Support

**TOML Configuration** (`config.toml`):

```toml
[api]
title = "Enterprise API"
version = "2.0.0"
description = "Enterprise-grade REST API"
debug = false

[cors]
origins = ["https://app.company.com", "https://REDACTED_LDAP_BIND_PASSWORD.company.com"]
methods = ["GET", "POST", "PUT", "DELETE"]
headers = ["Content-Type", "Authorization"]

[rate_limit]
requests_per_minute = 1000
burst_limit = 100

[logging]
level = "INFO"
format = "json"
```

**YAML Configuration** (`config.yaml`):

```yaml
api:
  title: "Enterprise API"
  version: "2.0.0"
  description: "Enterprise-grade REST API"
  debug: false

cors:
  origins:
    - "https://app.company.com"
    - "https://REDACTED_LDAP_BIND_PASSWORD.company.com"
  methods: ["GET", "POST", "PUT", "DELETE"]

rate_limit:
  requests_per_minute: 1000
  burst_limit: 100
```

**JSON Configuration** (`config.json`):

```json
{
  "api": {
    "title": "Enterprise API",
    "version": "2.0.0",
    "description": "Enterprise-grade REST API",
    "debug": false
  },
  "cors": {
    "origins": ["https://app.company.com"],
    "methods": ["GET", "POST"]
  }
}
```

## Runtime Configuration

### Programmatic Configuration

```python
from flext_api import FlextApiConfig

# Create configuration programmatically
config = FlextApiConfig(
    title="My Custom API",
    version="1.0.0",
    description="API configured at runtime",
    debug=True,
    cors_origins=["http://localhost:3000"],
    rate_limit=500,
    custom_setting="custom_value"
)

# Apply to FastAPI app
app = create_fastapi_app(config=config)
```

## Configuration Options

### Core API Settings

| Option        | Type | Default         | Description                 |
| ------------- | ---- | --------------- | --------------------------- |
| `title`       | str  | "FLEXT API"     | API title for documentation |
| `version`     | str  | "0.9.9"         | API version                 |
| `description` | str  | ""              | API description             |
| `docs_url`    | str  | "/docs"         | OpenAPI docs URL            |
| `redoc_url`   | str  | "/redoc"        | ReDoc URL                   |
| `openapi_url` | str  | "/openapi.JSON" | OpenAPI schema URL          |
| `debug`       | bool | false           | Enable debug mode           |

### CORS Configuration

| Option             | Type | Default | Description               |
| ------------------ | ---- | ------- | ------------------------- |
| `cors_origins`     | list | []      | Allowed CORS origins      |
| `cors_methods`     | list | ["GET"] | Allowed CORS methods      |
| `cors_headers`     | list | []      | Allowed CORS headers      |
| `cors_credentials` | bool | false   | Allow credentials in CORS |

### Rate Limiting

| Option              | Type | Default | Description                  |
| ------------------- | ---- | ------- | ---------------------------- |
| `rate_limit`        | int  | 100     | Requests per minute limit    |
| `rate_limit_window` | int  | 60      | Rate limit window in seconds |
| `rate_limit_burst`  | int  | 10      | Burst limit above base rate  |

## Advanced Configuration

### Custom Configuration Classes

```python
from flext_api import FlextApiConfig
from pydantic import Field

class CustomApiConfig(FlextApiConfig):
    """Custom API configuration with additional fields."""

    # Core API settings (inherited)
    title: str = "Custom API"
    version: str = "1.0.0"

    # Custom settings
    database_url: str = Field(..., description="Database connection URL")
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    feature_flags: dict = Field(default_factory=dict, description="Feature flags")
    worker_count: int = Field(default=4, ge=1, le=16, description="Number of worker processes")

# Usage
config = CustomApiConfig(
    title="My Custom API",
    database_url="postgresql://user:pass@localhost/mydb",
    feature_flags={"new_feature": True, "beta_feature": False}
)
```

### Configuration Validation

```python
from pydantic import ValidationError

try:
    config = CustomApiConfig(
        title="My API",
        database_url="invalid-url",  # This will fail validation
        worker_count=20  # This will fail validation (max 16)
    )
except ValidationError as e:
    print(f"Configuration validation failed: {e}")
```

## Configuration in Applications

### FastAPI Integration

```python
from flext_api import create_fastapi_app, FlextApiConfig

# Load configuration
config = FlextApiConfig())

# Create application with configuration
app = create_fastapi_app(config=config)

# Access configuration in routes
@app.get("/config")
async def get_config():
    """Get current API configuration."""
    return {
        "title": config.title,
        "version": config.version,
        "debug": config.debug,
        "environment": config.environment
    }
```

### Dependency Injection

```python
from flext_core import FlextCore

# Register configuration in container
container = FlextCore.Container.get_global()
container.register("api_config", config)

# Access configuration in services
class UserService(FlextCore.Service):
    def __init__(self):
        super().__init__()
        self.container = FlextCore.Container.get_global()
        self.config_result = self.container.get("api_config")

    def get_config_value(self, key: str):
        """Get configuration value."""
        if self.config_result.is_success:
            config = self.config_result.unwrap()
            return getattr(config, key, None)
        return None
```

## Environment Management

### Environment Detection

```python
from flext_api import FlextApiConfig

# Automatic environment detection
config = FlextApiConfig()
```

### Environment Variables

```python
import os
from flext_api import FlextApiConfig

# Environment variable configuration
config = FlextApiConfig(
    title=os.getenv("API_TITLE", "Default API"),
    version=os.getenv("API_VERSION", "1.0.0"),
    debug=os.getenv("API_DEBUG", "false").lower() == "true",
    cors_origins=os.getenv("CORS_ORIGINS", "[]"),  # JSON list
    rate_limit=int(os.getenv("RATE_LIMIT", "100"))
)
```

## Configuration Best Practices

### Security Considerations

```python
# Sensitive configuration (use environment variables or secrets management)
config = FlextApiConfig(
    database_url=os.getenv("DATABASE_URL"),  # Required env var
    jwt_secret=os.getenv("JWT_SECRET"),     # Required env var
    api_key=os.getenv("API_KEY"),           # Required env var
)

# Validate required configuration
required_vars = ["DATABASE_URL", "JWT_SECRET", "API_KEY"]
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")
```

### Production Configuration

```python
# Production-ready configuration
prod_config = FlextApiConfig(
    title="Production API",
    version="1.0.0",
    description="Production enterprise API",
    debug=False,  # Disable debug in production
    docs_url=None,  # Disable docs in production
    redoc_url=None,  # Disable redoc in production
    cors_origins=["https://app.company.com"],  # Specific origins only
    rate_limit=1000,  # Higher rate limit for production
    ssl_certificate="/path/to/cert.pem",
    ssl_key="/path/to/key.pem"
)
```

## Configuration Validation

### Runtime Validation

```python
def validate_configuration(config: FlextApiConfig):
    """Validate configuration at runtime."""
    errors = []

    # Validate required fields
    if not config.title:
        errors.append("API title is required")

    if not config.version:
        errors.append("API version is required")

    # Validate CORS configuration
    if config.cors_origins:
        for origin in config.cors_origins:
            if not origin.startswith(("http://", "https://")):
                errors.append(f"Invalid CORS origin: {origin}")

    # Validate rate limiting
    if config.rate_limit <= 0:
        errors.append("Rate limit must be positive")

    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

    return True
```

### Configuration Testing

```python
import pytest
from flext_api import FlextApiConfig

def test_configuration_validation():
    """Test configuration validation."""
    # Valid configuration
    config = FlextApiConfig(
        title="Test API",
        version="1.0.0",
        cors_origins=["https://example.com"]
    )

    assert validate_configuration(config)

    # Invalid configuration
    invalid_config = FlextApiConfig(
        title="",  # Empty title
        version="1.0.0"
    )

    with pytest.raises(ValueError, match="API title is required"):
        validate_configuration(invalid_config)
```

## Configuration Management

### Configuration Reloading

```python
from flext_api import FlextApiConfig
import threading
import time

class ConfigurationManager:
    """Manage configuration with hot reloading."""

    def __init__(self):
        self.config = FlextApiConfig()
        self.last_modified = time.time()
        self.lock = threading.Lock()

    def reload_config(self):
        """Reload configuration from files."""
        with self.lock:
            new_config = FlextApiConfig()

            # Validate new configuration
            if self._validate_config_change(new_config):
                self.config = new_config
                self.last_modified = time.time()
                print("Configuration reloaded successfully")

    def get_config(self) -> FlextApiConfig:
        """Get current configuration."""
        with self.lock:
            return self.config

    def _validate_config_change(self, new_config: FlextApiConfig) -> bool:
        """Validate configuration changes."""
        # Ensure critical settings don't change unexpectedly
        critical_fields = ["title", "version", "debug"]

        for field in critical_fields:
            if getattr(self.config, field) != getattr(new_config, field):
                print(f"Warning: {field} changed during reload")
                # Could trigger alerts or require approval

        return True
```

This configuration system provides comprehensive support for managing API settings across different environments and deployment scenarios.
