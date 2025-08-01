# API Reference

Referência completa da API da FLEXT API.

## Core Classes

### FlextApi

**Classe principal que unifica todas as funcionalidades.**

```python
class FlextApi:
    def __init__(self) -> None

    def flext_api_create_client(
        self,
        config: dict | None = None
    ) -> FlextResult[FlextApiClient]
```

**Métodos:**

- `flext_api_create_client()` - Cria cliente HTTP configurado

### FlextResult

**Pattern para tratamento consistente de erros (da flext-core).**

```python
class FlextResult[T]:
    success: bool
    data: T | None
    error: str | None
    error_type: str | None

    @classmethod
    def ok(cls, data: T) -> FlextResult[T]

    @classmethod
    def fail(cls, error: str, error_type: str = None) -> FlextResult[T]

    @property
    def is_success(self) -> bool

    @property
    def is_failure(self) -> bool
```

## HTTP Client

### FlextApiClient

**Cliente HTTP extensível com sistema de plugins.**

```python
class FlextApiClient:
    def __init__(
        self,
        config: FlextApiClientConfig,
        plugins: list[FlextApiPlugin] = None
    )

    async def get(
        self,
        path: str,
        params: dict = None,
        headers: dict = None,
        timeout: float = None,
        **kwargs
    ) -> FlextResult[FlextApiClientResponse]

    async def post(
        self,
        path: str,
        json: dict = None,
        data: Any = None,
        headers: dict = None,
        timeout: float = None,
        **kwargs
    ) -> FlextResult[FlextApiClientResponse]

    async def put(...) -> FlextResult[FlextApiClientResponse]
    async def patch(...) -> FlextResult[FlextApiClientResponse]
    async def delete(...) -> FlextResult[FlextApiClientResponse]

    async def get_health(self) -> FlextResult[dict]
    async def get_metrics(self) -> FlextResult[dict]
    async def close(self) -> None
```

### FlextApiClientConfig

**Configuração do cliente HTTP.**

```python
class FlextApiClientConfig:
    base_url: str
    timeout: float = 30.0
    headers: dict[str, str] = None
    auth: tuple[str, str] = None
    verify_ssl: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5
    proxy: str = None
```

### FlextApiClientResponse

**Wrapper para respostas HTTP.**

```python
class FlextApiClientResponse:
    status_code: int
    headers: dict[str, str]
    content: bytes

    def json(self) -> dict
    def text(self) -> str
```

### FlextApiClientRequest

**Representação de requisição HTTP.**

```python
class FlextApiClientRequest:
    method: FlextApiClientMethod
    url: str
    headers: dict[str, str]
    params: dict[str, object]
    json: dict = None
    data: Any = None
    timeout: float = None
```

### FlextApiClientMethod

**Enum para métodos HTTP.**

```python
class FlextApiClientMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
```

## Plugins

### FlextApiPlugin

**Classe base para plugins do cliente HTTP.**

```python
class FlextApiPlugin:
    def __init__(self, name: str)

    async def before_request(
        self,
        request: FlextApiClientRequest
    ) -> FlextApiClientRequest

    async def after_request(
        self,
        request: FlextApiClientRequest,
        response: FlextApiClientResponse
    ) -> FlextApiClientResponse

    async def on_error(
        self,
        request: FlextApiClientRequest,
        error: Exception
    ) -> Exception

    def get_metrics(self) -> dict
```

### FlextApiCachingPlugin

**Plugin de cache com TTL.**

```python
class FlextApiCachingPlugin(FlextApiPlugin):
    def __init__(
        self,
        ttl: int = 300,
        max_size: int = 1000,
        include_headers: list[str] = None
    )
```

### FlextApiRetryPlugin

**Plugin de retry com backoff exponencial.**

```python
class FlextApiRetryPlugin(FlextApiPlugin):
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        retry_on_status: list[int] = None,
        retry_on_timeout: bool = True
    )
```

### FlextApiCircuitBreakerPlugin

**Plugin circuit breaker para tolerância a falhas.**

```python
class FlextApiCircuitBreakerPlugin(FlextApiPlugin):
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: tuple = None
    )
```

## Query Builder

### FlextApiQueryBuilder

**Builder fluente para construção de queries.**

