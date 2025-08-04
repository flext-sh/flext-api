# Getting Started - FLEXT API

**Complete quick start guide** for developing with flext-api following flext-core patterns.

> **⚠️ Important**: This project is migrating to flext-core compliance (35% → 95%). This guide shows the **correct** patterns that should be followed.

---

## 🎯 Prerequisites

### **Development Environment**

- **Python 3.13+** (mandatory)
- **Poetry** (recommended) or pip
- **Git** for version control
- **VSCode** or similar (recommended for Python development)

### **Technical Knowledge**

- **FastAPI** - Async web framework
- **Pydantic** - Data validation and serialization
- **flext-core patterns** - FlextResult, FlextService, FlextEntity
- **Type hints** - Python typing system
- **Async/await** - Asynchronous programming

---

## ⚡ Quick Setup

### **1. Clone and Installation**

```bash
# Clone complete FLEXT repository
git clone https://github.com/flext-sh/flext.git
cd flext/flext-api

# Complete setup with development dependencies
make setup

# Or manually
poetry install --with dev,test,docs
poetry run pre-commit install
```

### **2. Environment Verification**

```bash
# Verify installation
make diagnose

# Execute quality gates
make validate

# Expected output:
# ✅ Lint: OK
# ✅ Type check: OK
# ✅ Security: OK
# ✅ Tests: OK (90%+ coverage)
```

### **3. First Test Drive**

```bash
# Start development server
make dev

# ✅ Server running at http://localhost:8000
# ✅ Swagger UI: http://localhost:8000/docs
# ✅ ReDoc: http://localhost:8000/redoc
```

---

## 🔥 First Example - HTTP Client

### **CORRECT Pattern (flext-core compliant)**

```python
from flext_api import create_flext_api
from flext_core import FlextResult, get_logger

# ✅ Logger following flext-core pattern
logger = get_logger(__name__)

def http_client_example() -> FlextResult[dict]:
    """HTTP client example following flext-core patterns."""

    # ✅ Factory function for API
    api = create_flext_api()

    # ✅ FlextResult error handling
    client_result = api.flext_api_create_client({
        "base_url": "https://api.github.com",
        "timeout": 30,
        "max_retries": 3,
        "headers": {"User-Agent": "FLEXT-API/0.9.0"}
    })

    if client_result.is_failure:
        logger.error("Client creation failed", error=client_result.error)
        return FlextResult.fail(
            error=f"Failed to create HTTP client: {client_result.error}",
            error_code="CLIENT_CREATION_FAILED"
        )

    client = client_result.data
    logger.info("HTTP client created successfully")

    # ✅ Type-safe response
    return FlextResult.ok({
        "client_type": type(client).__name__,
        "base_url": "https://api.github.com",
        "status": "ready"
    })

# Execution
if __name__ == "__main__":
    result = http_client_example()

    if result.success:
        print(f"✅ Success: {result.data}")
    else:
        print(f"❌ Error: {result.error}")
```

---

## 🏗️ Second Example - Query Builder

### **Type-Safe Query Construction**

```python
from flext_api import create_flext_api, FlextApiQueryBuilder
from flext_core import FlextResult, get_logger
from typing import Dict, List, Any

logger = get_logger(__name__)

def query_builder_example() -> FlextResult[Dict[str, Any]]:
    """Query builder example with flext-core patterns."""

    api = create_flext_api()
    builder = api.get_builder()

    # ✅ Complex query construction
    query_params = {
        "filters": {
            "status": ["active", "pending"],
            "created_after": "2025-01-01T00:00:00Z",
            "tags": {"contains": ["api", "production"]},
            "priority": {"gte": 3}
        },
        "pagination": {
            "page": 1,
            "size": 50,
            "offset": 0
        },
        "sorting": [
            {"field": "created_at", "direction": "desc"},
            {"field": "priority", "direction": "asc"}
        ],
        "includes": ["metadata", "relationships"]
    }

    # ✅ Builder pattern with FlextResult
    query_result = builder.for_query().build(query_params)

    if query_result.is_failure:
        logger.error("Query building failed",
                    error=query_result.error,
                    params=query_params)
        return FlextResult.fail(
            error=f"Query construction failed: {query_result.error}",
            error_code="QUERY_BUILD_FAILED"
        )

    query = query_result.data
    logger.info("Query built successfully",
               query_size=len(str(query)),
               filters_count=len(query_params.get("filters", {})))

    return FlextResult.ok({
        "query": query,
        "estimated_results": 50,
        "cache_key": f"query_{hash(str(query))}",
        "build_timestamp": "2025-01-02T10:00:00Z"
    })

# Execution
if __name__ == "__main__":
    result = query_builder_example()

    if result.success:
        data = result.data
        print(f"✅ Query: {data['query']}")
        print(f"📊 Cache key: {data['cache_key']}")
    else:
        print(f"❌ Error: {result.error}")
```

---

