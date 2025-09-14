# HTTP Client

The flext-api HTTP client is an async, typed wrapper around httpx that returns `FlextResult` values and uses Pydantic v2 models.

No plugin/circuit‑breaker/caching systems are implemented at this time.

## Overview

`FlextApiClient` provides:
- Async `get/post/put/delete`
- Minimal connection management (httpx.AsyncClient lifecycle)
- `health_check()`, `start()`, `stop()`, and simple configuration helpers

## Basic usage

```python
from flext_api import FlextApiClient, FlextApiModels

client = FlextApiClient(
    FlextApiModels.ClientConfig(
        base_url="https://httpbin.org",
        timeout=30,
        headers={"User-Agent": "flext-api/0.9.0"},
    )
)

async def example():
    await client.start()
    res = await client.get("/get", params={"q": "ping"})
    if res.is_success:
        print(res.value.status_code)
    await client.stop()
```

## Request options

All request methods accept optional `params`, `headers`, `json`, `data`, and `files` keyword arguments, forwarded to httpx.

```python
res = await client.post(
    "/post",
    json={"name": "Jane"},
    headers={"X-Trace": "123"}
)
```

## Health check

```python
health = client.health_check()
print(health["status"], health["base_url"])  # e.g. "stopped", "https://httpbin.org"
```

## Configuration

`FlextApiModels.ClientConfig` fields:
- `base_url: str`
- `timeout: float`
- `max_retries: int`
- `headers: dict[str, str]`
- `auth_token: str | None`
- `api_key: str | None`

Use `client.configure({...})` to update settings; `client.get_config()` returns a dict view.
# Métricas detalhadas
metrics_result = await client.get_metrics()
if metrics_result.success:
    metrics = metrics_result.data

    # Cache metrics
    cache_stats = metrics['plugins'].get('CachingPlugin', {})
    print(f"Cache hit rate: {cache_stats.get('hit_rate', 0)}")

    # Retry metrics
    retry_stats = metrics['plugins'].get('RetryPlugin', {})
    print(f"Retries performed: {retry_stats.get('retry_count', 0)}")

    # Circuit breaker status
    circuit_stats = metrics['plugins'].get('CircuitBreakerPlugin', {})
    print(f"Circuit state: {circuit_stats.get('state', 'closed')}")
```

## Context Managers

### Uso com Context Manager (Recomendado)

```python
from flext_api import create_client_with_plugins

async def example_with_context():
    async with create_client_with_plugins(
        base_url="https://api.example.com",
        enable_cache=True
    ) as client:
        # Fazer requisições
        result = await client.get("/users")
        if result.success:
            users = result.data.json()
            print(f"Found {len(users)} users")

    # Cliente fechado automaticamente
```

## Error Handling

### Tipos de Erro

```python
from flext_api.client import (
    FlextApiConnectionError,
    FlextApiTimeoutError,
    FlextApiHTTPError
)

try:
    result = await client.get("/users")
    if not result.success:
        if result.error_type == "timeout":
            print("Request timed out")
        elif result.error_type == "connection":
            print("Connection failed")
        elif result.error_type == "http":
            print(f"HTTP error: {result.error}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Automático

```python
# Retry configurado no plugin
retry_plugin = FlextApiRetryPlugin(
    max_retries=3,
    retry_on_status=[429, 500, 502, 503, 504],
    retry_on_timeout=True,
    backoff_factor=2.0
)

client = FlextApiClient(config, plugins=[retry_plugin])

# Requisição com retry automático
result = await client.get("/unreliable-endpoint")
```

## Best Practices

### 1. Sempre Fechar Conexões

```python
# ❌ Ruim
client = create_client_with_plugins(base_url="...")
result = await client.get("/data")
# Esqueceu de fechar

# ✅ Bom
async with create_client_with_plugins(base_url="...") as client:
    result = await client.get("/data")
```

### 2. Configurar Timeouts Apropriados

```python
# Para APIs rápidas
fast_client = create_client_with_plugins(
    base_url="https://fast-api.com",
    timeout=5.0
)

# Para processamento longo
slow_client = create_client_with_plugins(
    base_url="https://slow-api.com",
    timeout=300.0  # 5 minutos
)
```

### 3. Usar Plugins Adequados

```python
# Para APIs externas instáveis
external_client = create_client_with_plugins(
    base_url="https://external-api.com",
    enable_retry=True,
    enable_circuit_breaker=True,
    enable_cache=True  # Cache para reduzir chamadas
)

# Para APIs internas confiáveis
internal_client = create_client_with_plugins(
    base_url="https://internal-api.company.com",
    enable_cache=False,  # Sem cache para dados frescos
    enable_retry=False   # Falha rápida
)
```

### 4. Monitorar Performance

```python
# Verificar métricas periodicamente
async def monitor_client_health():
    health = await client.get_health()
    metrics = await client.get_metrics()

    if health.success:
        success_rate = health.data['success_rate']
        if success_rate < 0.95:  # Menos de 95%
            print("⚠️ Client health degraded!")
```

## Exemplos Práticos

Veja exemplos completos em:

- [Basic Client Usage](../examples/basic_client_usage.py)
- [Advanced Features](../examples/02_advanced_features.py)
- [Enterprise Patterns](../examples/enterprise_api_complete.py)
