# FLEXT API

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Uma biblioteca Python moderna para construção de APIs HTTP com padrões avançados de cliente, builders e plugins. Desenvolvida com FastAPI, fornece funcionalidades unificadas para criação de clientes HTTP robustos e construção de APIs usando composição de padrões do flext-core.

## 🚀 Características Principais

### HTTP Client com Plugins
- **Cliente HTTP extensível** com sistema de plugins
- **Caching inteligente** com TTL configurável
- **Retry automático** com backoff exponencial
- **Circuit breaker** para tolerância a falhas
- **Configuração flexível** via dependency injection

### Builder Patterns
- **Query Builder** para construção fluente de filtros e ordenação
- **Response Builder** para respostas padronizadas com metadata
- **API Builder** para criação de aplicações FastAPI configuráveis

### Arquitetura Moderna
- **Composition over inheritance** - design baseado em composição
- **FlextResult pattern** - tratamento consistente de erros
- **Dependency injection** - gerenciamento centralizado de dependências
- **Type safety** - tipagem estrita com MyPy
- **Async/await** - suporte completo para programação assíncrona

## 📦 Instalação

### Requisitos
- Python 3.13+
- Poetry (recomendado) ou pip

### Via Poetry (Recomendado)
```bash
# Clonar o repositório
git clone https://github.com/flext-sh/flext-api
cd flext-api

# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell
```

### Via pip
```bash
pip install flext-api
```

### Dependências Principais
- **flext-core**: Padrões base, logging, FlextResult, DI container
- **FastAPI 0.116+**: Framework web com suporte async
- **Pydantic 2.10+**: Validação e serialização de dados
- **aiohttp 3.12+**: Cliente HTTP assíncrono
- **httpx 0.28+**: Cliente HTTP moderno
- **structlog 25.4+**: Logging estruturado

## 🔧 Uso Rápido

### Cliente HTTP Básico
```python
from flext_api import FlextApi, create_client_with_plugins

# Criar API instance
api = FlextApi()

# Criar cliente HTTP com plugins
client = create_client_with_plugins(
    base_url="https://api.example.com",
    enable_cache=True,
    enable_retry=True, 
    enable_circuit_breaker=True,
    timeout=30.0
)

# Fazer requisições
async def example():
    # GET request
    result = await client.get("/users")
    if result.is_success:
        users = result.data.json()
    
    # POST request
    result = await client.post("/users", json={"name": "John"})
    
    # Fechar conexões
    await client.close()
```

### Query Builder
```python
from flext_api import FlextApiQueryBuilder

# Construir queries complexas
qb = FlextApiQueryBuilder()
query = (qb
    .equals("status", "active")
    .greater_than("age", 18)
    .like("name", "John%")
    .sort_desc("created_at")
    .page(1, 20)
    .build()
)

# Resultado: query estruturada para filtros, ordenação e paginação
```

### Response Builder
```python
from flext_api import FlextApiResponseBuilder

# Respostas padronizadas
rb = FlextApiResponseBuilder()

# Resposta de sucesso
success = (rb
    .success(data=users)
    .with_pagination(total=100, page=1, page_size=20)
    .with_metadata("query_time_ms", 45)
    .build()
)

# Resposta de erro
error = rb.error("User not found", 404).build()
```

### FastAPI Builder
```python
from flext_api import FlextApiBuilder, flext_api_create_app

# App básica
app = flext_api_create_app()

# App customizada
builder = FlextApiBuilder()
app = (builder
    .with_info("My API", "Custom API", "1.0.0")
    .with_cors(origins=["https://myapp.com"])
    .with_rate_limiting(per_minute=100)
    .with_logging()
    .with_security()
    .with_health_checks()
    .build()
)
```

## 📚 Exemplos Detalhados

### 1. Cliente com Plugins Personalizados
```python
from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiCachingPlugin,
    FlextApiRetryPlugin,
    FlextApiCircuitBreakerPlugin
)

# Configuração avançada
config = FlextApiClientConfig(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"User-Agent": "MyApp/1.0"}
)

# Plugins personalizados
plugins = [
    FlextApiCachingPlugin(ttl=300, max_size=1000),
    FlextApiRetryPlugin(max_retries=3, backoff_factor=2.0),
    FlextApiCircuitBreakerPlugin(failure_threshold=5, recovery_timeout=60)
]

# Criar cliente
client = FlextApiClient(config, plugins)
```

### 2. Plugin Customizado
```python
from flext_api import FlextApiPlugin

class AuthPlugin(FlextApiPlugin):
    def __init__(self, api_key: str):
        super().__init__("AuthPlugin")
        self.api_key = api_key
    
    async def before_request(self, request):
        request.headers["Authorization"] = f"Bearer {self.api_key}"
        return request
    
    async def after_request(self, request, response):
        if response.status_code == 401:
            # Renovar token se necessário
            pass
        return response
```

### 3. Integração Completa
```python
import asyncio
from flext_api import FlextApi, FlextApiQueryBuilder, FlextApiResponseBuilder

async def complete_example():
    # 1. Criar API instance
    api = FlextApi()
    
    # 2. Construir query
    qb = FlextApiQueryBuilder()
    query = qb.equals("department", "sales").sort_desc("performance").build()
    
    # 3. Criar cliente HTTP
    client_result = api.flext_api_create_client({
        "base_url": "https://api.company.com"
    })
    
    if client_result.success:
        client = client_result.data
        
        # 4. Fazer requisição
        result = await client.get("/employees", params=query)
        
        if result.is_success:
            # 5. Construir resposta padronizada
            rb = FlextApiResponseBuilder()
            response = (rb
                .success(result.data.json())
                .with_metadata("source", "api")
                .build()
            )
            return response

# Executar
asyncio.run(complete_example())
```