## 🔌 Third Example - Plugin System

### **HTTP Client with Custom Plugins**

```python
from flext_api import (
    create_flext_api,
    FlextApiCachingPlugin,
    FlextApiRetryPlugin,
    FlextApiCircuitBreakerPlugin,
    create_client_with_plugins
)
from flext_core import FlextResult, get_logger
from typing import List

logger = get_logger(__name__)

def client_with_plugins_example() -> FlextResult[dict]:
    """HTTP client with plugins example following flext-core patterns."""

    # ✅ Plugin configuration
    plugins = [
        # Cache with 5-minute TTL
        FlextApiCachingPlugin(
            ttl=300,
            max_size=1000,
            cache_key_prefix="flext_api"
        ),

        # Retry with exponential backoff
        FlextApiRetryPlugin(
            max_retries=3,
            backoff_factor=2.0,
            retry_on_status=[500, 502, 503, 504]
        ),

        # Circuit breaker for protection
        FlextApiCircuitBreakerPlugin(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
    ]

    # ✅ Client configuration
    config = {
        "base_url": "https://api.example.com",
        "timeout": 30,
        "headers": {
            "Authorization": "Bearer token_here",
            "Content-Type": "application/json",
            "X-Client": "FLEXT-API"
        }
    }

    # ✅ Create client with plugins using FlextResult
    try:
        client = create_client_with_plugins(config, plugins)
        logger.info("Client with plugins created successfully",
                   plugins_count=len(plugins),
                   base_url=config["base_url"])

        return FlextResult.ok({
            "client_type": type(client).__name__,
            "plugins_enabled": [type(p).__name__ for p in plugins],
            "base_url": config["base_url"],
            "features": ["caching", "retry", "circuit_breaker"],
            "status": "ready"
        })

    except Exception as e:
        logger.exception("Client creation with plugins failed",
                        error=str(e),
                        config=config)
        return FlextResult.fail(
            error=f"Failed to create client with plugins: {e}",
            error_code="CLIENT_PLUGINS_FAILED"
        )

# Execution
if __name__ == "__main__":
    result = client_with_plugins_example()

    if result.success:
        data = result.data
        print(f"✅ Client ready: {data['client_type']}")
        print(f"🔌 Plugins: {', '.join(data['plugins_enabled'])}")
        print(f"🚀 Features: {', '.join(data['features'])}")
    else:
        print(f"❌ Error: {result.error}")
```

---

## 🎯 Quarto Exemplo - FastAPI Integration

### **API Endpoints com Padrões FLEXT-Core**

```python
from fastapi import FastAPI, HTTPException, Depends
from flext_api import flext_api_create_app, create_flext_api
from flext_core import FlextResult, get_logger
from pydantic import BaseModel
from typing import Dict, Any

# ✅ Logger seguindo padrão flext-core
logger = get_logger(__name__)

# ✅ Pydantic models para request/response
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str

class QueryRequest(BaseModel):
    filters: Dict[str, Any]
    pagination: Dict[str, int] = {"page": 1, "size": 10}

class QueryResponse(BaseModel):
    query: Dict[str, Any]
    results_count: int
    cache_key: str

# ✅ FastAPI app com flext-api patterns
app = flext_api_create_app()

def get_flext_api():
    """Dependency injection para FlextApi."""
    return create_flext_api()

@app.get("/health", response_model=HealthResponse)
async def health_check(api = Depends(get_flext_api)):
    """Health check endpoint seguindo padrões flext-core."""

    health_result = api.health_check()

    if health_result.is_failure:
        logger.error("Health check failed", error=health_result.error)
        raise HTTPException(
            status_code=500,
            detail=f"Service unhealthy: {health_result.error}"
        )

    health_data = health_result.data
    logger.info("Health check successful", status=health_data.get("status"))

    return HealthResponse(
        status=health_data.get("status", "unknown"),
        service=health_data.get("service", "flext-api"),
        version="0.9.0",
        timestamp="2025-01-02T10:00:00Z"
    )

@app.post("/queries/build", response_model=QueryResponse)
async def build_query(
    request: QueryRequest,
    api = Depends(get_flext_api)
):
    """Query building endpoint com padrões flext-core."""

    logger.info("Building query",
               filters_count=len(request.filters),
               page=request.pagination.get("page", 1))

    builder = api.get_builder()
    query_params = {
        "filters": request.filters,
        "pagination": request.pagination
    }

    query_result = builder.for_query().build(query_params)

    if query_result.is_failure:
        logger.error("Query building failed",
                    error=query_result.error,
                    request=request.dict())
        raise HTTPException(
            status_code=400,
            detail=f"Query building failed: {query_result.error}"
        )

    query = query_result.data
    cache_key = f"query_{hash(str(query))}"

    logger.info("Query built successfully",
               cache_key=cache_key,
               query_size=len(str(query)))

    return QueryResponse(
        query=query,
        results_count=request.pagination.get("size", 10),
        cache_key=cache_key
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("FLEXT-API FastAPI application started",
               version="0.9.0",
               patterns=["FlextResult", "FlextService", "structured_logging"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🧪 Testing com Padrões FLEXT-Core

### **Unit Tests Seguindo Padrões**

```python
# tests/test_getting_started_examples.py
import pytest
from flext_api import create_flext_api
from flext_core import FlextResult, get_logger

