# Builder Patterns

Os builders da FLEXT API fornecem interfaces fluentes para construção de queries e responses padronizadas.

## Overview

A FLEXT API oferece três builders principais:

- **FlextApiQueryBuilder** - Construção de queries com filtros e ordenação
- **FlextApiResponseBuilder** - Respostas padronizadas com metadata
- **FlextApiBuilder** - Configuração de aplicações FastAPI

## Query Builder

### Uso Básico

```python
from flext_api import FlextApiQueryBuilder

qb = FlextApiQueryBuilder()
query = (qb
    .equals("status", "active")
    .greater_than("age", 18)
    .sort_desc("created_at")
    .page(1, 20)
    .build()
)

print(query)
# Output:
# {
#   "filters": [
#     {"field": "status", "operator": "equals", "value": "active"},
#     {"field": "age", "operator": "greater_than", "value": 18}
#   ],
#   "sorts": [
#     {"field": "created_at", "direction": "desc"}
#   ],
#   "page": 1,
#   "page_size": 20,
#   "limit": 20,
#   "offset": 0
# }
```

### Operadores de Filtro

#### Comparação

```python
qb = FlextApiQueryBuilder()

# Igualdade
qb.equals("status", "active")
qb.not_equals("status", "deleted")

# Comparação numérica
qb.greater_than("age", 18)
qb.greater_than_or_equal("salary", 50000)
qb.less_than("score", 100)
qb.less_than_or_equal("attempts", 3)

# Intervalos
qb.between("age", 18, 65)
qb.not_between("score", 0, 10)
```

#### Texto

```python
# Pattern matching
qb.like("name", "John%")          # Começa com "John"
qb.not_like("email", "%temp%")    # Não contém "temp"
qb.ilike("name", "john%")         # Case-insensitive like

# Busca em texto
qb.contains("description", "python")
qb.startswith("code", "PROD")
qb.endswith("email", "@company.com")
```

#### Listas e Nulos

```python
# Verificação de listas
qb.in_list("department", ["sales", "marketing", "engineering"])
qb.not_in_list("status", ["deleted", "suspended"])

# Verificação de nulos
qb.is_null("deleted_at")
qb.is_not_null("email")

# Verificação de vazios
qb.is_empty("notes")
qb.is_not_empty("tags")
```

#### Datas

```python
from datetime import datetime, date

# Comparação de datas
qb.date_equals("created_at", date(2025, 1, 1))
qb.date_before("due_date", datetime.now())
qb.date_after("start_date", "2025-01-01")

# Intervalos de data
qb.date_between("created_at", "2025-01-01", "2025-12-31")

# Funções de data
qb.date_year("created_at", 2025)
qb.date_month("created_at", 1)
qb.date_day("created_at", 15)
```

### Ordenação

```python
qb = FlextApiQueryBuilder()

# Ordenação simples
qb.sort_asc("name")           # Ascendente
qb.sort_desc("created_at")    # Descendente

# Múltiplas ordenações
query = (qb
    .sort_asc("department")    # Primeiro por departamento
    .sort_desc("salary")       # Depois por salário (desc)
    .sort_asc("name")          # Finalmente por nome
    .build()
)

# Ordenação customizada
qb.sort_by("priority", "desc", nulls_first=True)
```

### Paginação

```python
qb = FlextApiQueryBuilder()

# Paginação por página
qb.page(1, 20)        # Página 1, 20 itens por página
qb.page(2, 50)        # Página 2, 50 itens por página

# Paginação por limit/offset
qb.limit(100)         # Limitar a 100 resultados
qb.offset(50)         # Pular os primeiros 50

# Combinado
query = (qb
    .equals("active", True)
    .sort_desc("updated_at")
    .page(3, 25)       # Página 3, 25 por página (offset=50, limit=25)
    .build()
)
```

### Queries Complexas

