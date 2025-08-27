#!/usr/bin/env python3
"""FLEXT API - Advanced Features Examples (CORRECTED).

Este exemplo demonstra recursos avançados da FLEXT API com funcionalidade REAL.
Todos os métodos usados existem e funcionam conforme implementados.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    build_error_response,
    build_paginated_response,
    build_query,
    build_success_response,
    create_flext_api,
)


def example_advanced_query_building() -> None:
    """Example: Advanced query construction using real existing methods."""
    # Query complexa usando apenas métodos que existem
    qb = FlextApiClient.QueryBuilder()
    complex_query = (
        qb.equals("status", "active")
        .equals("type", "premium")
        .not_equals("deleted_at", None)  # Simula registros não deletados
        .contains("description", "premium")  # Usando contains que existe
        .equals("verified", True)
        .sort_desc("created_at")
        .sort_asc("name")
        .page(3)
        .page_size(50)
        .search("electronics")  # Usando search que existe
        .fields(["id", "name", "status"])  # Campos específicos
        .includes(["profile", "settings"])  # Incluir relacionados
        .excludes(["internal_notes"])  # Excluir campos
        .build()
    )

    print("Complex query:", complex_query)

    # Query usando factory function
    search_query = build_query(
        filters={
            "category": "electronics",
            "status": "published",
            "price_range": "100-500",
        },
        page=1,
        page_size=25,
    )
    print("Search query:", search_query)


def example_advanced_response_building() -> None:
    """Example: Advanced response construction using real methods."""
    # Success response com metadata
    rb = FlextApiClient.ResponseBuilder()
    success_response = (
        rb.success(
            data={
                "users": [
                    {"id": 1, "name": "Alice", "email": "alice@example.com"},
                    {"id": 2, "name": "Bob", "email": "bob@example.com"},
                ],
                "total": 2,
            },
            message="Users retrieved successfully",
        )
        .with_metadata({"query_time": "0.045s", "cache_hit": True, "version": "1.0"})
        .build()
    )
    print("Success response:", success_response)

    # Error response
    error_response = build_error_response("Invalid authentication credentials", 401)
    print("Error response:", error_response)

    # Paginated response usando a função correta
    paginated_response = build_paginated_response(
        data=[{"id": i, "name": f"Item {i}"} for i in range(1, 21)],
        current_page=2,
        page_size=20,
        total_items=100,
        message="Page retrieved successfully",
    )
    print("Paginated response keys:", list(paginated_response.keys()))


async def example_http_client_usage() -> None:
    """Example: HTTP client with real functionality."""
    # Criar cliente HTTP
    config = FlextApiClientConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30.0,
        headers={"Content-Type": "application/json", "User-Agent": "FlextAPI/1.0.0"},
    )

    client = FlextApiClient(config)

    try:
        # Fazer requisição GET real (se conexão disponível)
        response = await client.get("/posts/1")
        if response.success:
            print("GET request successful:", response.data)
        else:
            print("GET request failed:", response.error)
    except Exception as e:
        print(f"Network request failed: {e}")
    finally:
        await client.close()


def example_service_integration() -> None:
    """Example: API service integration."""
    # Criar serviço API
    api = create_flext_api()

    # Obter builder
    builder = api.get_builder()

    # Query usando builder do serviço
    query_builder = builder.for_query()
    query = (
        query_builder.equals("status", "published")
        .sort_desc("created_at")
        .page(1)
        .page_size(10)
        .build()
    )
    print("Service query:", query)

    # Response usando builder do serviço
    response_builder = builder.for_response()
    response = response_builder.success(data={"message": "Hello from service"}).build()
    print("Service response:", response)


def example_factory_functions_advanced() -> None:
    """Example: Advanced usage of factory functions."""
    # Query avançada
    advanced_query = build_query(
        filters={"status": "active", "category": "premium", "region": "US"},
        search="electronics",
        page=2,
        page_size=50,
    )
    print("Advanced query:", advanced_query)

    # Success response avançada
    advanced_success = build_success_response(
        data={
            "users": [
                {"id": 1, "name": "John", "role": "admin"},
                {"id": 2, "name": "Jane", "role": "user"},
            ],
            "pagination": {"current_page": 1, "total_pages": 10, "total_items": 200},
        },
        message="Advanced data retrieved successfully",
    )
    print("Advanced success has data:", "data" in advanced_success)

    # Error response avançado
    advanced_error = build_error_response(
        message="Database connection timeout", status_code=503
    )
    print("Advanced error:", advanced_error["message"])


async def main() -> None:
    """Run all examples."""
    print("=== Advanced Query Building ===")
    example_advanced_query_building()

    print("\n=== Advanced Response Building ===")
    example_advanced_response_building()

    print("\n=== Service Integration ===")
    example_service_integration()

    print("\n=== Factory Functions Advanced ===")
    example_factory_functions_advanced()

    print("\n=== HTTP Client Usage ===")
    await example_http_client_usage()


if __name__ == "__main__":
    asyncio.run(main())