```python
class FlextApiQueryBuilder:
    def __init__(self)

    # Filtros de comparação
    def equals(self, field: str, value: Any) -> FlextApiQueryBuilder
    def not_equals(self, field: str, value: Any) -> FlextApiQueryBuilder
    def greater_than(self, field: str, value: Any) -> FlextApiQueryBuilder
    def greater_than_or_equal(self, field: str, value: Any) -> FlextApiQueryBuilder
    def less_than(self, field: str, value: Any) -> FlextApiQueryBuilder
    def less_than_or_equal(self, field: str, value: Any) -> FlextApiQueryBuilder
    def between(self, field: str, min_val: Any, max_val: Any) -> FlextApiQueryBuilder
    def not_between(self, field: str, min_val: Any, max_val: Any) -> FlextApiQueryBuilder

    # Filtros de texto
    def like(self, field: str, pattern: str) -> FlextApiQueryBuilder
    def not_like(self, field: str, pattern: str) -> FlextApiQueryBuilder
    def ilike(self, field: str, pattern: str) -> FlextApiQueryBuilder
    def contains(self, field: str, value: str) -> FlextApiQueryBuilder
    def startswith(self, field: str, value: str) -> FlextApiQueryBuilder
    def endswith(self, field: str, value: str) -> FlextApiQueryBuilder

    # Filtros de lista e nulos
    def in_list(self, field: str, values: list) -> FlextApiQueryBuilder
    def not_in_list(self, field: str, values: list) -> FlextApiQueryBuilder
    def is_null(self, field: str) -> FlextApiQueryBuilder
    def is_not_null(self, field: str) -> FlextApiQueryBuilder
    def is_empty(self, field: str) -> FlextApiQueryBuilder
    def is_not_empty(self, field: str) -> FlextApiQueryBuilder

    # Filtros de data
    def date_equals(self, field: str, date_val: Any) -> FlextApiQueryBuilder
    def date_before(self, field: str, date_val: Any) -> FlextApiQueryBuilder
    def date_after(self, field: str, date_val: Any) -> FlextApiQueryBuilder
    def date_between(self, field: str, start: Any, end: Any) -> FlextApiQueryBuilder
    def date_year(self, field: str, year: int) -> FlextApiQueryBuilder
    def date_month(self, field: str, month: int) -> FlextApiQueryBuilder
    def date_day(self, field: str, day: int) -> FlextApiQueryBuilder

    # Ordenação
    def sort_asc(self, field: str) -> FlextApiQueryBuilder
    def sort_desc(self, field: str) -> FlextApiQueryBuilder
    def sort_by(
        self,
        field: str,
        direction: str,
        nulls_first: bool = False
    ) -> FlextApiQueryBuilder

    # Paginação
    def page(self, page: int, size: int) -> FlextApiQueryBuilder
    def limit(self, limit: int) -> FlextApiQueryBuilder
    def offset(self, offset: int) -> FlextApiQueryBuilder

    # Utilitários
    def reset(self) -> FlextApiQueryBuilder
    def build(self) -> dict[str, object]
```

### FlextApiQueryOperator

**Enum para operadores de query.**

```python
class FlextApiQueryOperator(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    LIKE = "like"
    NOT_LIKE = "not_like"
    ILIKE = "ilike"
    CONTAINS = "contains"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
```

## Response Builder

### FlextApiResponseBuilder

**Builder para respostas padronizadas.**

```python
class FlextApiResponseBuilder:
    def __init__(self)

    def success(self, data: Any = None) -> FlextApiResponseBuilder
    def error(self, message: str, code: int = None) -> FlextApiResponseBuilder

    def with_metadata(self, key: str, value: Any) -> FlextApiResponseBuilder
    def with_pagination(
        self,
        total: int,
        page: int,
        page_size: int
    ) -> FlextApiResponseBuilder

    def with_error_details(self, details: Any) -> FlextApiResponseBuilder
    def with_status_code(self, code: int) -> FlextApiResponseBuilder
    def with_headers(self, headers: dict) -> FlextApiResponseBuilder
    def with_debug_info(self, info: dict) -> FlextApiResponseBuilder

    def reset(self) -> FlextApiResponseBuilder
    def build(self) -> dict[str, object]
```

