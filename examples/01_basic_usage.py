#!/usr/bin/env python3
"""FLEXT API - Basic Usage Examples.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Este exemplo demonstra o uso básico da FLEXT API com funcionalidade real.
"""

import asyncio
from flext_api import (
    FlextApiClient,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    FlextApiBuilder,
    flext_api_create_app,
)


def example_query_builder():
    """Exemplo: Como usar o FlextApiQueryBuilder."""
    print("=== FlextApiQueryBuilder Example ===")
    
    # Criar query builder
    qb = FlextApiQueryBuilder()
    
    # Construir query simples
    simple_query = (
        qb.equals("status", "active")
        .like("name", "John%")
        .sort_desc("created_at")
        .limit(10)
        .build()
    )
    
    print("Simple Query:", simple_query)
    
    # Construir query complexa
    qb.reset()  # Limpar query anterior
    complex_query = (
        qb.equals("department", "engineering")
        .greater_than("salary", 50000)
        .between("age", 25, 45)
        .is_not_null("email")
        .sort_asc("last_name")
        .sort_desc("hire_date")
        .page(2, 25)  # Página 2, 25 itens por página
        .build()
    )
    
    print("Complex Query:", complex_query)
    print()


def example_response_builder():
    """Exemplo: Como usar o FlextApiResponseBuilder."""
    print("=== FlextApiResponseBuilder Example ===")
    
    # Response de sucesso
    rb = FlextApiResponseBuilder()
    success_response = (
        rb.success({"id": 123, "name": "John Doe"})
        .with_metadata("version", "1.0")
        .with_metadata("source", "database")
        .build()
    )
    
    print("Success Response:", success_response)
    
    # Response de erro
    rb = FlextApiResponseBuilder()
    error_response = rb.error("User not found", 404).build()
    
    print("Error Response:", error_response)
    
    # Response paginada
    users = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"},
        {"id": 3, "name": "Bob"},
    ]
    
    rb = FlextApiResponseBuilder()
    paginated_response = (
        rb.success(users)
        .with_pagination(total=100, page=1, page_size=3)
        .build()
    )
    
    print("Paginated Response:", paginated_response)
    print()


def example_fastapi_builder():
    """Exemplo: Como usar o FlextApiBuilder."""
    print("=== FlextApiBuilder Example ===")
    
    # App básica com features automáticas
    basic_app = flext_api_create_app()
    print(f"Basic App: {basic_app.title} with {len(basic_app.routes)} routes")
    
    # App customizada com builder
    builder = FlextApiBuilder()
    custom_app = (
        builder
        .with_info("My Custom API", "API customizada para demonstração", "2.1.0")
        .with_cors(origins=["https://myapp.com", "https://admin.myapp.com"])
        .with_rate_limiting(per_minute=200)
        .with_logging()
        .with_security()
        .with_health_checks()
        .with_metrics_endpoint()
        .build()
    )
    
    print(f"Custom App: {custom_app.title} v{custom_app.version}")
    print(f"Routes: {len(custom_app.routes)}")
    
    # Mostrar algumas rotas
    for route in custom_app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {route.methods} {route.path}")
    
    print()


async def example_http_client():
    """Exemplo: Como usar o FlextApiClient para fazer requisições HTTP."""
    print("=== FlextApiClient Example ===")
    
    from flext_api import create_client_with_plugins
    
    # Criar client com plugins
    client = create_client_with_plugins(
        "https://httpbin.org",
        enable_cache=True,
        enable_retry=True,
        enable_circuit_breaker=True,
        timeout=10.0
    )
    
    try:
        print("Making HTTP requests...")
        
        # GET request
        result = await client.get("/json")
        if result.is_success:
            response = result.data
            print(f"GET /json: {response.status_code} - {len(str(response.data))} chars")
        
        # POST request
        post_data = {"name": "John", "email": "john@example.com"}
        result = await client.post("/post", json=post_data)
        if result.is_success:
            response = result.data
            print(f"POST /post: {response.status_code}")
        
        # Health check do client
        health_result = await client.get_health()
        if health_result.is_success:
            health = health_result.data
            print(f"Client Health: {health['request_count']} requests made")
        
        # Métricas dos plugins
        metrics_result = await client.get_metrics()
        if metrics_result.is_success:
            metrics = metrics_result.data
            cache_metrics = metrics['plugins'].get('CachingPlugin', {})
            print(f"Cache Stats: {cache_metrics}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await client.close()
    
    print()


def example_integration():
    """Exemplo: Integração completa dos componentes."""
    print("=== Integration Example ===")
    
    # 1. Construir query para buscar usuários
    qb = FlextApiQueryBuilder()
    user_query = (
        qb.equals("department", "sales")
        .greater_than("performance_score", 8.0)
        .sort_desc("last_review_date")
        .page(1, 20)
        .build()
    )
    
    print("1. Built query for high-performing sales users:")
    print(f"   Filters: {len(user_query['filters'])}")
    print(f"   Sorts: {len(user_query['sorts'])}")
    print(f"   Pagination: page {user_query['page']}, size {user_query['page_size']}")
    
    # 2. Simular dados de resposta
    mock_users = [
        {"id": 1, "name": "Alice", "score": 9.2, "department": "sales"},
        {"id": 2, "name": "Bob", "score": 8.8, "department": "sales"},
        {"id": 3, "name": "Carol", "score": 8.5, "department": "sales"},
    ]
    
    # 3. Construir response padronizada
    rb = FlextApiResponseBuilder()
    api_response = (
        rb.success(mock_users)
        .with_pagination(total=156, page=1, page_size=20)
        .with_metadata("query_time_ms", 45)
        .with_metadata("cache_hit", False)
        .build()
    )
    
    print("2. Built standardized API response:")
    print(f"   Success: {api_response['success']}")
    print(f"   Data count: {len(api_response['data'])}")
    print(f"   Total records: {api_response['pagination']['total']}")
    print(f"   Metadata: {list(api_response['metadata'].keys())}")
    
    # 4. Verificar que funciona como esperado
    assert api_response['success'] is True
    assert len(api_response['data']) == 3
    assert api_response['pagination']['total_pages'] == 8  # 156/20 = 7.8 -> 8
    
    print("3. ✅ All components work together correctly!")
    print()


async def main():
    """Executar todos os exemplos."""
    print("FLEXT API - Basic Usage Examples")
    print("=" * 50)
    print()
    
    # Exemplos síncronos
    example_query_builder()
    example_response_builder()
    example_fastapi_builder()
    example_integration()
    
    # Exemplo assíncrono
    await example_http_client()
    
    print("=" * 50)
    print("✅ All examples completed successfully!")
    print()
    print("Next steps:")
    print("- Check examples/02_advanced_features.py for advanced usage")
    print("- Run tests with: pytest tests/")
    print("- Start development server with: uvicorn flext_api.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())