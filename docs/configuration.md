# Configuration Management

**FLEXT API configuration patterns and environment management**

> **Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > [flext-api](../README.md) > Configuration

---

## 🎯 Configuration Overview

FLEXT API uses **FlextBaseSettings** patterns from flext-core for type-safe configuration management across all HTTP client operations, FastAPI applications, and plugin systems.

### **Configuration Sources**

1. **Environment Variables** - Runtime configuration (development/production)
2. **YAML Configuration Files** - Complex structured settings
3. **Python Settings Classes** - Type-safe configuration with validation
4. **Plugin Configuration** - Extensible plugin-specific settings

---

## 🔧 Environment Variables

### **Core Service Configuration**

```bash
# HTTP Client Configuration
FLEXT_API_CLIENT_TIMEOUT=30              # Default client timeout in seconds
FLEXT_API_CLIENT_MAX_RETRIES=3          # Default retry attempts
FLEXT_API_CLIENT_BASE_URL=""            # Default base URL (optional)

# FastAPI Application Configuration
FLEXT_API_HOST="0.0.0.0"               # Server bind address
FLEXT_API_PORT=8000                    # Server port
FLEXT_API_WORKERS=1                    # Number of worker processes

# Logging Configuration
FLEXT_LOG_LEVEL="INFO"                 # Logging level (DEBUG, INFO, WARNING, ERROR)
FLEXT_LOG_FORMAT="json"                # Log format (json, text)
FLEXT_LOG_CORRELATION_ID=true          # Enable correlation ID tracking

# Plugin System Configuration
FLEXT_API_PLUGINS_ENABLED=true         # Enable plugin system
FLEXT_API_CACHING_TTL=300              # Default cache TTL in seconds
FLEXT_API_RETRY_BACKOFF_FACTOR=2.0     # Exponential backoff multiplier
```

### **Integration Configuration**

```bash
# FLEXT-Core Integration
FLEXT_CONTAINER_MODE="global"          # Use global DI container
FLEXT_RESULT_STRICT_MODE=true          # Enforce FlextResult usage

# Observability Integration
FLEXT_METRICS_ENABLED=true             # Enable metrics collection
FLEXT_TRACING_ENABLED=true             # Enable distributed tracing
FLEXT_HEALTH_CHECK_INTERVAL=30         # Health check frequency

# Authentication Integration
FLEXT_AUTH_ENABLED=false               # Enable authentication middleware
FLEXT_AUTH_SERVICE_URL=""              # Authentication service endpoint
```

---

## ⚙️ Configuration Classes

### **HTTP Client Configuration**

```python
from flext_api import FlextApiClientConfig
from flext_core import FlextBaseSettings
from pydantic import Field
from typing import Optional, Dict, Any

class FlextApiClientConfig(FlextBaseSettings):
    """HTTP client configuration with validation."""

    base_url: str = Field(..., description="Base URL for HTTP requests")
    timeout: float = Field(default=30.0, gt=0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    headers: Dict[str, str] = Field(default_factory=dict, description="Default headers")

    # Plugin configuration
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, gt=0, description="Cache TTL in seconds")

    # SSL and security
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ssl_context: Optional[Any] = Field(default=None, description="Custom SSL context")

    class Config:
        env_prefix = "FLEXT_API_CLIENT_"
        case_sensitive = False
```

### **FastAPI Application Configuration**

```python
from flext_core import FlextBaseSettings
from pydantic import Field
from typing import List, Optional

class FlextApiAppConfig(FlextBaseSettings):
    """FastAPI application configuration."""

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server bind address")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, description="Number of worker processes")

    # Application settings
    debug: bool = Field(default=False, description="Enable debug mode")
    reload: bool = Field(default=False, description="Enable auto-reload")
    access_log: bool = Field(default=True, description="Enable access logging")

    # CORS configuration
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")

    # Health check configuration
    health_check_path: str = Field(default="/health", description="Health check endpoint")
    ready_check_path: str = Field(default="/ready", description="Readiness check endpoint")

    class Config:
        env_prefix = "FLEXT_API_"
        case_sensitive = False
```

---

## 🔌 Plugin Configuration

### **Caching Plugin Configuration**

```python
from flext_api import FlextApiCachingPlugin
from flext_core import FlextBaseSettings
from pydantic import Field
from typing import Optional

class CachingPluginConfig(FlextBaseSettings):
    """Caching plugin configuration."""

    enabled: bool = Field(default=True, description="Enable caching plugin")
    ttl: int = Field(default=300, gt=0, description="Default cache TTL in seconds")
    max_size: int = Field(default=1000, gt=0, description="Maximum cache entries")

    # Cache key configuration
    include_headers: bool = Field(default=False, description="Include headers in cache key")
    include_query_params: bool = Field(default=True, description="Include query params in cache key")

    # Redis configuration (optional)
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    redis_key_prefix: str = Field(default="flext_api:", description="Redis key prefix")

    class Config:
        env_prefix = "FLEXT_API_CACHING_"
```

### **Retry Plugin Configuration**

