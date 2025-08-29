# Python Module Organization & Semantic Patterns

**The FLEXT API Module Architecture & Best Practices for HTTP Foundation Library**

---

## 🏗️ **Module Architecture Overview**

FLEXT API implements a **layered module architecture** following Clean Architecture and Domain-Driven Design principles, serving as the HTTP foundation library for all 32 projects in the FLEXT ecosystem. This structure provides consistent HTTP client functionality, query/response builders, and FastAPI integration patterns.

### **Core Design Principles**

1. **HTTP Foundation**: Unified HTTP interface for all ecosystem projects
2. **Composition over Inheritance**: FlextApi class composes functionality from builders and clients
3. **Type-Safe Everything**: Comprehensive type hints with MyPy strict compliance
4. **Railway-Oriented**: FlextResult[T] threading through all HTTP operations
5. **Plugin Architecture**: Extensible HTTP client with caching, retry, and circuit breaker patterns
6. **FLEXT-Core Compliance**: Follows flext-core patterns for ecosystem consistency

---

## 📁 **Module Structure & Responsibilities**

### **Root Module (Public API Gateway)**

```python
# Main entry point - used by all ecosystem projects
src/flext_api/
├── __init__.py              # 🎯 Public API gateway for HTTP foundation
├── api.py                   # 🎯 FlextApi main service class
├── main.py                  # 🎯 FastAPI application entry point
└── py.typed                 # 🎯 Type information marker
```

**Responsibility**: Establish the public HTTP contracts that all ecosystem projects depend on.

**Import Pattern**:

```python
# All ecosystem projects start here
from flext_api import create_flext_api, FlextApiClient, FlextApiBuilder
```

### **Core HTTP Layer**

```python
# HTTP client and communication core
├── client.py                # 🚀 FlextApiClient - HTTP client with plugins
├── builder.py               # 🚀 FlextApiBuilder - Query/response builders
├── app.py                   # 🚀 FastAPI application factory
└── constants.py             # 🚀 HTTP constants and enums
```

**Responsibility**: Provide the HTTP communication foundation and builder patterns.

**Usage Pattern**:

```python
from flext_api.client import FlextApiClient, FlextApiClientConfig
from flext_api.builder import FlextApiQueryBuilder, FlextApiResponseBuilder

def setup_http_client() -> FlextResult[FlextApiClient]:
    config = FlextApiClientConfig(base_url="https://api.example.com")
    return FlextResult[None].ok(FlextApiClient(config))
```

### **Configuration & Infrastructure Layer**

```python
# Configuration and system integration
├── config.py                # ⚙️ FlextApiSettings - HTTP configuration
├── infrastructure/          # ⚙️ Infrastructure concerns
│   ├── __init__.py
│   └── config.py            # ⚙️ Advanced configuration patterns
├── exceptions.py            # ⚙️ HTTP-specific exceptions
├── fields.py                # ⚙️ Field definitions and validators
├── storage.py               # ⚙️ Storage and caching abstractions
└── types.py                 # ⚙️ Type definitions and aliases
```

**Responsibility**: Handle HTTP configuration, infrastructure concerns, and type system.

**Configuration Pattern**:

```python
from flext_api.config import FlextApiSettings

class ProjectHttpSettings(FlextApiSettings):
    default_timeout: int = 30
    max_retries: int = 3
    enable_caching: bool = True

    class Config:
        env_prefix = "PROJECT_HTTP_"
```

### **Domain-Driven Design Layer**

```python
# DDD implementation for HTTP domain
├── domain/                  # 🏛️ HTTP domain modeling
│   ├── __init__.py
│   ├── entities.py          # 🏛️ HTTP domain entities (ApiRequest, etc.)
│   └── value_objects.py     # 🏛️ HTTP value objects (URL, Headers, etc.)
```

**Responsibility**: Provide rich domain modeling for HTTP concepts following DDD principles.

**Domain Modeling Pattern**:

```python
from flext_api.domain.entities import ApiRequest
from flext_api.domain.value_objects import HttpUrl, HttpHeaders

class ApiRequest(FlextModels.Entity):
    method: str
    url: HttpUrl
    headers: HttpHeaders
    timeout: float = 30.0

    def validate_domain_rules(self) -> FlextResult[None]:
        if self.timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")
        return FlextResult[None].ok(None)

    def with_retry(self) -> FlextResult[ApiRequest]:
        return self.copy_with(retry_count=self.retry_count + 1)

class HttpUrl(FlextModels.Value):
    url: str

    def __post_init__(self):
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

    @property
    def domain(self) -> str:
        from urllib.parse import urlparse
        return urlparse(self.url).netloc
```

---

## 🎯 **Semantic Naming Conventions**

### **Public API Naming (FlextApiXxx)**

All public exports use the `FlextApi` prefix for clear namespace separation:

```python
# Core HTTP patterns
FlextApi                     # Main HTTP service facade
FlextApiClient              # HTTP client with plugins
FlextApiBuilder             # Query/response builder facade
FlextApiQueryBuilder        # Query construction builder
FlextApiResponseBuilder     # Response construction builder
FlextApiClientConfig        # HTTP client configuration

# HTTP domain entities
FlextApiRequest             # HTTP request domain entity
FlextApiResponse            # HTTP response domain entity
FlextApiPlugin              # HTTP client plugin base class
FlextApiCachingPlugin       # Caching plugin implementation
FlextApiRetryPlugin         # Retry plugin implementation
FlextApiCircuitBreakerPlugin # Circuit breaker plugin implementation

# HTTP value objects
FlextApiUrl                 # URL value object
FlextApiHeaders             # Headers value object
FlextApiMethod              # HTTP method enum
FlextApiStatus              # HTTP status enum

# Configuration patterns
FlextApiSettings            # HTTP configuration settings
FlextApiClientStatus        # Client status enum
FlextApiClientProtocol      # HTTP protocol enum
```