logger = get_logger(__name__)

class TestFlextApiGettingStarted:
    """Test cases para exemplos do getting started."""

    def test_create_api_follows_flext_core_patterns(self):
        """✅ Test: API creation seguindo padrões flext-core."""

        # ✅ Factory function usage
        api = create_flext_api()

        # ✅ Verify instance type
        assert api is not None
        assert hasattr(api, 'health_check')
        assert hasattr(api, 'get_builder')
        assert hasattr(api, 'flext_api_create_client')

        # ✅ Health check returns FlextResult
        health_result = api.health_check()
        assert isinstance(health_result, FlextResult)
        assert health_result.success

        health_data = health_result.data
        assert isinstance(health_data, dict)
        assert "service" in health_data
        assert health_data["service"] == "FlextApi"

    def test_client_creation_error_handling(self):
        """✅ Test: Client creation error handling com FlextResult."""

        api = create_flext_api()

        # ✅ Test invalid config - should return FlextResult.fail()
        invalid_config = {"base_url": "invalid_url"}  # Invalid URL

        client_result = api.flext_api_create_client(invalid_config)

        # ✅ Should fail gracefully with FlextResult
        assert isinstance(client_result, FlextResult)
        assert client_result.is_failure
        assert client_result.error is not None
        assert "Invalid URL format" in client_result.error

    def test_query_builder_patterns(self):
        """✅ Test: Query builder seguindo padrões corretos."""

        api = create_flext_api()
        builder = api.get_builder()

        # ✅ Complex query params
        query_params = {
            "filters": {"status": "active"},
            "pagination": {"page": 1, "size": 10}
        }

        # ✅ Builder should return FlextResult
        query_result = builder.for_query().build(query_params)

        assert isinstance(query_result, FlextResult)
        assert query_result.success

        query = query_result.data
        assert isinstance(query, dict)
        assert "filters" in query
        assert query["filters"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_service_lifecycle_patterns(self):
        """✅ Test: Service lifecycle seguindo padrões FlextService."""

        api = create_flext_api()

        # ✅ Start service (note: current implementation is async, should be sync)
        start_result = await api.start()
        assert isinstance(start_result, FlextResult)
        assert start_result.success

        # ✅ Health check
        health_result = api.health_check()
        assert health_result.success

        # ✅ Stop service
        stop_result = await api.stop()
        assert isinstance(stop_result, FlextResult)
        assert stop_result.success

# Execute tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 🚀 Próximos Passos

### **1. Explorar Documentação Avançada**

- **[Architecture Guide](architecture.md)** - Padrões arquiteturais completos
- **[API Reference](api-reference.md)** - Referência completa da API
- **[Client Guide](client.md)** - HTTP client avançado e plugins
- **[Builders Guide](builders.md)** - Query/Response builders detalhados

### **2. Entender o Plano de Migração**

- **[TODO.md](TODO.md)** - Desvios atuais e plano de correção
- **[CLAUDE.md](../CLAUDE.md)** - Guia para desenvolvimento com Claude Code

### **3. Contribuir para o Projeto**

- Seguir padrões flext-core rigorosamente
- Incluir tests abrangentes (90%+ coverage)
- Executar `make validate` antes de commits
- Participar da migração para 95% conformidade

### **4. Comandos Úteis para Desenvolvimento**

```bash
# Durante desenvolvimento
make dev              # Server localhost:8000
make test             # Execute todos os tests
make check            # Quick quality check

# Antes de commit
make validate         # Complete validation
make format           # Auto-format code
make type-check       # Type safety check

# Debug e diagnóstico
make diagnose         # Project health check
make coverage-html    # Coverage report
make api-docs         # Generate OpenAPI docs
```

---

## ⚡ Troubleshooting

### **Common Issues**

1. **Import Errors**

   ```bash
   # ✅ Solution: Check flext-core dependency
   poetry show flext-core
   poetry install --with dev
   ```

2. **Type Errors**

   ```bash
   # ✅ Solution: Check strict mode
   make type-check
   # Fix specific type errors
   ```

3. **Test Failures**

   ```bash
   # ✅ Solution: Run specific tests
   pytest tests/test_api_core.py -v
   # Check coverage
   make coverage-html
   ```

4. **Quality Gate Failures**

   ```bash
   # ✅ Solution: Auto-fix when possible
   make format
   make fix
   make validate
   ```

---

**📖 Next**: [Architecture Guide](architecture.md) - Understand complete architecture and flext-core patterns in detail.
