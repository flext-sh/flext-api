# Configuration

flext-api uses Pydantic v2 models for configuration. This page documents the models that exist today and how to use them. No plugin‑specific settings are implemented.

## Client configuration

`FlextApiModels.ClientConfig` defines the HTTP client settings.

```python
from flext_api import FlextApiModels

cfg = FlextApiModels.ClientConfig(
    base_url="https://httpbin.org",
    timeout=30.0,
    max_retries=3,
    headers={"User-Agent": "flext-api/0.9.0"},
    auth_token=None,
    api_key=None,
)
```

Fields:
- `base_url: str` – required, must start with http/https
- `timeout: float` – seconds
- `max_retries: int` – non‑negative
- `headers: dict[str, str]` – optional default headers
- `auth_token: str | None` – optional bearer token
- `api_key: str | None` – optional API key (added as Bearer for convenience)

## FastAPI application configuration

`FlextApiModels.AppConfig` configures the FastAPI app created by `create_fastapi_app`.

```python
from flext_api import FlextApiModels, create_fastapi_app

app = create_fastapi_app(
    FlextApiModels.AppConfig(
        title="Example API",
        app_version="1.0.0",
        description="FlextAPI application",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
)
```

Environment variables
- flext-api does not define its own env var loader here; prefer configuring via code or your process manager.
        case_sensitive = False
```

---

## 🔌 Plugin Configuration

### **Caching Plugin Configuration**

```python
from flext_api import FlextApiCachingPlugin
from flext_core import FlextConfig
from pydantic import Field
from typing import Optional

class CachingPluginConfig(FlextConfig):
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
from flext_core import FlextConfig
from pydantic import Field
from typing import List

class RetryPluginConfig(FlextConfig):
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
from flext_core import FlextLogger
import yaml

logger = FlextLogger(__name__)

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
from flext_core import FlextLogger

logger = FlextLogger(__name__)

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
