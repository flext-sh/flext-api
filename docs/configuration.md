# Configuration Guide - flext-api

**Environment and Settings Management for FLEXT HTTP Foundation**

**Version**: 0.9.9 RC | **Updated**: September 17, 2025

This guide covers all configuration options, environment variables, and settings management for flext-api HTTP client and FastAPI applications based on the actual implementation.

---

## 🎯 Configuration Overview

flext-api provides configuration management through:

- **FlextApiConfig**: Main configuration class extending flext-core FlextConfig
- **Environment Variables**: FLEXT*API* prefixed environment variables
- **ClientConfig Models**: Type-safe Pydantic configuration models for HTTP clients
- **AppConfig Models**: FastAPI application configuration through models

---

## 🌍 Environment Variables

All environment variables use the `FLEXT_API_` prefix and are defined in `FlextApiConfig`.

### **Server Configuration**

| Variable              | Type    | Default                                     | Description                |
| --------------------- | ------- | ------------------------------------------- | -------------------------- |
| `FLEXT_API_API_HOST`  | string  | `${FlextConstants.Platform.DEFAULT_HOST}`   | Host address to bind       |
| `FLEXT_API_API_PORT`  | int     | `${FlextConstants.Platform.FLEXT_API_PORT}` | Port number to bind        |
| `FLEXT_API_WORKERS`   | int     | `4`                                         | Number of worker processes |
| `FLEXT_API_API_DEBUG` | boolean | `false`                                     | Enable debug mode          |

### **API Configuration**

| Variable                 | Type   | Default                   | Description      |
| ------------------------ | ------ | ------------------------- | ---------------- |
| `FLEXT_API_API_TITLE`    | string | `FLEXT API`               | API title        |
| `FLEXT_API_API_VERSION`  | string | `0.9.9`                   | API version      |
| `FLEXT_API_API_BASE_URL` | string | `https://api.example.com` | Default base URL |

### **Client Configuration**

| Variable                | Type  | Default                                    | Description                |
| ----------------------- | ----- | ------------------------------------------ | -------------------------- |
| `FLEXT_API_API_TIMEOUT` | float | `${FlextApiConstants.DEFAULT_TIMEOUT}`     | Request timeout in seconds |
| `FLEXT_API_MAX_RETRIES` | int   | `${FlextApiConstants.DEFAULT_MAX_RETRIES}` | Maximum retry attempts     |

---

## ⚙️ Configuration Classes

### **FlextApiConfig**

Main configuration class extending flext-core FlextConfig.

```python
from flext_api.config import FlextApiConfig

# Default configuration
config = FlextApiConfig()

# Access configuration values
print(f"API Host: {config.api_host}")
print(f"API Port: {config.api_port}")
print(f"Timeout: {config.api_timeout}")
```

**Available Properties:**

```python
class FlextApiConfig(FlextConfig):
    # Server configuration
    api_host: str = FlextConstants.Platform.DEFAULT_HOST
    api_port: int = FlextConstants.Platform.FLEXT_API_PORT
    workers: int = 4
    api_debug: bool = False

    # API configuration
    api_title: str = "FLEXT API"
    api_version: str = "0.9.9"
    api_base_url: str = "https://api.example.com"

    # Client configuration
    api_timeout: float = FlextApiConstants.DEFAULT_TIMEOUT
    max_retries: int = FlextApiConstants.DEFAULT_MAX_RETRIES
```

### **ClientConfig Model**

HTTP client configuration model from FlextApiModels.

```python
from flext_api.models import FlextApiModels

config = FlextApiModels.ClientConfig(
    base_url="https://api.enterprise.com",
    timeout=FlextApiConstants.DEFAULT_TIMEOUT,
    max_retries=3,
    headers={
        "User-Agent": "my-service/1.0.0",
        "Accept": "application/json"
    },
    auth_token="your-bearer-token",
    api_key="your-api-key"
)

# Get authentication headers
auth_headers = config.get_auth_header()
all_headers = config.get_default_headers()
```

### **AppConfig Model**

FastAPI application configuration model from FlextApiModels.

```python
from flext_api.models import FlextApiModels

app_config = FlextApiModels.AppConfig(
    title="Enterprise API Service",
    app_version="1.0.0",
    description="Production API using flext-api foundation",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
```

---

## 🔧 Configuration Examples

### **Basic HTTP Client Configuration**

```python
from flext_api import FlextApiClient
from flext_api.config import FlextApiConfig

def basic_client_config():
    """Basic HTTP client with configuration."""

    # Create configuration
    config = FlextApiConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=FlextApiConstants.DEFAULT_TIMEOUT,
        headers={
            "User-Agent": "flext-api-example/1.0.0",
            "Accept": "application/json"
        }
    )

    # Create client with configuration
    client = FlextApiClient(config=config)

    try:
        # Use configured client
        result = client.get("/posts/1")
        if result.is_success:
            response = result.unwrap()
            print(f"Post: {response.body}")
    finally:
        client.close()

# Run example
run(basic_client_config())
```

### **Environment-Based Configuration**

