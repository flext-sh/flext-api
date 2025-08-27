#!/usr/bin/env python3
"""FLEXT API - Basic usage examples (corrected).

This example demonstrates basic FLEXT API usage with real functionality.
All methods used exist and work as expected.

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
    build_error_response,
    build_query,
    build_success_response,
    create_flext_api,
    create_flext_api_app,
)


def example_query_builder() -> None:
    """Demonstrate how to use ``FlextApiQueryBuilder`` with real methods."""
    # Criar query builder
    qb = FlextApiQueryBuilder()

    # Construir query simples usando APENAS métodos que existem
    (
        qb.equals("status", "active")
        .equals("type", "user")
        .sort_desc("created_at")
        .build()
    )

    # Construir query complexa - usando apenas métodos que existem
    qb2 = FlextApiQueryBuilder()  # Nova instância para query complexa
    (
        qb2.equals("department", "engineering")
        .not_equals("salary", 0)  # Usando not_equals que existe, não greater_than
        .equals("active", True)  # Corrigido: value= não é necessário
        .sort_asc("last_name")
        .sort_desc("hire_date")
        .page(2)
        .page_size(25)  # Página 2, 25 itens por página
        .build()
    )

    # Query com paginação - usando apenas métodos que existem
    qb3 = FlextApiQueryBuilder()  # Nova instância para query paginada
    (
        qb3.equals("status", "published")
        .not_equals("views", 0)  # Usando not_equals, não greater_than
        .sort_desc("created_at")  # Campo que existe
        .page(1)  # Primeira página
        .page_size(50)  # 50 itens
        .build()
    )


def example_response_builder() -> None:
    """Demonstrate how to use ``FlextApiResponseBuilder`` with real methods."""
    # Response builder
    rb = FlextApiResponseBuilder()

    # Success response - usando apenas métodos que existem
    (
        rb.success(data={"id": 1, "name": "John"}, message="User created")
        .with_metadata(
            {"timestamp": "2025-01-01T00:00:00Z", "request_id": "req-123"}
        )  # with_metadata existe
        .build()
    )

    # Error response
    rb2 = FlextApiResponseBuilder()  # Nova instância para error response
    (
        rb2.error("Validation failed", 400)  # error() precisa de status_code
        .with_metadata(
            {"field_errors": {"email": "Invalid format"}}
        )  # with_metadata existe
        .build()
    )

    # Para paginated response, use PaginatedResponseBuilder ou build_paginated_response()
    # O ResponseBuilder comum não tem pagination() method


def example_factory_functions() -> None:
    """Demonstrate how to use factory functions with real signatures."""
    # Build query using factory function - build_query(**kwargs)
    query = build_query(
        filters={"status": "active", "type": "premium"}, page=1, page_size=20
    )
    print("Query built:", query)

    # Build success response - build_success_response(data, message)
    success_data = {"users": [{"id": 1}, {"id": 2}], "count": 2}
    success_response = build_success_response(
        data=success_data, message="Users retrieved successfully"
    )
    print("Success response:", success_response)

    # Build error response - build_error_response(message, status_code)
    error_response = build_error_response(
        message="Database connection failed", status_code=503
    )
    print("Error response:", error_response)


async def example_api_service() -> None:
    """Demonstrate how to use the ``FlextApi`` service."""
    # Criar API service
    api = create_flext_api()

    # Start service
    await api.start_async()

    # Health check
    api.health_check()

    # Get builder
    builder = api.get_builder()
    query_builder = builder.for_query()
    query_builder.equals("active", value=True).build()

    # Create HTTP client
    client_result = api.create_client(
        {
            "base_url": "https://api.example.com",
            "timeout": 30.0,
            "headers": {"Authorization": "Bearer token123"},
        },
    )

    if client_result.success and client_result.value is not None:
        # Get client from service
        api.get_client()

    # Stop service
    await api.stop_async()


async def example_http_client() -> None:
    """Demonstrate how to use ``FlextApiClient``."""
    # Configure client
    config = FlextApiClientConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30.0,
        headers={"User-Agent": "FlextAPI/1.0.0"},
        max_retries=3,
    )

    # Create client
    client = FlextApiClient(config)

    # FlextApiClient não tem métodos start(), stop(), health_check()
    # Esses métodos não existem na implementação atual

    try:
        # Example of actual HTTP request (commented to avoid network calls)
        # response = await client.get("/test")
        # print("Response:", response)
        print("Client created successfully")
    finally:
        await client.close()  # Use close() instead of stop()


def example_fastapi_app() -> None:
    """Demonstrate how to create the FastAPI application."""
    # Create FastAPI app
    app = create_flext_api_app()

    # List routes
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            pass


def example_main_builder() -> None:
    """Demonstrate how to use the main ``FlextApiBuilder``."""
    # Create main builder
    builder = FlextApiBuilder()

    # Get query builder
    query_builder = builder.for_query()
    (
        query_builder.equals("category", "technology")
        .not_equals("price", 0)  # Usando not_equals, não greater_than
        .sort_desc("rating")
        .page(1)
        .page_size(20)
        .build()
    )

    # Get response builder
    response_builder = builder.for_response()
    (
        response_builder.success(data={"products": [], "total": 0})
        .with_metadata(
            {"search_terms": ["technology", "high-price"]}
        )  # Corrigido para with_metadata
        # ResponseBuilder não tem pagination(), usar PaginatedResponseBuilder ou build_paginated_response()
        .build()
    )


async def main() -> None:
    """Run all examples."""
    # Basic examples
    example_query_builder()
    example_response_builder()
    example_factory_functions()
    example_main_builder()
    example_fastapi_app()

    # Async examples
    await example_api_service()
    await example_http_client()


if __name__ == "__main__":
    asyncio.run(main())