## 🛠️ Desenvolvimento

### Comandos Essenciais
```bash
# Setup completo do projeto
make setup

# Verificação rápida (lint + type)
make check

# Validação completa (lint + type + security + test)
make validate

# Executar testes
make test

# Executar apenas testes unitários
make test-unit

# Servidor de desenvolvimento
make dev  # http://localhost:8000

# Documentação interativa
make dev  # Então acesse http://localhost:8000/docs
```

### Comandos de Qualidade
```bash
# Linting
make lint

# Formatação
make format

# Type checking
make type-check

# Auditoria de segurança
make security

# Coverage HTML
make coverage-html
```

### Estrutura do Projeto
```
src/flext_api/
├── api.py               # Classe FlextApi principal
├── builder.py           # Query/Response builders  
├── client.py            # Cliente HTTP com plugins
├── constants.py         # Constantes e enums
├── fields.py            # Definições de campos
├── main.py              # Entry point FastAPI
├── application/         # Serviços de aplicação (legacy)
├── domain/              # Entidades de domínio (legacy)  
├── infrastructure/      # DI container e configuração
└── routes/              # Handlers de rota FastAPI

examples/                # Exemplos de uso
├── 01_basic_usage.py    # Uso básico de todos os componentes
├── 02_advanced_features.py  # Recursos avançados e plugins
└── ...                  # Mais exemplos

tests/                   # Testes abrangentes
├── unit/                # Testes unitários
├── integration/         # Testes de integração
└── e2e/                 # Testes end-to-end
```

## 🧪 Testes

### Executar Testes
```bash
# Todos os testes com coverage
pytest

# Apenas testes unitários
pytest -m unit

# Apenas testes de integração  
pytest -m integration

# Testes específicos
pytest tests/unit/test_client_enterprise.py -v

# Com coverage detalhado
pytest --cov=flext_api --cov-report=html
```

### Marcadores de Teste
- `unit` - Testes unitários isolados
- `integration` - Testes de integração
- `e2e` - Testes end-to-end
- `slow` - Testes que demoram mais
- `api` - Testes de endpoints
- `client` - Testes do cliente HTTP

## 📋 Padrões de Qualidade

### Zero Tolerance Quality Gates
- ✅ **90% minimum test coverage** 
- ✅ **Zero lint errors** (ruff with ALL rules)
- ✅ **Zero type errors** (strict MyPy)
- ✅ **Security scanning** (bandit + pip-audit)
- ✅ **Pre-commit hooks** automáticos

### Anti-Patterns (Nunca Fazer)
- ❌ Suprimir erros de lint/type sem corrigir a causa
- ❌ Usar inheritance quando composition é mais apropriada
- ❌ Pular o pattern FlextResult para tratamento de erros
- ❌ Hardcoding ao invés de dependency injection
- ❌ Instanciação direta ao invés de factory patterns

## 🔗 Integração com Ecosystem FLEXT

Este projeto faz parte do ecosystem FLEXT maior:

### Core Libraries
- **flext-core**: Padrões base, logging, DI container
- **flext-observability**: Monitoring e métricas
- **flext-auth**: Autenticação e autorização

### Services  
- **FlexCore (Go)**: Container runtime com plugins (port 8080)
- **FLEXT Service (Go/Python)**: Serviço de processamento (port 8081)

### Data Integration
- **flext-meltano**: Orquestração de pipelines Singer
- **flext-tap-***: Extractors de dados (5 projetos)
- **flext-target-***: Loaders de dados (5 projetos)

## 📖 Documentação

### Links Úteis
- **API Docs**: `make dev` → http://localhost:8000/docs
- **ReDoc**: `make dev` → http://localhost:8000/redoc  
- **Exemplos**: Veja pasta `examples/`
- **CLAUDE.md**: Guidance para development

### Gerar Documentação
```bash
# OpenAPI schema
make api-docs  # Gera openapi.json

# Docs locais
make docs-serve  # Se mkdocs estiver configurado
```

## 🤝 Contribuindo

1. **Fork** o repositório
2. **Clone** sua fork: `git clone https://github.com/seu-usuario/flext-api`
3. **Setup**: `make setup`
4. **Branch**: `git checkout -b feature/nova-funcionalidade`
5. **Desenvolva** seguindo os patterns estabelecidos
6. **Teste**: `make validate` (deve passar sem erros)
7. **Commit**: `git commit -m "feat: adicionar nova funcionalidade"`
8. **Push**: `git push origin feature/nova-funcionalidade`
9. **Pull Request** para a branch `main`

### Checklist para PR
- [ ] Testes passando (`make validate`)
- [ ] Coverage >= 90%
- [ ] Documentação atualizada se necessário
- [ ] Seguindo patterns do flext-core
- [ ] Usando composition over inheritance
- [ ] FlextResult para tratamento de erros

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Suporte

- **Issues**: https://github.com/flext-sh/flext-api/issues
- **Discussions**: https://github.com/flext-sh/flext/discussions
- **Email**: team@flext.sh

## 🗺️ Roadmap

### v0.9.0 (Próxima)
- [ ] Melhorar documentação API
- [ ] Adicionar mais plugins built-in
- [ ] Otimizar performance do cliente HTTP
- [ ] Integração com OpenAPI 3.1

### v1.0.0 (Estável)
- [ ] API estável e backwards compatible
- [ ] Documentação completa
- [ ] Benchmarks de performance
- [ ] Guias de migração

---

**FLEXT API** - Construindo APIs modernas com padrões enterprise 🚀