**Rationale**: Clear namespace separation prevents conflicts with ecosystem projects and provides obvious HTTP context.

### **Module-Level Naming**

```python
# Module names are HTTP-focused and descriptive
api.py                      # Contains FlextApi main service
client.py                   # Contains FlextApiClient and HTTP client patterns
builder.py                  # Contains FlextApiBuilder and construction patterns
config.py                   # Contains FlextApiSettings and configuration
app.py                      # Contains FastAPI application factory
main.py                     # Contains FastAPI application entry point
```

**Pattern**: One primary HTTP concern per module with related utilities.

### **Internal Naming (\_xxx)**

```python
# Internal modules use underscore prefix (currently none in flext-api)
_http_base.py               # Internal HTTP implementation (future)
_client_base.py             # Internal client implementation (future)
_plugin_base.py             # Internal plugin implementation (future)

# Internal functions and classes
def _validate_http_config(config: dict) -> bool:
    """Internal HTTP configuration validation"""

class _InternalHttpHandler:
    """Internal HTTP handler implementation"""
```

**Rule**: Anything with `_` prefix is internal and not part of public API.

---

## 📦 **Import Patterns & Best Practices**

### **Recommended Import Styles**

#### **1. Primary Pattern (Recommended for Ecosystem)**

```python
# Import from main package - gets HTTP foundation needs
from flext_api import create_flext_api, FlextApiClient, FlextApiBuilder
from flext_core import FlextResult, FlextLogger

# Use patterns directly for HTTP operations
def setup_http_service() -> FlextResult[FlextApi]:
    api = create_flext_api()
    return FlextResult[None].ok(api)
```

#### **2. Specific Module Pattern (For Advanced HTTP Usage)**

```python
# Import from specific modules for HTTP clarity
from flext_api.client import FlextApiClient, FlextApiClientConfig
from flext_api.builder import FlextApiQueryBuilder, FlextApiResponseBuilder
from flext_api.config import FlextApiSettings

# More explicit for HTTP-specific functionality
```

#### **3. Plugin System Pattern**

```python
# Import plugins for HTTP client extension
from flext_api import (
    FlextApiCachingPlugin,
    FlextApiRetryPlugin,
    FlextApiCircuitBreakerPlugin,
    create_client_with_plugins
)

# Configure HTTP client with plugins
plugins = [
    FlextApiCachingPlugin(ttl=300),
    FlextApiRetryPlugin(max_retries=3)
]
client = create_client_with_plugins(config, plugins)
```

#### **4. FastAPI Integration Pattern**

```python
# Import FastAPI integration components
from flext_api import flext_api_create_app
from flext_api.main import app
from fastapi import Depends

# FastAPI application with HTTP patterns
app = flext_api_create_app()

@app.get("/health")
async def health_check(api = Depends(create_flext_api)):
    return api.health_check()
```

### **Anti-Patterns (Forbidden)**

```python
# ❌ Don't import everything
from flext_api import *

# ❌ Don't import internal modules (none currently exist)
from flext_api._internal import _InternalClass

# ❌ Don't use deep imports unnecessarily
from flext_api.client import FlextApiClient, _private_http_function

# ❌ Don't alias HTTP core types (confusing across ecosystem)
from flext_api import FlextApiClient as HttpClient  # Breaks ecosystem consistency

# ❌ Don't bypass FlextResult pattern
from flext_api.client import FlextApiClient
client = FlextApiClient(config)  # Should return FlextResult
```

---

## 🏛️ **Architectural Patterns**

### **Layer Separation for HTTP Foundation**

```python
# Each layer has clear HTTP-focused boundaries
┌─────────────────────────────────────┐
│     FastAPI Application Layer       │  # main.py, app.py
│    (Web Framework, HTTP Endpoints)  │
├─────────────────────────────────────┤
│       HTTP Service Layer            │  # api.py (FlextApi facade)
│   (HTTP Business Logic, Validation) │
├─────────────────────────────────────┤
│         HTTP Domain Layer           │  # domain/entities.py, domain/value_objects.py
│    (HTTP Concepts, Business Rules)  │  # ApiRequest, HttpUrl, HttpHeaders
├─────────────────────────────────────┤
│     HTTP Infrastructure Layer       │  # client.py, config.py, storage.py
│  (HTTP Clients, Configuration, I/O) │
├─────────────────────────────────────┤
│       Foundation Layer              │  # From flext-core
│   (FlextResult, FlextModels.Entity, etc.)  │  # FlextConfig, logging
└─────────────────────────────────────┘
```

### **HTTP Dependency Direction**

```python
# Dependencies flow inward (Clean Architecture for HTTP)
FastAPI Layer    →  HTTP Service Layer  →  HTTP Domain Layer  →  Foundation Layer
     ↓                     ↓                      ↓                    ↓
HTTP Infrastructure Layer → HTTP Domain Layer → Foundation Layer   (OK)
```

**Rule**: Higher HTTP layers can depend on lower layers, never the reverse.

### **HTTP Cross-Cutting Concerns**

