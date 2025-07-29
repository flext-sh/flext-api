# Getting Started

Este guia irá ajudá-lo a começar com a FLEXT API rapidamente.

## Instalação

### Requisitos
- Python 3.13+
- Poetry (recomendado) ou pip

### Via Poetry
```bash
# Adicionar ao projeto existente
poetry add flext-api

# Ou clonar e instalar
git clone https://github.com/flext-sh/flext-api
cd flext-api
poetry install
```

### Via pip
```bash
pip install flext-api
```

## Primeiro Uso

### 1. Import Básico
```python
from flext_api import FlextApi, FlextResult
```

### 2. Criar Instância da API
```python
# Instância simples
api = FlextApi()

# Com factory function
from flext_api import create_flext_api
api = create_flext_api()
```

### 3. Cliente HTTP Básico
```python
from flext_api import create_client_with_plugins

# Cliente simples
client = create_client_with_plugins(
    base_url="https://jsonplaceholder.typicode.com"
)

# Fazer requisição
async def example():
    result = await client.get("/posts/1")
    if result.is_success:
        post = result.data.json()
        print(f"Post title: {post['title']}")
    
    await client.close()
```

### 4. Query Builder
```python
from flext_api import FlextApiQueryBuilder

qb = FlextApiQueryBuilder()
query = (qb
    .equals("status", "published")
    .greater_than("views", 100)
    .sort_desc("created_at")
    .page(1, 10)
    .build()
)

print(query)
# Output: structured query dict with filters, sorts, pagination
```

### 5. Response Builder
```python
from flext_api import FlextApiResponseBuilder

rb = FlextApiResponseBuilder()
response = (rb
    .success(data={"message": "Hello World"})
    .with_metadata("timestamp", "2025-01-01T12:00:00Z")
    .build()
)

print(response)
# Output: standardized response format
```

## Exemplo Completo

```python
import asyncio
from flext_api import FlextApi, FlextApiQueryBuilder, create_client_with_plugins

async def complete_example():
    # 1. Criar API
    api = FlextApi()
    
    # 2. Construir query
    qb = FlextApiQueryBuilder()
    query = qb.equals("userId", 1).build()
    
    # 3. Cliente HTTP
    client = create_client_with_plugins(
        base_url="https://jsonplaceholder.typicode.com",
        enable_cache=True,
        timeout=30.0
    )
    
    try:
        # 4. Fazer requisição
        result = await client.get("/posts", params=query)
        
        if result.is_success:
            posts = result.data.json()
            print(f"Found {len(posts)} posts")
            
            for post in posts:
                print(f"- {post['title']}")
        else:
            print(f"Error: {result.error}")
    
    finally:
        await client.close()

# Executar
if __name__ == "__main__":
    asyncio.run(complete_example())
```

## Próximos Passos

1. **HTTP Client**: Leia sobre [plugins e configurações avançadas](client.md)
2. **Builders**: Explore [Query e Response builders](builders.md) 
3. **FastAPI**: Veja como [criar APIs](fastapi.md) com FLEXT
4. **Examples**: Execute os [exemplos práticos](../examples/) 
5. **Testing**: Configure seu [ambiente de desenvolvimento](contributing.md)

## Troubleshooting

### Problemas Comuns

**ImportError: cannot import name 'FlextApi'**
```bash
# Verificar instalação
pip list | grep flext-api
# Reinstalar se necessário
pip uninstall flext-api && pip install flext-api
```

**ModuleNotFoundError: No module named 'flext_core'**
```bash
# Instalar dependência principal
pip install flext-core
```

**TypeError em async/await**
- Certifique-se de usar `await` com métodos async do cliente
- Use `asyncio.run()` para executar código assíncrono

### Verificar Instalação
```python
# Test script para verificar se tudo está funcionando
import asyncio
from flext_api import FlextApi

async def test_install():
    api = FlextApi()
    print("✅ FLEXT API instalada corretamente!")
    
    # Test client creation
    result = api.flext_api_create_client({"base_url": "https://httpbin.org"})
    if result.success:
        print("✅ Cliente HTTP funcionando!")
        client = result.data
        await client.close()
    else:
        print(f"❌ Erro ao criar cliente: {result.error}")

asyncio.run(test_install())
```

## Ajuda

Se você ainda tiver problemas:
- Consulte os [exemplos](../examples/)
- Abra uma [issue no GitHub](https://github.com/flext-sh/flext-api/issues)
- Veja as [discussões da comunidade](https://github.com/flext-sh/flext/discussions)