```python
import os
from flext_api.config import FlextApiConfig

# Set environment variables
os.environ['HTTP_BASE_URL'] = 'https://api.production.com'
os.environ['HTTP_TIMEOUT'] = '60'
os.environ['HTTP_AUTH_TOKEN'] = 'prod-token-123'

# Load configuration from environment
config = FlextApiConfig()
config.load_from_environment()

print(f"Base URL: {config.base_url}")
print(f"Timeout: {config.timeout}")
print(f"Has Auth: {config.auth_token is not None}")
```

### **Production FastAPI Configuration**

```python
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

def create_production_api():
    """Create production FastAPI application."""

    # Production configuration
    config = FlextApiModels.AppConfig(
        title="Enterprise Data API",
        app_version="1.2.0",
        description="Production API for enterprise data integration",
        docs_url="/docs",  # Available in production
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Create FastAPI app
    app = create_fastapi_app(config)

    # Add production middleware
    @app.middleware("http")
    def add_security_headers(request, call_next):
        response = call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    return app

app = create_production_api()
```

---

## 🔐 Security Configuration

### **Authentication Setup**

```python
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels

# Bearer Token Authentication
config = FlextApiModels.ClientConfig(
    base_url="https://secure-api.com",
    auth_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    ssl_verify=True,  # Always verify SSL in production
    headers={
        "User-Agent": "secure-client/1.0.0"
    }
)

client = FlextApiClient(config=config)

# API Key Authentication
api_config = FlextApiModels.ClientConfig(
    base_url="https://api-key-service.com",
    api_key="ak_live_1234567890abcdef",
    headers={
        "X-API-Version": "2025-09-17"
    }
)

api_client = FlextApiClient(config=api_config)
```

### **SSL/TLS Configuration**

```python
from flext_api import FlextApiClient

# Secure HTTPS configuration
secure_client = FlextApiClient(
    base_url="https://secure-api.enterprise.com",
    ssl_verify=True,  # Verify SSL certificates (default: True)
    timeout=FlextApiConstants.DEFAULT_TIMEOUT,
    headers={
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
)

# Development configuration (less secure)
dev_client = FlextApiClient(
    base_url=f"http://{FlextConstants["Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}""],  # HTTP allowed for local dev
    ssl_verify=False,  # Only for development
    timeout=FlextApiConstants.DEVELOPMENT_TIMEOUT
)
```

---

## 🚀 Performance Configuration

### **Connection Pool Settings**

```python
from flext_api import FlextApiClient

# High-performance configuration
performance_client = FlextApiClient(
    base_url="https://high-volume-api.com",
    timeout=FlextApiConstants.DEFAULT_TIMEOUT,
    max_connections=100,     # Total connection pool size
    keepalive_connections=20, # Keep-alive connections
    http2=True,              # Enable HTTP/2 (if supported)
    headers={
        "Connection": "keep-alive",
        "Keep-Alive": f"timeout={FlextApiConstants.DEFAULT_TIMEOUT * 2}, max=100"
    }
)
```

### **Timeout Configuration**

```python
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels

# Different timeout strategies
quick_client = FlextApiClient(
    base_url="https://fast-api.com",
    timeout=FlextApiConstants.MONITORING_TIMEOUT  # Quick timeout for fast APIs
)

slow_client = FlextApiClient(
    base_url="https://slow-processing-api.com",
    timeout=FlextApiConstants.MAX_TIMEOUT  # 5 minutes for long-running operations
)

# Per-request timeout override
request = FlextApiModels.HttpRequest(
    method="POST",
    url="/long-process",
    timeout=FlextApiConstants.MAX_TIMEOUT * 2,  # 10 minutes for this specific request
    json={"data": "large dataset"}
)
```

---

## 🔧 Development Configuration

### **Development Environment Setup**

```python
import os
from flext_api.config import FlextApiConfig
from flext_api.app import create_fastapi_app
from flext_api.models import FlextApiModels

def setup_development_environment():
    """Configure for development environment."""

    # Development environment variables
    os.environ['HTTP_BASE_URL'] = f'http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}'
    os.environ['HTTP_TIMEOUT'] = str(FlextApiConstants.DEVELOPMENT_TIMEOUT)
    os.environ['FASTAPI_HOST'] = FlextConstants.Platform.DEFAULT_HOST
    os.environ['FASTAPI_PORT'] = str(FlextConstants.Platform.FLEXT_API_PORT)
    os.environ['FASTAPI_RELOAD'] = 'true'
    os.environ['FASTAPI_LOG_LEVEL'] = 'debug'

    # HTTP client configuration
    http_config = FlextApiConfig(
        base_url=f"http://{FlextConstants["Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}""],
        timeout=FlextApiConstants.DEVELOPMENT_TIMEOUT,
        ssl_verify=False,  # Development only
        headers={
            "X-Development": "true",
            "User-Agent": "flext-api-dev/0.9.9"
        }
    )

    # FastAPI configuration
    app_config = FlextApiModels.AppConfig(
        title="Development API",
        app_version="0.9.9 RC",
        description="Development API with debug features",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    return http_config, app_config

# Use in development
http_config, app_config = setup_development_environment()
```