```python
# Handled via HTTP plugins and decorators
from flext_api import FlextApiCachingPlugin, FlextApiRetryPlugin
from flext_core.decorators import with_correlation_id, with_metrics

class HttpService:
    @with_correlation_id
    @with_metrics("http_service.api_call")
    def make_api_call(self, url: str) -> FlextResult[dict]:
        client_result = self.create_client_with_plugins([
            FlextApiCachingPlugin(ttl=300),
            FlextApiRetryPlugin(max_retries=3)
        ])

        return client_result.flat_map(lambda client: client.get(url))
```

---

## 🔄 **Railway-Oriented Programming for HTTP**

### **HTTP Operation Chain Patterns**

```python
# HTTP request pipeline with error handling
def http_request_pipeline(url: str, data: dict) -> FlextResult[ProcessedResponse]:
    return (
        validate_url(url)
        .flat_map(lambda valid_url: validate_request_data(data))
        .flat_map(lambda valid_data: create_http_client())
        .flat_map(lambda client: client.post(valid_url, json=valid_data))
        .map(lambda response: process_http_response(response))
    )

# HTTP client creation with configuration
def create_configured_client(config: dict) -> FlextResult[FlextApiClient]:
    return (
        validate_http_config(config)
        .map(lambda valid_config: FlextApiClientConfig(**valid_config))
        .flat_map(lambda client_config: FlextApiClient.create(client_config))
    )

# HTTP request with retry and caching
async def http_request_with_resilience(
    client: FlextApiClient,
    request: ApiRequest
) -> FlextResult[ApiResponse]:
    return (
        await client.execute_request(request)
        .recover_async(lambda error: retry_request(client, request))
        .map(lambda response: cache_response(request, response))
    )
```

### **HTTP Plugin Chain Patterns**

```python
# Plugin execution chain
async def execute_http_plugins(
    plugins: List[FlextApiPlugin],
    request: ApiRequest
) -> FlextResult[ApiRequest]:
    processed_request = request

    for plugin in plugins:
        plugin_result = await plugin.before_request(processed_request)
        if plugin_result.is_failure:
            return plugin_result
        processed_request = plugin_result.data

    return FlextResult[None].ok(processed_request)

# Response plugin chain
async def process_http_response_plugins(
    plugins: List[FlextApiPlugin],
    response: ApiResponse
) -> FlextResult[ApiResponse]:
    processed_response = response

    for plugin in reversed(plugins):  # Reverse order for response processing
        plugin_result = await plugin.after_response(processed_response)
        if plugin_result.is_failure:
            return plugin_result
        processed_response = plugin_result.data

    return FlextResult[None].ok(processed_response)
```

---

## 🎯 **HTTP Domain-Driven Design Patterns**

### **HTTP Entity Patterns**

```python
from flext_core import FlextModels.Entity, FlextResult
from flext_api.domain.value_objects import HttpUrl, HttpHeaders

class ApiRequest(FlextModels.Entity):
    """Rich HTTP request entity with business logic"""
    method: str
    url: HttpUrl
    headers: HttpHeaders
    payload: dict | None = None
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def validate_domain_rules(self) -> FlextResult[None]:
        """HTTP request validation business rules"""
        if self.timeout <= 0:
            return FlextResult[None].fail(
                error="Timeout must be positive",
                error_code="INVALID_TIMEOUT"
            )

        if self.method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            return FlextResult[None].fail(
                error=f"Unsupported HTTP method: {self.method}",
                error_code="INVALID_HTTP_METHOD"
            )

        return FlextResult[None].ok(None)

    def increment_retry(self) -> FlextResult[ApiRequest]:
        """Retry logic with domain validation"""
        if self.retry_count >= self.max_retries:
            return FlextResult[None].fail(
                error="Maximum retries exceeded",
                error_code="MAX_RETRIES_EXCEEDED"
            )

        updated_request = self.copy_with(retry_count=self.retry_count + 1)
        updated_request.add_domain_event({
            "type": "RequestRetried",
            "request_id": self.id,
            "retry_count": updated_request.retry_count,
            "correlation_id": self.correlation_id
        })
        return FlextResult[None].ok(updated_request)

    def with_timeout(self, timeout: float) -> FlextResult[ApiRequest]:
        """Timeout modification with validation"""
        if timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")

        return FlextResult[None].ok(self.copy_with(timeout=timeout))

class ApiResponse(FlextModels.Entity):
    """HTTP response entity with metadata"""
    status_code: int
    headers: HttpHeaders
    body: str | dict
    request_id: str
    duration_ms: float
    cached: bool = False

    def validate_domain_rules(self) -> FlextResult[None]:
        """HTTP response validation"""
        if not (100 <= self.status_code <= 599):
            return FlextResult[None].fail("Invalid HTTP status code")

        if self.duration_ms < 0:
            return FlextResult[None].fail("Duration cannot be negative")

        return FlextResult[None].ok(None)

    def success(self) -> bool:
        """HTTP success status check"""
        return 200 <= self.status_code <= 299

    def is_client_error(self) -> bool:
        """HTTP client error status check"""
        return 400 <= self.status_code <= 499

    def is_server_error(self) -> bool:
        """HTTP server error status check"""
        return 500 <= self.status_code <= 599
```

### **HTTP Value Object Patterns**

