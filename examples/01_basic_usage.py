#!/usr/bin/env python3
"""FLEXT API - Basic Usage Examples.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Este exemplo demonstra o uso básico da FLEXT API com funcionalidade real.

"""

import asyncio

from flext_api import (
    FlextApiBuilder,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    flext_api_create_app,
)


def example_query_builder() -> None:
    """Exemplo: Como usar o FlextApiQueryBuilder."""
    print("=== FlextApiQueryBuilder Example ===")

    # Criar query builder
    qb = FlextApiQueryBuilder()

    # Construir query simples
    simple_query = (
        qb.equals("status", "active")
        .equals("name", "John")  # Changed from .like() which doesn't exist
        .sort_desc("created_at")
        .page(1)  # Set page number
        .page_size(10)  # Set page size
        .build()
    )

    print("Simple Query:", simple_query)

    # Construir query complexa
    qb2 = FlextApiQueryBuilder()  # Create new instance instead of reset()
    complex_query = (
        qb2.equals("department", "engineering")
        .greater_than("salary", 50000)
        .greater_than("age", 25)  # Changed from .between() which doesn't exist
        .equals("email_verified", True)
        .sort_asc("last_name")
        .sort_desc("hire_date")
        .page(2)  # Página 2
        .page_size(25)  # 25 itens por página
        .build()
    )

    print("Complex Query:", complex_query)
    print()


def example_response_builder() -> None:
    """Exemplo: Como usar o FlextApiResponseBuilder."""
    print("=== FlextApiResponseBuilder Example ===")

    # Response de sucesso
    rb = FlextApiResponseBuilder()
    success_response = (
        rb.success(data={"id": 123, "name": "John Doe"})
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
        rb.success(data=users).with_pagination(total=100, page=1, page_size=3).build()
    )

    print("Paginated Response:", paginated_response)
    print()


def example_fastapi_builder() -> None:
    """Exemplo: Como usar o FlextApiBuilder."""
    print("=== FlextApiBuilder Example ===")

    # App básica com features automáticas
    basic_app = flext_api_create_app()
    print(f"Basic App: {basic_app.title} with {len(basic_app.routes)} routes")

    # Demonstrar uso do builder para queries e responses
    builder = FlextApiBuilder()

    # Use builder for query construction
    query_builder = builder.for_query()
    sample_query = (
        query_builder.equals("category", "technology")
        .greater_than("price", 100)
        .sort_desc("rating")
        .page(1)
        .page_size(20)
        .build()
    )
    print(f"Builder Query: {sample_query}")

    # Use builder for response construction
    response_builder = builder.for_response()
    sample_response = (
        response_builder.success(data={"products": [], "total": 0})
        .with_metadata("search_terms", ["technology", "high-price"])
        .with_pagination(total=0, page=1, page_size=20)
        .build()
    )
    print(f"Builder Response: {sample_response}")

    print()


async def example_http_client() -> None:
    """Exemplo: Como usar o FlextApiClient para fazer requisições HTTP."""
    print("=== FlextApiClient Example ===")

    # Configure client
    config = FlextApiClientConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30.0,
        headers={"User-Agent": "FlextAPI/1.0.0"},
        max_retries=3,
    )

    # Create client
    client = FlextApiClient(config)

    try:
        # Start client
        await client.start()

        print("Client configured with:")
        print(f"  Base URL: {client.config.base_url}")
        print(f"  Timeout: {client.config.timeout}s")
        print(f"  Max Retries: {client.config.max_retries}")
        print(f"  Headers: {client.config.headers}")

        # Health check (sync method)
        health_result = client.health_check()
        print("Client Health:", health_result)

        # Note: In a real application, you would make HTTP requests here
        # but for this example, we'll just demonstrate the client setup
        print("Client ready for HTTP requests")

    except (ConnectionError, TimeoutError) as e:
        print(f"Error: {e}")

    finally:
        # Stop client
        await client.stop()
        print("Client stopped successfully")

    print()


def example_integration() -> None:
    """Exemplo: Integração completa dos componentes."""
    print("=== Integration Example ===")

    # 1. Construir query para buscar usuários
    qb = FlextApiQueryBuilder()
    user_query = (
        qb.equals("department", "sales")
        .greater_than("performance_score", 8.0)
        .sort_desc("last_review_date")
        .page(1)
        .page_size(20)
        .build()
    )

    print("1. Built query for high-performing sales users:")
    print(f"   Filters: {len(user_query.filters)}")
    print(f"   Sorts: {len(user_query.sorts)}")
    print(f"   Pagination: page {user_query.page}, size {user_query.page_size}")

    # 2. Simular dados de resposta
    mock_users = [
        {"id": 1, "name": "Alice", "score": 9.2, "department": "sales"},
        {"id": 2, "name": "Bob", "score": 8.8, "department": "sales"},
        {"id": 3, "name": "Carol", "score": 8.5, "department": "sales"},
    ]

    # 3. Construir response padronizada
    rb = FlextApiResponseBuilder()
    api_response = (
        rb.success(data=mock_users)
        .with_pagination(total=156, page=1, page_size=20)
        .with_metadata("query_time_ms", 45)
        .with_metadata("cache_hit", value=False)
        .build()
    )

    print("2. Built standardized API response:")
    print(f"   Success: {api_response.success}")
    print(f"   Data count: {len(api_response.data)}")
    print(f"   Total records: {api_response.pagination['total']}")
    print(f"   Metadata: {list(api_response.metadata.keys())}")

    # 4. Verificar que funciona como esperado
    expected_data_count = 3
    expected_total_pages = 8  # 156/20 = 7.8 -> 8

    if not api_response.success:
        msg = f"Expected True, got {api_response['success']}"
        raise AssertionError(msg)
    if len(api_response.data) != expected_data_count:
        msg = f"Expected {expected_data_count}, got {len(api_response['data'])}"
        raise AssertionError(msg)
    if api_response.pagination["total_pages"] != expected_total_pages:
        actual_pages = api_response.pagination["total_pages"]
        msg = f"Expected {expected_total_pages}, got {actual_pages}"
        raise AssertionError(msg)

    print("3. ✅ All components work together correctly!")
    print()


async def main() -> None:
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
