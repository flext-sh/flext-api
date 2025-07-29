# HTTP Client

O cliente HTTP da FLEXT API é extensível, robusto e otimizado para uso em produção.

## Overview

O `FlextApiClient` oferece:

- **Sistema de plugins** para extensibilidade
- **Connection pooling** automático
- **Retry logic** configurável  
- **Circuit breaker** para tolerância a falhas
- **Caching inteligente** com TTL
- **Rate limiting** integrado
- **Métricas e monitoring** built-in

## Uso Básico

### Cliente Simples

```python
from flext_api import FlextApiClient, FlextApiClientConfig

# Configuração básica
config = FlextApiClientConfig(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"User-Agent": "MyApp/1.0"}
)

# Criar cliente
client = FlextApiClient(config)

# Fazer requisições
async def example():
    # GET
    result = await client.get("/users")
    
    # POST
    result = await client.post("/users", json={"name": "John"})
    
    # PUT, PATCH, DELETE também disponíveis
    result = await client.put("/users/1", json={"name": "Jane"})
    result = await client.patch("/users/1", json={"active": False})
    result = await client.delete("/users/1")
    
    # Sempre fechar conexões
    await client.close()
```

### Factory Function (Recomendado)

```python
from flext_api import create_client_with_plugins

# Forma mais simples
client = create_client_with_plugins(
    base_url="https://api.example.com",
    enable_cache=True,
    enable_retry=True,
    enable_circuit_breaker=True,
    timeout=30.0
)
```

## Plugins

### Plugins Built-in

#### 1. Caching Plugin

```python
from flext_api import FlextApiCachingPlugin

cache_plugin = FlextApiCachingPlugin(
    ttl=300,          # 5 minutos
    max_size=1000,    # Máximo 1000 entries
    include_headers=["Authorization"]  # Headers para considerar no cache
)
```

#### 2. Retry Plugin  

```python
from flext_api import FlextApiRetryPlugin

retry_plugin = FlextApiRetryPlugin(
    max_retries=3,
    backoff_factor=2.0,  # Backoff exponencial
    retry_on_status=[500, 502, 503, 504],
    retry_on_timeout=True
)
```

#### 3. Circuit Breaker Plugin

```python
from flext_api import FlextApiCircuitBreakerPlugin

circuit_plugin = FlextApiCircuitBreakerPlugin(
    failure_threshold=5,    # 5 falhas para abrir
    recovery_timeout=60,    # 60s para tentar recuperar
    expected_exception=(ConnectionError, TimeoutError)
)
```

### Plugin Customizado

```python
from flext_api import FlextApiPlugin

class AuthPlugin(FlextApiPlugin):
    def __init__(self, api_key: str):
        super().__init__("AuthPlugin")
        self.api_key = api_key
        self.token = None
    
    async def before_request(self, request):
        """Adicionar autenticação."""
        if self.token:
            request.headers["Authorization"] = f"Bearer {self.token}"
        else:
            request.headers["X-API-Key"] = self.api_key
        return request
    
    async def after_request(self, request, response):
        """Processar resposta."""
        if response.status_code == 401:
            # Token expirado, renovar
            await self._refresh_token()
        return response
    
    async def on_error(self, request, error):
        """Lidar com erros."""
        print(f"Request failed: {error}")
        return error
    
    async def _refresh_token(self):
        # Lógica para renovar token
        pass

# Usar plugin customizado
auth_plugin = AuthPlugin("my-api-key")
client = FlextApiClient(config, plugins=[auth_plugin])
```

## Configuração Avançada

### FlextApiClientConfig

```python
from flext_api import FlextApiClientConfig

config = FlextApiClientConfig(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json"
    },
    auth=("username", "password"),  # Basic auth
    verify_ssl=True,
    follow_redirects=True,
    max_redirects=5,
    proxy="http://proxy.company.com:8080"
)
```

### Request Configuration

```python
# Configurar requisição específica
result = await client.get(
    "/users",
    params={"page": 1, "limit": 10},
    headers={"X-Custom": "value"},
    timeout=60.0,  # Override timeout padrão
    follow_redirects=False
)
```

## Tratamento de Respostas

### FlextResult Pattern

```python
# Todas as operações retornam FlextResult
result = await client.get("/users")

if result.is_success:
    response = result.data
    
    # Acessar dados
    status_code = response.status_code
    headers = response.headers
    data = response.json()  # ou .text(), .content
    
    print(f"Status: {status_code}")
    print(f"Data: {data}")
else:
    print(f"Error: {result.error}")
    print(f"Error type: {result.error_type}")
```

### Tipos de Response

```python
# JSON response
result = await client.get("/api/users")
if result.is_success:
    users = result.data.json()

# Text response
result = await client.get("/health", headers={"Accept": "text/plain"})
if result.is_success:
    status = result.data.text()

# Binary response
result = await client.get("/files/image.png")
if result.is_success:
    image_bytes = result.data.content
```

## Health Checks e Métricas

### Health Check

```python
# Health check do cliente
health_result = await client.get_health()
if health_result.is_success:
    health = health_result.data
    print(f"Requests made: {health['request_count']}")
    print(f"Success rate: {health['success_rate']}")
    print(f"Average response time: {health['avg_response_time']}")
```

### Métricas dos Plugins

```python
# Métricas detalhadas
metrics_result = await client.get_metrics()
if metrics_result.is_success:
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
        if result.is_success:
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
    if not result.is_success:
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
    
    if health.is_success:
        success_rate = health.data['success_rate']
        if success_rate < 0.95:  # Menos de 95%
            print("⚠️ Client health degraded!")
```

## Exemplos Práticos

Veja exemplos completos em:

- [Basic Client Usage](../examples/basic_client_usage.py)
- [Advanced Features](../examples/02_advanced_features.py)
- [Enterprise Patterns](../examples/enterprise_api_complete.py)