```python
from flext_core import FlextModels.Value
from urllib.parse import urlparse, urljoin

class HttpUrl(FlextModels.Value):
    """Immutable URL value object with validation"""
    url: str

    def __post_init__(self):
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

        parsed = urlparse(self.url)
        if not parsed.netloc:
            raise ValueError("URL must have a valid domain")

    @property
    def scheme(self) -> str:
        return urlparse(self.url).scheme

    @property
    def domain(self) -> str:
        return urlparse(self.url).netloc

    @property
    def path(self) -> str:
        return urlparse(self.url).path

    @property
    def query(self) -> str:
        return urlparse(self.url).query

    def join(self, path: str) -> HttpUrl:
        """Join URL with path"""
        new_url = urljoin(self.url, path)
        return HttpUrl(new_url)

    def with_query(self, params: dict) -> HttpUrl:
        """Add query parameters"""
        from urllib.parse import urlencode
        separator = "&" if self.query else "?"
        query_string = urlencode(params)
        new_url = f"{self.url}{separator}{query_string}"
        return HttpUrl(new_url)

class HttpHeaders(FlextModels.Value):
    """HTTP headers value object"""
    headers: dict[str, str]

    def __post_init__(self):
        # Normalize header names to lowercase
        self.headers = {k.lower(): v for k, v in self.headers.items()}

    def get(self, name: str) -> str | None:
        """Get header value (case-insensitive)"""
        return self.headers.get(name.lower())

    def with_header(self, name: str, value: str) -> HttpHeaders:
        """Add header"""
        new_headers = {**self.headers, name.lower(): value}
        return HttpHeaders(new_headers)

    def without_header(self, name: str) -> HttpHeaders:
        """Remove header"""
        new_headers = {k: v for k, v in self.headers.items() if k != name.lower()}
        return HttpHeaders(new_headers)

    @property
    def content_type(self) -> str | None:
        return self.get("content-type")

    @property
    def authorization(self) -> str | None:
        return self.get("authorization")

class HttpTimeout(FlextModels.Value):
    """HTTP timeout value object with validation"""
    connect_timeout: float
    read_timeout: float

    def __post_init__(self):
        if self.connect_timeout <= 0:
            raise ValueError("Connect timeout must be positive")
        if self.read_timeout <= 0:
            raise ValueError("Read timeout must be positive")

    @property
    def total_timeout(self) -> float:
        return self.connect_timeout + self.read_timeout

    @classmethod
    def from_total(cls, total: float) -> HttpTimeout:
        """Create timeout from total value"""
        if total <= 0:
            raise ValueError("Total timeout must be positive")
        # Split: 30% connect, 70% read
        connect = total * 0.3
        read = total * 0.7
        return cls(connect, read)
```

---

## 🔧 **HTTP Configuration Patterns**

### **Environment-Aware HTTP Configuration**

```python
from flext_core import FlextConfig
from flext_api.domain.value_objects import HttpTimeout

class HttpClientSettings(FlextConfig):
    """HTTP client configuration with environment variables"""
    default_timeout: float = 30.0
    max_retries: int = 3
    user_agent: str = "FLEXT-API/0.9.0"
    verify_ssl: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5

    class Config:
        env_prefix = "HTTP_CLIENT_"
        env_file = ".env"

    @property
    def timeout_config(self) -> HttpTimeout:
        return HttpTimeout.from_total(self.default_timeout)

    def for_service(self, service_name: str) -> dict:
        """Get configuration for specific service"""
        return {
            "timeout": self.timeout_config,
            "user_agent": f"{self.user_agent} ({service_name})",
            "max_retries": self.max_retries,
            "verify_ssl": self.verify_ssl
        }

class FlextApiSettings(FlextConfig):
    """FLEXT API configuration composition"""
    # Server Configuration
    api_host: str = Field(default="0.0.0.0", env="FLEXT_API_HOST")
    api_port: int = Field(default=8000, env="FLEXT_API_PORT")
    api_workers: int = Field(default=1, env="FLEXT_API_WORKERS")

    # HTTP Client Configuration
    http_client: HttpClientSettings = field(default_factory=HttpClientSettings)

    # Plugin Configuration
    enable_caching: bool = Field(default=True, env="FLEXT_API_ENABLE_CACHING")
    cache_ttl: int = Field(default=300, env="FLEXT_API_CACHE_TTL")
    enable_retry: bool = Field(default=True, env="FLEXT_API_ENABLE_RETRY")
    enable_circuit_breaker: bool = Field(default=False, env="FLEXT_API_ENABLE_CIRCUIT_BREAKER")

    class Config:
        env_prefix = "FLEXT_API_"
        env_nested_delimiter = "__"

    def validate_business_rules(self) -> FlextResult[None]:
        """HTTP-specific business rule validation"""
        errors = []

        if self.api_port < 1 or self.api_port > 65535:
            errors.append("API port must be between 1 and 65535")

        if self.cache_ttl <= 0 and self.enable_caching:
            errors.append("Cache TTL must be positive when caching is enabled")

        if self.http_client.default_timeout <= 0:
            errors.append("HTTP timeout must be positive")

        if errors:
            return FlextResult[None].fail(f"Configuration validation failed: {'; '.join(errors)}")

        return FlextResult[None].ok(None)

# Environment variables example:
# FLEXT_API_HOST=localhost
# FLEXT_API_PORT=8000
# FLEXT_API_ENABLE_CACHING=true
# FLEXT_API_HTTP_CLIENT__DEFAULT_TIMEOUT=60
# HTTP_CLIENT_MAX_RETRIES=5
```

### **Service-Specific HTTP Configuration**

