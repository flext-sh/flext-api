#!/usr/bin/env python3
"""FLEXT API - Basic usage examples (corrected).

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This example demonstrates basic FLEXT API usage with real functionality.
All methods used exist and work as expected.

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

    # Construir query complexa
    qb2 = FlextApiQueryBuilder()  # Nova instância para query complexa
    (
        qb2.equals("department", "engineering")
        .greater_than("salary", 50000)
        .equals("active", value=True)
        .sort_asc("last_name")
        .sort_desc("hire_date")
        .page(2)
        .page_size(25)  # Página 2, 25 itens por página
        .build()
    )

    # Query com paginação
    qb3 = FlextApiQueryBuilder()  # Nova instância para query paginada
    (
        qb3.equals("status", "published")
        .greater_than("views", 1000)
        .sort_desc("popularity")
        .page(1)  # Primeira página
        .page_size(50)  # 50 itens
        .build()
    )


def example_response_builder() -> None:
    """Demonstrate how to use ``FlextApiResponseBuilder``."""
    # Response builder
    rb = FlextApiResponseBuilder()

    # Success response
    (
        rb.success(data={"id": 1, "name": "John"}, message="User created")
        .metadata({"timestamp": "2025-01-01T00:00:00Z", "request_id": "req-123"})
        .build()
    )

    # Error response
    rb2 = FlextApiResponseBuilder()  # Nova instância para error response
    (
        rb2.error("Validation failed")
        .metadata({"field_errors": {"email": "Invalid format"}})
        .build()
    )

    # Paginated response
    rb3 = FlextApiResponseBuilder()  # Nova instância para paginated response
    (
        rb3.success(data=[{"id": 1}, {"id": 2}])
        .pagination(page=1, page_size=10, total=100)
        .metadata({"query_time": "0.045s"})
        .build()
    )


def example_factory_functions() -> None:
    """Demonstrate how to use factory functions."""
    # Build query using factory function
    query_dict = {"status": "active", "type": "premium"}
    # build_query expects list[dict[str, object]]; convert dict to list with object values
    query_filters: list[dict[str, object]] = [
        {"field": str(k), "value": v, "operator": "eq"} for k, v in query_dict.items()
    ]
    build_query(query_filters)

    # Build success response
    success_data = {"users": [{"id": 1}, {"id": 2}], "count": 2}
    build_success_response(
        data=success_data,
        message="Users retrieved successfully",
        metadata={"execution_time": "0.123s"},
    )

    # Build error response
    build_error_response(
        error="Database connection failed",
        status_code=503,
        metadata={"details": {"retry_after": 30}},
    )


async def example_api_service() -> None:
    """Demonstrate how to use the ``FlextApi`` service."""
    # Criar API service
    api = create_flext_api()

    # Start service
    await api.start()

    # Health check
    api.health_check()

    # Get builder
    builder = api.get_builder()
    query_builder = builder.for_query()
    query_builder.equals("active", value=True).build()

    # Create HTTP client
    client_result = api.flext_api_create_client(
        {
            "base_url": "https://api.example.com",
            "timeout": 30.0,
            "headers": {"Authorization": "Bearer token123"},
        },
    )

    if client_result.success and client_result.data is not None:
        # Get client from service
        api.get_client()

    # Stop service
    await api.stop()


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

    # Start client
    await client.start()

    # Mock HTTP requests (since we don't want real network calls in examples)

    # Health check
    client.health_check()

    # Stop client
    await client.stop()


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
        .greater_than("price", 100)
        .sort_desc("rating")
        .page(1)
        .page_size(20)
        .build()
    )

    # Get response builder
    response_builder = builder.for_response()
    (
        response_builder.success(data={"products": [], "total": 0})
        .metadata({"search_terms": ["technology", "high-price"]})
        .pagination(page=1, page_size=20, total=0)
        .build()
    )


async def main() -> None:
    """Run all examples."""
    try:
        # Basic examples
        example_query_builder()
        example_response_builder()
        example_factory_functions()
        example_main_builder()
        example_fastapi_app()

        # Async examples
        await example_api_service()
        await example_http_client()

    except (RuntimeError, ValueError, TypeError):
        raise


if __name__ == "__main__":
    asyncio.run(main())
