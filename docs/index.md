# FLEXT API Documentation

Bem-vindo à documentação da FLEXT API - uma biblioteca Python moderna para construção de APIs HTTP com padrões avançados.

## 🚀 Overview

FLEXT API é uma biblioteca que combina:

- **Cliente HTTP extensível** com sistema de plugins
- **Builder patterns** para construção fluente de queries e responses
- **FastAPI integration** para criação de APIs robustas
- **Composition-based architecture** usando padrões do flext-core

## 📚 Quick Start

### Instalação

```bash
poetry add flext-api
# ou
pip install flext-api
```

### Uso Básico

```python
from flext_api import FlextApi, create_client_with_plugins

# Criar instância da API
api = FlextApi()

# Cliente HTTP com plugins
client = create_client_with_plugins(
    base_url="https://api.example.com",
    enable_cache=True,
    enable_retry=True
)
```

## 📖 Guias

### [Getting Started](getting-started.md)

Como começar a usar a FLEXT API do zero.

### [HTTP Client](client.md)

Usando o cliente HTTP com plugins para requisições robustas.

### [Builder Patterns](builders.md)

Query Builder e Response Builder para construção fluente.

### [FastAPI Integration](fastapi.md)

Criando aplicações FastAPI com os builders da FLEXT.

### [Plugins](plugins.md)

Sistema de plugins extensível para o cliente HTTP.

### [Advanced Usage](advanced.md)

Padrões avançados e customizações.

## 🔗 API Reference

### [API Reference](api-reference.md)

Documentação completa de todas as classes e métodos.

## 🛠️ Development

### [Contributing](contributing.md)

Como contribuir para o projeto.

### [Architecture](architecture.md)

Decisões arquiteturais e padrões.

## 🧪 Examples

Veja os exemplos práticos na pasta `examples/`:

- [Basic Usage](../examples/01_basic_usage.py)
- [Advanced Features](../examples/02_advanced_features.py)

## 🆘 Support

- **GitHub Issues**: <https://github.com/flext-sh/flext-api/issues>
- **Discussions**: <https://github.com/flext-sh/flext/discussions>
- **Email**: <team@flext.sh>