```python
class OracleApiSettings(FlextConfig):
    """Oracle API specific HTTP configuration"""
    base_url: str = Field(env="ORACLE_API_BASE_URL")
    timeout: float = 120.0  # Oracle can be slow
    max_retries: int = 5
    auth_token: str = Field(repr=False, env="ORACLE_API_TOKEN")

    class Config:
        env_prefix = "ORACLE_API_"

class LdapApiSettings(FlextConfig):
    """LDAP API specific HTTP configuration"""
    base_url: str = Field(env="LDAP_API_BASE_URL")
    timeout: float = 30.0
    max_retries: int = 3
    cert_path: str = Field(env="LDAP_API_CERT_PATH")

    class Config:
        env_prefix = "LDAP_API_"

class EcosystemHttpSettings(FlextConfig):
    """HTTP configuration for entire FLEXT ecosystem"""
    oracle: OracleApiSettings = field(default_factory=OracleApiSettings)
    ldap: LdapApiSettings = field(default_factory=LdapApiSettings)
    default: HttpClientSettings = field(default_factory=HttpClientSettings)

    def get_client_config(self, service: str) -> dict:
        """Get HTTP client config for specific ecosystem service"""
        service_config = getattr(self, service, self.default)
        return {
            "base_url": service_config.base_url,
            "timeout": service_config.timeout,
            "max_retries": service_config.max_retries
        }
```

---

## 🚀 **HTTP Performance & Optimization Patterns**

### **HTTP Connection Pooling**

```python
from typing import Dict, Optional
import aiohttp

class HttpConnectionPool:
    """HTTP connection pool management"""

    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self._sessions: Dict[str, aiohttp.ClientSession] = {}

    async def get_session(self, base_url: str) -> FlextResult[aiohttp.ClientSession]:
        """Get or create HTTP session for base URL"""
        if base_url not in self._sessions:
            connector = aiohttp.TCPConnector(limit=self.max_connections)
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            self._sessions[base_url] = session

        return FlextResult[None].ok(self._sessions[base_url])

    async def close_all(self) -> FlextResult[None]:
        """Close all HTTP sessions"""
        for session in self._sessions.values():
            await session.close()
        self._sessions.clear()
        return FlextResult[None].ok(None)

# Usage in HTTP client
class FlextApiClient:
    def __init__(self, config: FlextApiClientConfig):
        self.config = config
        self.connection_pool = HttpConnectionPool()

    async def make_request(self, request: ApiRequest) -> FlextResult[ApiResponse]:
        session_result = await self.connection_pool.get_session(request.url.domain)

        return session_result.flat_map_async(
            lambda session: self._execute_request(session, request)
        )
```

### **HTTP Caching Patterns**

```python
from typing import Optional
import hashlib
import json
from datetime import datetime, timedelta

class HttpCacheEntry:
    """HTTP cache entry with TTL"""
    def __init__(self, response: ApiResponse, ttl: int):
        self.response = response
        self.created_at = datetime.utcnow()
        self.ttl = ttl

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)

class HttpCache:
    """HTTP response cache with TTL support"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, HttpCacheEntry] = {}

    def _generate_cache_key(self, request: ApiRequest) -> str:
        """Generate cache key from request"""
        key_data = {
            "method": request.method,
            "url": request.url.url,
            "headers": dict(sorted(request.headers.headers.items())),
            "payload": request.payload
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, request: ApiRequest) -> FlextResult[Optional[ApiResponse]]:
        """Get cached response if available and not expired"""
        cache_key = self._generate_cache_key(request)

        if cache_key not in self._cache:
            return FlextResult[None].ok(None)

        entry = self._cache[cache_key]
        if entry.is_expired():
            del self._cache[cache_key]
            return FlextResult[None].ok(None)

        return FlextResult[None].ok(entry.response)

    def set(self, request: ApiRequest, response: ApiResponse, ttl: int) -> FlextResult[None]:
        """Cache response with TTL"""
        if not response.success():
            return FlextResult[None].ok(None)  # Don't cache errors

        cache_key = self._generate_cache_key(request)

        # Remove oldest entries if at capacity
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(),
                           key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]

        self._cache[cache_key] = HttpCacheEntry(response, ttl)
        return FlextResult[None].ok(None)

# Caching plugin implementation
class FlextApiCachingPlugin(FlextApiPlugin):
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        self.cache = HttpCache(max_size)
        self.ttl = ttl

    async def before_request(self, request: ApiRequest) -> FlextResult[ApiRequest]:
        """Check cache before making request"""
        if request.method != "GET":
            return FlextResult[None].ok(request)  # Only cache GET requests

        cached_response_result = self.cache.get(request)
        if cached_response_result.success and cached_response_result.data:
            # Mark request as satisfied by cache
            cached_request = request.copy_with(cached_response=cached_response_result.data)
            return FlextResult[None].ok(cached_request)

        return FlextResult[None].ok(request)

    async def after_response(self, response: ApiResponse) -> FlextResult[ApiResponse]:
        """Cache successful responses"""
        # Reconstruct request from response metadata
        request = self._reconstruct_request(response)
        if request and response.success():
            await self.cache.set(request, response, self.ttl)

        return FlextResult[None].ok(response)
```

---

## 🧪 **HTTP Testing Patterns**

### **Test Organization for HTTP**

```python
# Test structure mirrors HTTP source structure
tests/
├── unit/                    # Unit tests (HTTP mocked)
│   ├── test_api.py          # Tests for api.py
│   ├── test_client.py       # Tests for client.py
│   ├── test_builder.py      # Tests for builder.py
│   ├── test_config.py       # Tests for config.py
│   └── domain/              # HTTP domain tests
│       ├── test_entities.py # HTTP entity tests
│       └── test_value_objects.py # HTTP value object tests
├── integration/             # Integration tests (real HTTP)
│   ├── test_http_client.py  # Real HTTP integration
│   ├── test_api_endpoints.py # API endpoint integration
│   └── test_plugins.py      # Plugin integration
├── e2e/                     # End-to-end HTTP workflows
│   └── test_http_workflows.py # Complete HTTP workflows
├── benchmarks/              # HTTP performance tests
│   └── test_http_performance.py # Load and performance tests
├── conftest.py              # Test configuration
└── shared_http_domain.py    # Shared HTTP test domain models
```