### **Testing Configuration**

```python
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels

# Test configuration with mock server
test_client = FlextApiClient(
    base_url="https://httpbin.org",  # Public testing API
    timeout=FlextApiConstants.MONITORING_TIMEOUT,
    headers={
        "X-Test-Mode": "true",
        "User-Agent": "flext-api-test/0.9.9"
    }
)

# Configuration for unit tests
unit_test_config = FlextApiModels.ClientConfig(
    base_url="http://mock-server:8080",
    timeout=FlextApiConstants.TESTING_TIMEOUT,  # Quick timeout for unit tests
    max_retries=1,
    ssl_verify=False
)
```

---

## 🏭 Production Configuration

### **Production HTTP Client**

```python
import os
from flext_api import FlextApiClient
from flext_api.config import FlextApiConfig

def create_production_client():
    """Create production-ready HTTP client."""

    # Load from environment variables
    config = FlextApiConfig(
        base_url=os.getenv('PRODUCTION_API_URL'),
        timeout=float(os.getenv('HTTP_TIMEOUT', '30')),
        max_retries=int(os.getenv('HTTP_MAX_RETRIES', '3')),
        auth_token=os.getenv('PRODUCTION_API_TOKEN'),
        ssl_verify=True,  # Always verify SSL in production
        headers={
            "User-Agent": f"enterprise-service/{os.getenv('SERVICE_VERSION', '1.0.0')}",
            "Accept": "application/json",
            "X-Service-Name": os.getenv('SERVICE_NAME', 'flext-api-client')
        }
    )

    return FlextApiClient(config=config)

# Production client instance
production_client = create_production_client()
```

### **Production FastAPI Application**

```bash
# Production environment variables
export FASTAPI_HOST=0.0.0.0
export FASTAPI_PORT=${FlextConstants.Platform.FLEXT_API_PORT}
export FASTAPI_WORKERS=4
export FASTAPI_LOG_LEVEL=info
export HTTPS_ONLY=true
export SSL_VERIFY=true
export MAX_REQUEST_SIZE=10485760  # 10MB
```

```python
def create_production_fastapi():
    """Create production FastAPI application."""

    config = FlextApiModels.AppConfig(
        title="Enterprise Production API",
        app_version=os.getenv('SERVICE_VERSION', '1.0.0'),
        description="Production API for enterprise data integration",
        docs_url=None,  # Disable docs in production for security
        redoc_url=None,
        openapi_url=None
    )

    app = create_fastapi_app(config)

    # Production security middleware
    @app.middleware("http")
    def security_middleware(request, call_next):
        # Add security headers
        response = call_next(request)
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        })
        return response

    return app
```

---

## 🔍 Configuration Validation

### **Environment Validation**

```python
from flext_api.config import FlextApiConfig
from flext_core import FlextResult

def validate_production_config() -> FlextResult[FlextApiConfig]:
    """Validate production configuration."""

    try:
        config = FlextApiConfig()

        # Validate required settings
        if not config.base_url.startswith('https://'):
            return FlextResult[FlextApiConfig].fail(
                "Production requires HTTPS base URL"
            )

        if config.timeout < 30:
            return FlextResult[FlextApiConfig].fail(
                "Production timeout must be at least 30 seconds"
            )

        if not config.ssl_verify:
            return FlextResult[FlextApiConfig].fail(
                "SSL verification required in production"
            )

        return FlextResult[FlextApiConfig].ok(config)

    except Exception as e:
        return FlextResult[FlextApiConfig].fail(
            f"Configuration validation failed: {e}"
        )
```

### **Configuration Health Check**

```python
def config_health_check():
    """Check configuration health."""

    config = FlextApiConfig()
    client = FlextApiClient(config=config)

    try:
        # Test basic connectivity
        result = client.get("/health")

        if result.is_success:
            print("✅ Configuration healthy")
            return True
        else:
            print(f"❌ Configuration issue: {result.error}")
            return False

    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False
    finally:
        client.close()
```

---

## 📊 Configuration Best Practices

### **Security Best Practices**

1. **Never hardcode secrets** in configuration files
2. **Use environment variables** for sensitive data
3. **Always enable SSL verification** in production
4. **Rotate authentication tokens** regularly
5. **Use minimal permissions** for API keys

### **Performance Best Practices**

1. **Reuse HTTP clients** instead of creating new instances
2. **Configure appropriate timeouts** based on API characteristics
3. **Use connection pooling** for high-volume applications
4. **Enable HTTP/2** when supported by target APIs
5. **Monitor connection usage** and adjust pool sizes

### **Development Best Practices**

1. **Use different configurations** for dev/test/prod environments
2. **Validate configuration** at startup
3. **Log configuration issues** clearly
4. **Test with realistic configurations** in staging
5. **Document configuration requirements** for deployment

---

**Configuration Summary**: flext-api provides comprehensive configuration management through environment variables, type-safe configuration classes, and flexible runtime configuration. All configurations integrate seamlessly with FLEXT ecosystem patterns and support both development and production environments.