```python
from flext_api import FlextApiRetryPlugin
from flext_core import FlextBaseSettings
from pydantic import Field
from typing import List

class RetryPluginConfig(FlextBaseSettings):
    """Retry plugin configuration."""

    enabled: bool = Field(default=True, description="Enable retry plugin")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    backoff_factor: float = Field(default=2.0, gt=1.0, description="Exponential backoff multiplier")

    # Retry conditions
    retry_status_codes: List[int] = Field(
        default=[408, 429, 500, 502, 503, 504],
        description="HTTP status codes to retry"
    )
    retry_exceptions: List[str] = Field(
        default=["TimeoutError", "ConnectionError"],
        description="Exception types to retry"
    )

    # Timing configuration
    initial_delay: float = Field(default=1.0, gt=0, description="Initial retry delay in seconds")
    max_delay: float = Field(default=60.0, gt=0, description="Maximum retry delay in seconds")

    class Config:
        env_prefix = "FLEXT_API_RETRY_"
```

---

## 📁 Configuration Files

### **YAML Configuration Example**

```yaml
# config/flext-api.yaml
flext_api:
  client:
    base_url: "https://api.example.com"
    timeout: 30.0
    max_retries: 3
    headers:
      User-Agent: "FLEXT-API/0.9.0"
      Accept: "application/json"

  plugins:
    caching:
      enabled: true
      ttl: 300
      max_size: 1000

    retry:
      enabled: true
      max_retries: 3
      backoff_factor: 2.0
      retry_status_codes: [408, 429, 500, 502, 503, 504]

  server:
    host: "0.0.0.0"
    port: 8000
    workers: 1
    debug: false

  observability:
    metrics_enabled: true
    tracing_enabled: true
    health_check_interval: 30
```

### **Loading Configuration**

```python
from flext_api import create_flext_api
from flext_core import get_logger
import yaml

logger = get_logger(__name__)

def load_configuration(config_path: str = "config/flext-api.yaml"):
    """Load configuration from YAML file with environment override."""

    # Load base configuration from file
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)

    # Create API with configuration
    api = create_flext_api(config=config_data['flext_api'])

    logger.info("Configuration loaded successfully", config_path=config_path)
    return api
```

---

## 🔒 Security Configuration

### **SSL/TLS Configuration**

```python
import ssl
from flext_api import FlextApiClientConfig

# Create custom SSL context
ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_context.check_hostname = False  # Only for development
ssl_context.verify_mode = ssl.CERT_NONE  # Only for development

# Configure client with SSL
config = FlextApiClientConfig(
    base_url="https://internal-api.company.com",
    verify_ssl=True,
    ssl_context=ssl_context
)
```

### **Authentication Configuration**

```python
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def configure_authentication():
    """Configure API client with authentication."""

    api = create_flext_api()

    # Create client with authentication headers
    client_result = api.flext_api_create_client({
        "base_url": "https://api.example.com",
        "headers": {
            "Authorization": "Bearer your-jwt-token",
            "X-API-Key": "your-api-key"
        }
    })

    if client_result.success:
        logger.info("Authenticated client created successfully")
        return client_result.data
    else:
        logger.error("Authentication configuration failed", error=client_result.error)
        return None
```

---

## 🔧 Development Configuration

### **Development Settings**

```python
# config/development.py
from flext_api import FlextApiClientConfig, FlextApiAppConfig

# Development HTTP client configuration
CLIENT_CONFIG = FlextApiClientConfig(
    base_url="http://localhost:3000",
    timeout=10.0,
    max_retries=1,
    verify_ssl=False
)

# Development server configuration
APP_CONFIG = FlextApiAppConfig(
    host="127.0.0.1",
    port=8000,
    debug=True,
    reload=True,
    workers=1
)
```

### **Production Settings**

```python
# config/production.py
from flext_api import FlextApiClientConfig, FlextApiAppConfig

# Production HTTP client configuration
CLIENT_CONFIG = FlextApiClientConfig(
    base_url="https://api.production.com",
    timeout=30.0,
    max_retries=5,
    verify_ssl=True,
    headers={
        "User-Agent": "FLEXT-API-Production/0.9.0"
    }
)

# Production server configuration
APP_CONFIG = FlextApiAppConfig(
    host="0.0.0.0",
    port=8000,
    debug=False,
    reload=False,
    workers=4,
    access_log=True
)
```

---

## 🧪 Testing Configuration

### **Test Environment Configuration**

```python
# tests/conftest.py
import pytest
from flext_api import create_flext_api, FlextApiClientConfig

@pytest.fixture
def test_api_config():
    """Test configuration for FLEXT API."""
    return FlextApiClientConfig(
        base_url="http://httpbin.org",  # Reliable test endpoint
        timeout=5.0,
        max_retries=1,
        verify_ssl=True
    )

@pytest.fixture
def test_api(test_api_config):
    """Create test API instance."""
    return create_flext_api(client_config=test_api_config)
```

---

## 📚 Related Documentation

- **[Getting Started](getting-started.md)** - Basic setup and installation
- **[Architecture](architecture.md)** - System design and patterns
- **[Integration](integration.md)** - Ecosystem integration patterns
- **[Development](development.md)** - Development workflows
- **[Troubleshooting](troubleshooting.md)** - Common configuration issues

---

**Configuration Management v0.9.0** - Type-safe settings and environment management for FLEXT API HTTP foundation library.
