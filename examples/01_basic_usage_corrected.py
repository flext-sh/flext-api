#!/usr/bin/env python3
"""FLEXT API - Basic Usage Examples (CORRECTED).

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Este exemplo demonstra o uso básico da FLEXT API com funcionalidade REAL.
Todos os métodos usados existem e funcionam.
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
    flext_api_create_app,
)


def example_query_builder() -> None:
    """Exemplo: Como usar o FlextApiQueryBuilder com métodos REAIS."""
    print("=== FlextApiQueryBuilder Example ===")

    # Criar query builder
    qb = FlextApiQueryBuilder()

    # Construir query simples usando APENAS métodos que existem
    simple_query = (
        qb.equals("status", "active")
        .equals("type", "user")
        .sort_desc("created_at")
        .build()
    )

    print("Simple Query:", simple_query)

    # Construir query complexa
    qb2 = FlextApiQueryBuilder()  # Nova instância para query complexa
    complex_query = (
        qb2.equals("department", "engineering")
        .greater_than("salary", 50000)
        .equals("active", is_true=True)
        .sort_asc("last_name")
        .sort_desc("hire_date")
        .page(2, 25)  # Página 2, 25 itens por página
        .build()
    )

    print("Complex Query:", complex_query)

    # Query com paginação
    qb3 = FlextApiQueryBuilder()  # Nova instância para query paginada
    paginated_query = (
        qb3.equals("status", "published")
        .greater_than("views", 1000)
        .sort_desc("popularity")
        .page(1, 50)  # Primeira página, 50 itens
        .build()
    )

    print("Paginated Query:", paginated_query)


def example_response_builder() -> None:
    """Exemplo: Como usar o FlextApiResponseBuilder."""
    print("\n=== FlextApiResponseBuilder Example ===")

    # Response builder
    rb = FlextApiResponseBuilder()

    # Success response
    success_resp = (
        rb.success(data={"id": 1, "name": "John"}, message="User created")
        .with_metadata("timestamp", "2025-01-01T00:00:00Z")
        .with_metadata("request_id", "req-123")
        .build()
    )

    print("Success Response:", success_resp)

    # Error response
    rb2 = FlextApiResponseBuilder()  # Nova instância para error response
    error_resp = (
        rb2.error("Validation failed", 400)
        .with_metadata("field_errors", {"email": "Invalid format"})
        .build()
    )

    print("Error Response:", error_resp)

    # Paginated response
    rb3 = FlextApiResponseBuilder()  # Nova instância para paginated response
    paginated_resp = (
        rb3.success(data=[{"id": 1}, {"id": 2}])
        .with_pagination(total=100, page=1, page_size=10)
        .with_metadata("query_time", "0.045s")
        .build()
    )

    print("Paginated Response:", paginated_resp)


def example_factory_functions() -> None:
    """Exemplo: Como usar as funções factory."""
    print("\n=== Factory Functions Example ===")

    # Build query usando função factory
    query_dict = {"status": "active", "type": "premium"}
    query_result = build_query(query_dict)
    print("Factory Query:", query_result)

    # Build success response
    success_data = {"users": [{"id": 1}, {"id": 2}], "count": 2}
    success_resp = build_success_response(
        data=success_data,
        message="Users retrieved successfully",
        metadata={"execution_time": "0.123s"},
    )
    print("Factory Success Response:", success_resp)

    # Build error response
    error_resp = build_error_response(
        message="Database connection failed",
        code=503,
        details={"retry_after": 30},
    )
    print("Factory Error Response:", error_resp)


async def example_api_service() -> None:
    """Exemplo: Como usar o FlextApi service."""
    print("\n=== FlextApi Service Example ===")

    # Criar API service
    api = create_flext_api()

    # Start service
    start_result = await api.start()
    print("Service started:", start_result.is_success)

    # Health check
    health_result = api.health_check()
    print("Health check:", health_result.data)

    # Get builder
    builder = api.get_builder()
    query_builder = builder.for_query()
    query = query_builder.equals("active", is_true=True).build()
    print("Service Query:", query)

    # Create HTTP client
    client_result = api.flext_api_create_client(
        {
            "base_url": "https://api.example.com",
            "timeout": 30.0,
            "headers": {"Authorization": "Bearer token123"},
        }
    )

    if client_result.is_success:
        client = client_result.data
        print("Client created successfully:", client.config.base_url)

        # Get client from service
        service_client = api.get_client()
        print("Client from service:", service_client is not None)

    # Stop service
    stop_result = await api.stop()
    print("Service stopped:", stop_result.is_success)


async def example_http_client() -> None:
    """Exemplo: Como usar o FlextApiClient."""
    print("\n=== FlextApiClient Example ===")

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
    print("Client configured with:")
    print(f"  Base URL: {client.config.base_url}")
    print(f"  Timeout: {client.config.timeout}s")
    print(f"  Max Retries: {client.config.max_retries}")
    print(f"  Headers: {client.config.headers}")

    # Health check
    health_result = client.health_check()
    print("Client Health:", health_result.data)

    # Stop client
    await client.stop()
    print("Client stopped successfully")


def example_fastapi_app() -> None:
    """Exemplo: Como criar a aplicação FastAPI."""
    print("\n=== FastAPI Application Example ===")

    # Create FastAPI app
    app = flext_api_create_app()

    print("FastAPI app created:")
    print(f"  Title: {app.title}")
    print(f"  Description: {app.description}")
    print(f"  Version: {app.version}")

    # List routes
    print("Available routes:")
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            print(f"  {route.methods} {route.path}")


def example_main_builder() -> None:
    """Exemplo: Como usar o FlextApiBuilder principal."""
    print("\n=== FlextApiBuilder Example ===")

    # Create main builder
    builder = FlextApiBuilder()

    # Get query builder
    query_builder = builder.for_query()
    query = (
        query_builder.equals("category", "technology")
        .greater_than("price", 100)
        .sort_desc("rating")
        .page(1, 20)
        .build()
    )
    print("Main Builder Query:", query)

    # Get response builder
    response_builder = builder.for_response()
    response = (
        response_builder.success(data={"products": [], "total": 0})
        .with_metadata("search_terms", ["technology", "high-price"])
        .with_pagination(total=0, page=1, page_size=20)
        .build()
    )
    print("Main Builder Response:", response)


async def main() -> None:
    """Execute all examples."""
    print("FLEXT API - Complete Working Examples")
    print("=" * 50)

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

        print("\n" + "=" * 50)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("All methods used exist and work correctly.")

    except (RuntimeError, ValueError, TypeError) as e:
        print(f"\n❌ ERROR in examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