## FastAPI Builder

### FlextApiBuilder

**Builder para aplicações FastAPI.**

```python
class FlextApiBuilder:
    def __init__(self)

    def with_info(
        self,
        title: str,
        description: str = None,
        version: str = None
    ) -> FlextApiBuilder

    def with_cors(
        self,
        origins: list[str] = None,
        allow_methods: list[str] = None,
        allow_headers: list[str] = None
    ) -> FlextApiBuilder

    def with_rate_limiting(
        self,
        per_minute: int = 60
    ) -> FlextApiBuilder

    def with_logging(self) -> FlextApiBuilder
    def with_security(self) -> FlextApiBuilder
    def with_health_checks(self) -> FlextApiBuilder
    def with_metrics_endpoint(self) -> FlextApiBuilder

    def build(self) -> FastAPI
```

## Factory Functions

### create_flext_api

```python
def create_flext_api() -> FlextApi
```

### create_client

```python
def create_client(config: dict) -> FlextApiClient
```

### create_client_with_plugins

```python
def create_client_with_plugins(
    base_url: str = None,
    enable_cache: bool = False,
    enable_retry: bool = False,
    enable_circuit_breaker: bool = False,
    timeout: float = 30.0,
    **kwargs
) -> FlextApiClient
```

### build_query

```python
def build_query(filters: dict) -> dict
```

### build_success_response

```python
def build_success_response(
    data: Any = None,
    metadata: dict = None
) -> dict
```

### build_error_response

```python
def build_error_response(
    message: str,
    code: int = None,
    details: Any = None
) -> dict
```

### build_paginated_response

```python
def build_paginated_response(
    data: Any,
    page: int,
    size: int,
    total: int,
    metadata: dict = None
) -> dict
```

### flext_api_create_app

```python
def flext_api_create_app() -> FastAPI
```

## Constants e Enums

### FlextApiClientStatus

```python
class FlextApiClientStatus(Enum):
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    CLOSED = "closed"
```

### FlextApiClientProtocol

```python
class FlextApiClientProtocol(Enum):
    HTTP = "http"
    HTTPS = "https"
```

## Exception Types

### FlextApiConnectionError

```python
class FlextApiConnectionError(Exception):
    pass
```

### FlextApiTimeoutError

```python
class FlextApiTimeoutError(Exception):
    pass
```

### FlextApiHTTPError

```python
class FlextApiHTTPError(Exception):
    def __init__(self, status_code: int, message: str)

    status_code: int
    message: str
```

## Type Definitions

### Common Types

```python
from typing import Any, Dict, List, Optional, Union

QueryDict = Dict[str, object]
ResponseDict = Dict[str, object]
MetadataDict = Dict[str, object]
HeadersDict = Dict[str, str]
ParamsDict = Dict[str, object]
```

## Usage Examples

### Basic Usage

```python
from flext_api import FlextApi, FlextApiQueryBuilder, FlextApiResponseBuilder

# API instance
api = FlextApi()

# Query building
qb = FlextApiQueryBuilder()
query = qb.equals("active", True).sort_desc("created_at").build()

# Response building
rb = FlextApiResponseBuilder()
response = rb.success(data).with_metadata("count", 10).build()

# HTTP client
client_result = api.flext_api_create_client({"base_url": "https://api.example.com"})
if client_result.success:
    client = client_result.data
    result = await client.get("/users")
    await client.close()
```

### Advanced Usage

```python
from flext_api import (
    create_client_with_plugins,
    FlextApiCachingPlugin,
    FlextApiRetryPlugin
)

# Advanced client with plugins
client = create_client_with_plugins(
    base_url="https://api.example.com",
    enable_cache=True,
    enable_retry=True,
    timeout=30.0
)

# Custom plugins
plugins = [
    FlextApiCachingPlugin(ttl=300),
    FlextApiRetryPlugin(max_retries=3)
]

client = FlextApiClient(config, plugins)
```

## Version Information

```python
from flext_api import __version__, __version_info__

print(f"FLEXT API version: {__version__}")
print(f"Version info: {__version_info__}")
```

Para exemplos mais detalhados, consulte a pasta `examples/` e a documentação de [Getting Started](getting-started.md).