### **HTTP FlextResult Testing Patterns**

```python
import pytest
import aioresponses
from flext_api import create_flext_api, FlextApiClient
from flext_core import FlextResult

class TestHttpFlextResultPatterns:
    """Test HTTP operations with FlextResult patterns"""

    def test_api_creation_success(self):
        """Test successful HTTP API creation"""
        api_result = create_flext_api()

        assert isinstance(api_result, FlextApi)
        # API creation always succeeds, but operations may fail

        health_result = api_result.health_check()
        assert isinstance(health_result, FlextResult)
        assert health_result.success
        assert health_result.data["service"] == "FlextApi"

    def test_client_creation_success(self):
        """Test successful HTTP client creation"""
        api = create_flext_api()

        client_result = api.flext_api_create_client({
            "base_url": "https://api.example.com",
            "timeout": 30
        })

        assert isinstance(client_result, FlextResult)
        assert client_result.success
        assert isinstance(client_result.data, FlextApiClient)

    def test_client_creation_failure(self):
        """Test HTTP client creation failure"""
        api = create_flext_api()

        client_result = api.flext_api_create_client({
            "base_url": "invalid-url",  # Invalid URL
            "timeout": -1  # Invalid timeout
        })

        assert isinstance(client_result, FlextResult)
        assert client_result.is_failure
        assert "Invalid URL format" in client_result.error

    @pytest.mark.asyncio
    async def test_http_request_success_chain(self):
        """Test successful HTTP request chain"""
        with aioresponses.aioresponses() as m:
            m.get("https://api.example.com/users", payload={"users": []})

            api = create_flext_api()

            result = (
                api.flext_api_create_client({"base_url": "https://api.example.com"})
                .flat_map_async(lambda client: client.get("/users"))
                .map(lambda response: response.json())
            )

            assert result.success
            assert result.data == {"users": []}

    @pytest.mark.asyncio
    async def test_http_request_failure_propagation(self):
        """Test HTTP request failure propagation"""
        api = create_flext_api()

        result = (
            FlextResult[None].fail("Initial HTTP configuration error")
            .flat_map_async(lambda client: client.get("/users"))  # Should not execute
            .map(lambda response: response.json())  # Should not execute
        )

        assert result.is_failure
        assert result.error == "Initial HTTP configuration error"

class TestHttpDomainPatterns:
    """Test HTTP domain entity behavior"""

    def test_api_request_validation_success(self):
        """Test successful API request validation"""
        from flext_api.domain.entities import ApiRequest
        from flext_api.domain.value_objects import HttpUrl, HttpHeaders

        request = ApiRequest(
            method="GET",
            url=HttpUrl("https://api.example.com/users"),
            headers=HttpHeaders({"Authorization": "Bearer token"}),
            timeout=30.0
        )

        result = request.validate_domain_rules()
        assert result.success

    def test_api_request_validation_failure(self):
        """Test API request validation failure"""
        from flext_api.domain.entities import ApiRequest
        from flext_api.domain.value_objects import HttpUrl, HttpHeaders

        request = ApiRequest(
            method="GET",
            url=HttpUrl("https://api.example.com/users"),
            headers=HttpHeaders({}),
            timeout=-5.0  # Invalid timeout
        )

        result = request.validate_domain_rules()
        assert result.is_failure
        assert "Timeout must be positive" in result.error

    def test_http_url_value_object(self):
        """Test HTTP URL value object behavior"""
        from flext_api.domain.value_objects import HttpUrl

        # Valid URL
        url = HttpUrl("https://api.example.com/users")
        assert url.domain == "api.example.com"
        assert url.scheme == "https"

        # URL joining
        api_url = HttpUrl("https://api.example.com")
        users_url = api_url.join("/users")
        assert users_url.url == "https://api.example.com/users"

        # Invalid URL should raise ValueError
        with pytest.raises(ValueError, match="URL must start with"):
            HttpUrl("invalid-url")

class TestHttpPluginPatterns:
    """Test HTTP plugin system"""

    @pytest.mark.asyncio
    async def test_caching_plugin_hit(self):
        """Test HTTP caching plugin cache hit"""
        from flext_api import FlextApiCachingPlugin
        from flext_api.domain.entities import ApiRequest, ApiResponse

        plugin = FlextApiCachingPlugin(ttl=300)

        # Create request and response
        request = create_test_request()
        response = create_test_response()

        # Cache the response
        await plugin.after_response(response)

        # Request should hit cache
        cached_result = await plugin.before_request(request)
        assert cached_result.success
        # Check if request was marked as cached

    @pytest.mark.asyncio
    async def test_retry_plugin_retry(self):
        """Test HTTP retry plugin retry logic"""
        from flext_api import FlextApiRetryPlugin

        plugin = FlextApiRetryPlugin(max_retries=3)

        # Simulate failed request
        request = create_test_request()

        # Should allow retry
        retry_result = await plugin.on_error(Exception("Connection failed"), request)
        assert retry_result.success

def create_test_request() -> ApiRequest:
    """Helper to create test HTTP request"""
from flext_api.domain.entities import ApiRequest
from flext_api.domain.value_objects import HttpUrl, HttpHeaders

    return ApiRequest(
        method="GET",
        url=HttpUrl("https://api.example.com/test"),
        headers=HttpHeaders({"User-Agent": "Test"}),
        timeout=30.0
    )

def create_test_response() -> ApiResponse:
    """Helper to create test HTTP response"""
from flext_api.domain.entities import ApiResponse
from flext_api.domain.value_objects import HttpHeaders

    return ApiResponse(
        status_code=200,
        headers=HttpHeaders({"Content-Type": "application/json"}),
        body={"message": "success"},
        request_id="test-123",
        duration_ms=150.0
    )
```