```python
from flext_api import FlextApiQueryBuilder

def build_employee_search(department=None, min_salary=None, active_only=True):
    qb = FlextApiQueryBuilder()

    # Filtros condicionais
    if department:
        qb.equals("department", department)

    if min_salary:
        qb.greater_than_or_equal("salary", min_salary)

    if active_only:
        qb.equals("active", True)
        qb.is_null("terminated_at")

    # Busca avançada
    return (qb
        .is_not_null("email")
        .not_equals("status", "suspended")
        .date_after("hire_date", "2020-01-01")
        .sort_desc("performance_score")
        .sort_asc("last_name")
        .page(1, 50)
        .build()
    )

# Usar
query = build_employee_search(
    department="engineering",
    min_salary=80000,
    active_only=True
)
```

### Reset e Reutilização

```python
qb = FlextApiQueryBuilder()

# Primeira query
query1 = (qb
    .equals("type", "user")
    .sort_desc("created_at")
    .build()
)

# Reset para nova query
qb.reset()

# Segunda query (limpa)
query2 = (qb
    .equals("type", "REDACTED_LDAP_BIND_PASSWORD")
    .sort_asc("name")
    .build()
)
```

## Response Builder

### Uso Básico

```python
from flext_api import FlextApiResponseBuilder

rb = FlextApiResponseBuilder()

# Resposta de sucesso simples
success = rb.success({"id": 123, "name": "John"}).build()

# Resposta de erro
error = rb.error("User not found", 404).build()

print(success)
# Output:
# {
#   "success": True,
#   "data": {"id": 123, "name": "John"},
#   "error": None,
#   "metadata": {},
#   "timestamp": "2025-01-01T12:00:00Z"
# }
```

### Respostas de Sucesso

```python
rb = FlextApiResponseBuilder()

# Dados simples
response = rb.success("Operation completed").build()

# Dados complexos
users = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
]
response = rb.success(users).build()

# Com metadata
response = (rb
    .success(users)
    .with_metadata("count", len(users))
    .with_metadata("source", "database")
    .with_metadata("query_time_ms", 45)
    .build()
)
```

### Respostas de Erro

```python
rb = FlextApiResponseBuilder()

# Erro simples
response = rb.error("Invalid input").build()

# Erro com código
response = rb.error("User not found", 404).build()

# Erro com detalhes
response = (rb
    .error("Validation failed", 400)
    .with_error_details({
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_EMAIL"
    })
    .build()
)

# Múltiplos erros de validação
response = (rb
    .error("Multiple validation errors", 400)
    .with_error_details([
        {"field": "email", "message": "Required"},
        {"field": "age", "message": "Must be >= 18"}
    ])
    .build()
)
```

### Paginação

```python
rb = FlextApiResponseBuilder()

# Resposta paginada
users = get_users_page(page=1, size=20)  # Sua função
total_count = get_total_users()          # Sua função

response = (rb
    .success(users)
    .with_pagination(
        total=total_count,
        page=1,
        page_size=20
    )
    .build()
)

print(response['pagination'])
# Output:
# {
#   "total": 156,
#   "page": 1,
#   "page_size": 20,
#   "total_pages": 8,
#   "has_next": True,
#   "has_previous": False
# }
```

### Metadata Avançada

```python
rb = FlextApiResponseBuilder()

response = (rb
    .success(data)
    .with_metadata("request_id", "req_123456")
    .with_metadata("version", "v1.2.0")
    .with_metadata("cache_hit", False)
    .with_metadata("execution_time_ms", 125)
    .with_metadata("server", "api-01")
    .with_debug_info({
        "sql_query": "SELECT * FROM users WHERE active = ?",
        "query_params": [True],
        "index_used": "idx_users_active"
    })
    .build()
)
```

### Headers e Status

```python
rb = FlextApiResponseBuilder()

# Configurar resposta HTTP
response = (rb
    .success(data)
    .with_status_code(201)  # Created
    .with_headers({
        "Location": "/api/users/123",
        "X-Rate-Limit": "100"
    })
    .build()
)

# Acessar configurações HTTP
http_config = response.get('_http', {})
status_code = http_config.get('status_code', 200)
headers = http_config.get('headers', {})
```

## Factory Functions

### Helper Functions

