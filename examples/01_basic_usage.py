#!/usr/bin/env python3
"""FLEXT API - Basic usage examples.

This example demonstrates basic usage of the FLEXT API with real functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio

from flext_api import (
    FlextApiBuilder,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    create_flext_api_app,
)


def example_query_builder() -> None:
    """Demonstrate how to use ``FlextApiQueryBuilder``.

    Notes:
        Builds simple and complex queries, including pagination and sorting.

    """  # Criar query builder
    qb = FlextApiQueryBuilder()

    # Construir query simples
    (
        qb.equals("status", "active")
        .equals("name", "John")  # Changed from .like() which doesn't exist
        .sort_desc("created_at")
        .page(1)  # Set page number
        .page_size(10)  # Set page size
        .build()
    )

    # Construir query complexa
    qb2 = FlextApiQueryBuilder()  # Create new instance instead of reset()
    (
        qb2.equals("department", "engineering")
        .greater_than("salary", 50000)
        .greater_than("age", 25)  # Changed from .between() which doesn't exist
        .equals("email_verified", value=True)
        .sort_asc("last_name")
        .sort_desc("hire_date")
        .page(2)  # Página 2
        .page_size(25)  # 25 itens por página
        .build()
    )


def example_response_builder() -> None:
    """Demonstrate how to use ``FlextApiResponseBuilder``.

    Notes:
        Shows success, error, and paginated responses with metadata.

    """  # Response de sucesso
    rb = FlextApiResponseBuilder()
    (
        rb.success(data={"id": 123, "name": "John Doe"})
        .metadata({"version": "1.0", "source": "database"})
        .build()
    )

    # Response de erro
    rb = FlextApiResponseBuilder()
    rb.error("User not found").build()

    # Response paginada
    users = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"},
        {"id": 3, "name": "Bob"},
    ]

    rb = FlextApiResponseBuilder()
    (rb.success(data=users).pagination(page=1, page_size=3, total=100).build())


def example_fastapi_builder() -> None:
    """Demonstrate how to use ``FlextApiBuilder``.

    Notes:
        Creates a basic FastAPI app and uses the unified builder for
        query/response construction.

    """  # App básica com features automáticas
    create_flext_api_app()

    # Demonstrar uso do builder para queries e responses
    builder = FlextApiBuilder()

    # Use builder for query construction
    query_builder = builder.for_query()
    (
        query_builder.equals("category", "technology")
        .greater_than("price", 100)
        .sort_desc("rating")
        .page(1)
        .page_size(20)
        .build()
    )

    # Use builder for response construction
    response_builder = builder.for_response()
    (
        response_builder.success(data={"products": [], "total": 0})
        .metadata({"search_terms": ["technology", "high-price"]})
        .pagination(page=1, page_size=20, total=0)
        .build()
    )


async def example_http_client() -> None:
    """Demonstrate how to use ``FlextApiClient`` to make HTTP requests.

    Notes:
        Starts and stops the client, performs a health check, and prints
        effective configuration. Network requests are not performed in this
        example.

    """  # Configure client
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

        # Health check (sync method)
        client.health_check()

        # Note: In a real application, you would make HTTP requests here
        # but for this example, we'll just demonstrate the client setup

    except (ConnectionError, TimeoutError):
        pass

    finally:
        # Stop client
        await client.stop()


def example_integration() -> None:
    """Demonstrate complete integration of API components.

    Notes:
        Builds a query, simulates results, and creates a standardized
        API response, asserting expected fields.

    """  # 1. Construir query para buscar usuários
    qb = FlextApiQueryBuilder()
    (
        qb.equals("department", "sales")
        .greater_than("performance_score", 8.0)
        .sort_desc("last_review_date")
        .page(1)
        .page_size(20)
        .build()
    )

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
        .pagination(page=1, page_size=20, total=156)
        .metadata({"query_time_ms": 45, "cache_hit": False})
        .build()
    )

    len(api_response.data) if isinstance(api_response.data, list) else 0
    (
        api_response.pagination.get("total")
        if isinstance(api_response.pagination, dict)
        else None
    )

    # 4. Verificar que funciona como esperado
    expected_data_count = 3
    expected_total_pages = 8  # 156/20 = 7.8 -> 8

    if not api_response.success:
        msg: str = f"Expected True, got {api_response.success}"
        raise AssertionError(msg)
    if (
        len(api_response.data) if isinstance(api_response.data, list) else 0
    ) != expected_data_count:
        actual_len = (
            len(api_response.data) if isinstance(api_response.data, list) else 0
        )
        err_msg = f"Expected {expected_data_count}, got {actual_len}"
        raise AssertionError(err_msg)
    if (api_response.pagination or {}).get("total_pages") != expected_total_pages:
        actual_pages = (api_response.pagination or {}).get("total_pages")
        err_msg = f"Expected {expected_total_pages}, got {actual_pages}"
        raise AssertionError(err_msg)


async def main() -> None:
    """Run all examples."""  # Exemplos síncronos
    example_query_builder()
    example_response_builder()
    example_fastapi_builder()
    example_integration()

    # Exemplo assíncrono
    await example_http_client()


if __name__ == "__main__":
    asyncio.run(main())