---

## 📏 **HTTP Code Quality Standards**

### **HTTP Type Annotation Requirements**

```python
# ✅ Complete HTTP type annotations
def make_http_request(
    client: FlextApiClient,
    method: str,
    url: HttpUrl,
    headers: Optional[HttpHeaders] = None
) -> FlextResult[ApiResponse]:
    """Make HTTP request with complete type safety"""
    request = ApiRequest(method=method, url=url, headers=headers or HttpHeaders({}))
    return client.execute_request(request)

# ✅ Generic HTTP type usage
T = TypeVar('T')

def parse_http_response(
    response: ApiResponse,
    parser: Callable[[str], T]
) -> FlextResult[T]:
    """Generic HTTP response parsing with type safety"""
    if not response.success():
        return FlextResult[None].fail(f"HTTP error: {response.status_code}")

    try:
        parsed_data = parser(response.body)
        return FlextResult[None].ok(parsed_data)
    except Exception as e:
        return FlextResult[None].fail(f"Response parsing failed: {e}")

# ❌ Missing HTTP type annotations
def make_request(client, url):  # Missing types
    return client.get(url)
```

### **HTTP Error Handling Standards**

```python
# ✅ Always use FlextResult for HTTP error handling
def http_get_request(client: FlextApiClient, url: str) -> FlextResult[dict]:
    url_result = validate_http_url(url)
    if url_result.is_failure:
        return url_result

    request_result = client.get(url_result.data)
    if request_result.is_failure:
        return FlextResult[None].fail(f"HTTP request failed: {request_result.error}")

    return FlextResult[None].ok(request_result.data.json())

# ✅ Chain HTTP operations safely
def complex_http_workflow(
    base_url: str,
    auth_token: str
) -> FlextResult[ProcessedData]:
    return (
        create_authenticated_client(base_url, auth_token)
        .flat_map(lambda client: client.get("/data"))
        .flat_map(lambda response: parse_response_data(response))
        .map(lambda data: process_business_logic(data))
    )

# ❌ Never raise exceptions in HTTP business logic
def http_request_bad(client: FlextApiClient, url: str) -> dict:
    if not url.startswith("https://"):
        raise ValueError("URL must be HTTPS")  # Breaks railway pattern

    response = client.get(url)
    if response.status_code != 200:
        raise RuntimeError("Request failed")  # Breaks railway pattern

    return response.json()
```

### **HTTP Documentation Standards**

```python
def execute_http_request_with_plugins(
    client: FlextApiClient,
    request: ApiRequest,
    plugins: List[FlextApiPlugin]
) -> FlextResult[ApiResponse]:
    """
    Execute HTTP request with plugin processing pipeline.

    This function implements the complete HTTP request workflow including
    plugin pre-processing, request execution, and plugin post-processing.
    It follows the railway-oriented programming pattern for consistent
    error handling throughout the HTTP pipeline.

    Args:
        client: HTTP client instance for making requests
        request: HTTP request entity with method, URL, headers, and payload
        plugins: List of HTTP plugins to apply (caching, retry, etc.)

    Returns:
        FlextResult[ApiResponse]: Success contains HTTP response with metadata,
        failure contains detailed error message explaining request or plugin
        failure with correlation ID for debugging

    Example:
        >>> client = FlextApiClient(config)
        >>> request = ApiRequest(method="GET", url=HttpUrl("https://api.example.com"))
        >>> plugins = [FlextApiCachingPlugin(), FlextApiRetryPlugin()]
        >>> result = execute_http_request_with_plugins(client, request, plugins)
        >>> if result.success:
        ...     print(f"Response: {result.data.status_code}")
        ... else:
        ...     print(f"Error: {result.error}")
    """
    return (
        process_request_plugins(plugins, request)
        .flat_map_async(lambda processed_request: client.execute(processed_request))
        .flat_map_async(lambda response: process_response_plugins(plugins, response))
    )
```

---

## 🌐 **HTTP Ecosystem Integration Guidelines**

### **Cross-Project HTTP Import Standards**

```python
# ✅ Standard HTTP ecosystem imports
from flext_api import create_flext_api, FlextApiClient, FlextApiBuilder
from flext_core import FlextResult, FlextLogger
from flext_observability import FlextMetricsService

# ✅ Consistent HTTP error handling across projects
def sync_data_via_http(
    source_api: FlextApiClient,
    target_api: FlextApiClient,
    data_id: str
) -> FlextResult[dict]:
    return (
        source_api.get(f"/data/{data_id}")  # Returns FlextResult[ApiResponse]
        .map(lambda response: response.json())
        .flat_map(lambda data: target_api.post("/data", json=data))
        .map(lambda response: response.json())
    )

# ❌ Don't create custom HTTP result types per project
class OracleHttpResult[T]:  # Creates ecosystem fragmentation
    pass

class LdapHttpResult[T]:  # Creates ecosystem fragmentation
    pass
```

### **HTTP Configuration Integration**