```python
from flext_api import (
    build_query,
    build_success_response,
    build_error_response,
    build_paginated_response
)

# Query shortcut
query = build_query({"status": "active", "age__gte": 18})

# Response shortcuts
success = build_success_response(data=users)
error = build_error_response("Not found", 404)

# Paginated shortcut
paginated = build_paginated_response(
    data=users,
    page=1,
    size=20,
    total=156
)
```

## Integration Patterns

### Com FastAPI

```python
from fastapi import APIRouter
from flext_api import FlextApiQueryBuilder, FlextApiResponseBuilder

router = APIRouter()

@router.get("/users")
async def get_users(
    department: str = None,
    active: bool = True,
    page: int = 1,
    size: int = 20
):
    # Construir query
    qb = FlextApiQueryBuilder()
    if department:
        qb.equals("department", department)
    if active is not None:
        qb.equals("active", active)

    query = qb.sort_desc("created_at").page(page, size).build()

    # Buscar dados (sua lógica)
    users, total = await search_users(query)

    # Construir resposta
    rb = FlextApiResponseBuilder()
    return (rb
        .success(users)
        .with_pagination(total=total, page=page, page_size=size)
        .with_metadata("query_time_ms", 42)
        .build()
    )
```

### Com SQLAlchemy

```python
from sqlalchemy import and_, or_, desc, asc
from flext_api import FlextApiQueryBuilder

def apply_query_to_sqlalchemy(query_dict, base_query):
    """Converter query dict para SQLAlchemy query."""

    # Aplicar filtros
    for filter_item in query_dict.get("filters", []):
        field = filter_item["field"]
        operator = filter_item["operator"]
        value = filter_item["value"]

        if operator == "equals":
            base_query = base_query.filter(getattr(User, field) == value)
        elif operator == "greater_than":
            base_query = base_query.filter(getattr(User, field) > value)
        # ... outros operadores

    # Aplicar ordenação
    for sort_item in query_dict.get("sorts", []):
        field = sort_item["field"]
        direction = sort_item["direction"]

        if direction == "desc":
            base_query = base_query.order_by(desc(getattr(User, field)))
        else:
            base_query = base_query.order_by(asc(getattr(User, field)))

    # Aplicar paginação
    if "limit" in query_dict:
        base_query = base_query.limit(query_dict["limit"])
    if "offset" in query_dict:
        base_query = base_query.offset(query_dict["offset"])

    return base_query

# Usar
qb = FlextApiQueryBuilder()
query = qb.equals("active", True).sort_desc("created_at").page(1, 20).build()

sqlalchemy_query = apply_query_to_sqlalchemy(query, session.query(User))
users = sqlalchemy_query.all()
```

## Best Practices

### 1. Reutilizar Builders

```python
# ✅ Bom - Reutilizar com reset
qb = FlextApiQueryBuilder()

def build_active_users_query(department=None):
    qb.reset()  # Limpar estado anterior
    qb.equals("active", True)
    if department:
        qb.equals("department", department)
    return qb.build()

# ❌ Evitar - Criar novos builders desnecessariamente
def build_query_bad():
    return FlextApiQueryBuilder().equals("active", True).build()
```

### 2. Validar Inputs

```python
def build_search_query(filters: dict):
    qb = FlextApiQueryBuilder()

    # Validar filtros permitidos
    allowed_fields = ["name", "email", "department", "active"]

    for field, value in filters.items():
        if field not in allowed_fields:
            raise ValueError(f"Field '{field}' not allowed for filtering")

        qb.equals(field, value)

    return qb.build()
```

### 3. Usar Type Hints

```python
from typing import Optional, List, Dict
from flext_api import FlextApiQueryBuilder, FlextApiResponseBuilder

def build_user_query(
    active: Optional[bool] = None,
    departments: Optional[List[str]] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, object]:
    qb = FlextApiQueryBuilder()

    if active is not None:
        qb.equals("active", active)

    if departments:
        qb.in_list("department", departments)

    return qb.page(page, size).build()
```

## Exemplos Avançados

Veja exemplos completos em:

- [Basic Usage](../examples/01_basic_usage.py) - Query e Response builders
- [Advanced Patterns](../examples/02_advanced.py) - Patterns complexos
- [Real World Usage](../examples/real_world_usage.py) - Casos de uso reais