```python
# ✅ Extend FlextApiSettings in all ecosystem projects
class OracleHttpSettings(FlextApiSettings):
    """Oracle-specific HTTP configuration extending flext-api patterns"""
    oracle_base_url: str = Field(env="ORACLE_API_BASE_URL")
    oracle_timeout: float = 120.0  # Oracle can be slow
    oracle_auth_token: str = Field(repr=False, env="ORACLE_API_TOKEN")

    class Config:
        env_prefix = "ORACLE_HTTP_"

class LdapHttpSettings(FlextApiSettings):
    """LDAP-specific HTTP configuration extending flext-api patterns"""
    ldap_base_url: str = Field(env="LDAP_API_BASE_URL")
    ldap_cert_path: str = Field(env="LDAP_CERT_PATH")
    ldap_verify_ssl: bool = True

    class Config:
        env_prefix = "LDAP_HTTP_"

class EcosystemHttpSettings(FlextConfig):
    """HTTP configuration composing all ecosystem services"""
    oracle: OracleHttpSettings = field(default_factory=OracleHttpSettings)
    ldap: LdapHttpSettings = field(default_factory=LdapHttpSettings)
    default: FlextApiSettings = field(default_factory=FlextApiSettings)

    def create_client_for_service(self, service: str) -> FlextResult[FlextApiClient]:
        """Create HTTP client for specific ecosystem service"""
        service_config = getattr(self, service, self.default)

        return FlextApiClient.create({
            "base_url": service_config.base_url,
            "timeout": service_config.timeout,
            "headers": {"Authorization": f"Bearer {service_config.auth_token}"}
        })
```

### **HTTP Domain Model Consistency**

```python
# ✅ Use HTTP domain entities consistently across ecosystem
class OracleDataRequest(FlextModels.Entity):
    """Oracle data request following HTTP domain patterns"""
    oracle_query: str
    parameters: dict
    timeout: float = 120.0

    def to_http_request(self, base_url: HttpUrl) -> FlextResult[ApiRequest]:
        """Convert to HTTP request using flext-api patterns"""
        if not self.oracle_query:
            return FlextResult[None].fail("Oracle query is required")

        url = base_url.join("/oracle/query")
        headers = HttpHeaders({"Content-Type": "application/json"})
        payload = {
            "query": self.oracle_query,
            "parameters": self.parameters
        }

        return FlextResult[None].ok(ApiRequest(
            method="POST",
            url=url,
            headers=headers,
            payload=payload,
            timeout=self.timeout
        ))

class LdapSearchRequest(FlextModels.Entity):
    """LDAP search request following HTTP domain patterns"""
    base_dn: str
    filter_expr: str
    attributes: List[str]

    def to_http_request(self, base_url: HttpUrl) -> FlextResult[ApiRequest]:
        """Convert to HTTP request using flext-api patterns"""
        url = base_url.join("/ldap/search")
        headers = HttpHeaders({"Content-Type": "application/json"})
        payload = {
            "base_dn": self.base_dn,
            "filter": self.filter_expr,
            "attributes": self.attributes
        }

        return FlextResult[None].ok(ApiRequest(
            method="POST",
            url=url,
            headers=headers,
            payload=payload
        ))
```

---

## 📋 **HTTP Module Creation Checklist**

### **HTTP Module Creation Checklist**

- [ ] **Naming**: Uses HTTP-focused, descriptive name following FlextApi conventions
- [ ] **Location**: Placed in appropriate HTTP architectural layer
- [ ] **Imports**: Only imports from same or lower layers, flext-core, and HTTP dependencies
- [ ] **Types**: Complete HTTP type annotations with MyPy compliance
- [ ] **Error Handling**: Uses FlextResult for all HTTP error conditions
- [ ] **Domain Modeling**: Uses HTTP domain entities and value objects where appropriate
- [ ] **Plugin Support**: Implements HTTP plugin patterns if extending client functionality
- [ ] **Configuration**: Extends FlextApiSettings for HTTP configuration needs
- [ ] **Documentation**: Comprehensive docstrings with HTTP usage examples
- [ ] **Tests**: 90% coverage with HTTP unit, integration, and e2e tests
- [ ] **Exports**: Added to `__init__.py` if part of public HTTP API
- [ ] **Examples**: Working HTTP examples in appropriate example files
- [ ] **Ecosystem Impact**: Validated across dependent ecosystem projects

### **HTTP Quality Gate Checklist**

- [ ] **Linting**: `make lint` passes (Ruff with all rules)
- [ ] **Type Check**: `make type-check` passes (strict MyPy for HTTP types)
- [ ] **Tests**: `make test` passes (90% coverage minimum for HTTP functionality)
- [ ] **Security**: `make security` passes (Bandit + pip-audit for HTTP security)
- [ ] **Format**: `make format` passes (79 character line limit)
- [ ] **HTTP Integration**: Works with flext-api HTTP patterns and ecosystem projects
- [ ] **Documentation**: Updated relevant HTTP documentation files
- [ ] **Examples**: Added or updated working HTTP examples
- [ ] **Plugin Compatibility**: HTTP plugins work correctly with new modules
- [ ] **FLEXT-Core Compliance**: Follows flext-core patterns (95% compliance required)

---

**Last Updated**: January 2, 2025  
**Target Audience**: FLEXT ecosystem developers implementing HTTP functionality  
**Scope**: HTTP module organization for FLEXT API foundation library  
**Version**: 0.9.0 → 0.9.0 development guidelines  
**Related**: flext-core/docs/Python-module-organization.md for foundation patterns
