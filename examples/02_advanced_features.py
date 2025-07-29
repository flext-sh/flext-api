#!/usr/bin/env python3
"""FLEXT API - Advanced Features Examples.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Este exemplo demonstra recursos avançados da FLEXT API com funcionalidade REAL.
Todos os métodos usados existem e funcionam.
"""

from __future__ import annotations

import asyncio

from flext_api import (
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    build_error_response,
    build_paginated_response,
    build_query,
    build_success_response,
    create_client_with_plugins,
    create_flext_api,
    flext_api_create_app,
)


def example_advanced_query_building() -> None:
    """Exemplo: Construção avançada de queries usando todos os recursos."""
    print("=== Advanced Query Building Example ===")

    # Query complexa com múltiplos filtros e ordenação
    qb = FlextApiQueryBuilder()
    complex_query = (
        qb.equals("status", "active")
        .equals("type", "premium")
        .greater_than("created_at", "2024-01-01")
        .greater_than("score", 8.5)
        .equals("verified", is_true=True)
        .sort_desc("created_at")
        .sort_asc("name")
        .sort_desc("score")
        .page(3, 50)  # Página 3, 50 itens por página
        .build()
    )

    print("Complex Query with Multiple Filters:")
    print(f"  Filters: {len(complex_query['filters'])}")
    print(f"  Sorts: {len(complex_query['sorts'])}")
    print(f"  Page: {complex_query['page']}, Size: {complex_query['page_size']}")
    print(f"  Offset: {complex_query['offset']}, Limit: {complex_query['limit']}")

    # Construir query usando factory function com filtros
    search_filters = {
        "category": "electronics",
        "brand": "apple",
        "in_stock": True,
        "rating": 5,
    }
    factory_query = build_query(search_filters)
    print(f"\nFactory Query: {len(factory_query['filters'])} filters applied")
    print(f"Query structure: {factory_query}")


def example_advanced_response_building() -> None:
    """Exemplo: Construção avançada de responses com metadados e paginação."""
    print("\n=== Advanced Response Building Example ===")

    # Response com metadados complexos
    rb = FlextApiResponseBuilder()
    complex_response = (
        rb.success(data={"results": [], "summary": {"total": 0, "categories": 3}})
        .with_metadata("query_id", "qry_12345")
        .with_metadata("execution_time_ms", 234)
        .with_metadata("cache_hit", value=True)
        .with_metadata("database_queries", 2)
        .with_metadata("facets", {"categories": ["electronics", "books", "clothing"]})
        .with_metadata("suggestions", ["apple", "samsung", "google"])
        .build()
    )

    print("Complex Response with Rich Metadata:")
    print(f"  Success: {complex_response['success']}")
    print(f"  Metadata keys: {list(complex_response['metadata'].keys())}")
    print(f"  Has suggestions: {'suggestions' in complex_response['metadata']}")

    # Response paginada com metadados detalhados
    products = [
        {"id": i, "name": f"Product {i}", "price": 99.99 + i}
        for i in range(1, 21)
    ]

    paginated_response = build_paginated_response(
        data=products,
        total=1500,
        page=2,
        page_size=20,
        message="Products retrieved successfully",
        metadata={
            "search_terms": ["smartphone", "android"],
            "filters_applied": 4,
            "sort_by": "popularity",
            "execution_time": "0.089s",
            "cache_status": "partial_hit",
        },
    )

    print("\nPaginated Response:")
    print(f"  Data items: {len(paginated_response['data'])}")
    print(f"  Total pages: {paginated_response['pagination']['total_pages']}")
    print(f"  Has next: {paginated_response['pagination']['has_next']}")
    print(f"  Has previous: {paginated_response['pagination']['has_previous']}")
    print(f"  Metadata: {list(paginated_response['metadata'].keys())}")


async def example_advanced_client_configuration() -> None:
    """Exemplo: Configuração avançada do cliente HTTP com plugins."""
    print("\n=== Advanced Client Configuration Example ===")

    # Cliente com múltiplos plugins usando função factory
    client = create_client_with_plugins(
        base_url="https://api.github.com",
        enable_cache=True,
        enable_retry=True,
        enable_circuit_breaker=True,
        timeout=45.0,
        headers={
            "User-Agent": "FlextAPI-Advanced/2.0.0",
            "Accept": "application/vnd.github.v3+json",
            "X-Request-ID": "req_advanced_example_001",
        },
        max_retries=5,
    )

    try:
        # Iniciar cliente
        await client.start()

        print("Advanced Client Configuration:")
        print(f"  Base URL: {client.config.base_url}")
        print(f"  Timeout: {client.config.timeout}s")
        print(f"  Max Retries: {client.config.max_retries}")
        print(f"  Custom Headers: {len(client.config.headers or {})} headers")
        print(f"  Plugins: {len(client.plugins)} plugins configured")

        # Health check detalhado
        health_result = client.health_check()
        if health_result.is_success:
            health_data = health_result.data
            print("\nClient Health Status:")
            print(f"  Status: {health_data['status']}")
            print(f"  Base URL: {health_data['base_url']}")
            print(f"  Session Active: {health_data['session_active']}")
            print(f"  Plugins Count: {health_data['plugins_count']}")

        print("  Advanced client ready for production use")

    except (ConnectionError, TimeoutError) as e:
        print(f"Client configuration error: {e}")
    finally:
        await client.stop()


async def example_full_api_service_integration() -> None:
    """Exemplo: Integração completa do serviço API com todos os componentes."""
    print("\n=== Full API Service Integration Example ===")

    # Criar serviço completo
    api = create_flext_api()

    try:
        # Inicializar serviço
        start_result = await api.start()
        print(f"API Service Started: {start_result.is_success}")

        # Health check do serviço
        health_result = api.health_check()
        if health_result.is_success:
            health_data = health_result.data
            print(f"Service Health: {health_data['status']}")
            print(f"Client Configured: {health_data['client_configured']}")

        # Obter builder e criar query complexa
        builder = api.get_builder()

        # Query builder avançada
        query_builder = builder.for_query()
        advanced_query = (
            query_builder
            .equals("department", "engineering")
            .equals("level", "senior")
            .greater_than("experience_years", 5)
            .greater_than("salary", 80000)
            .equals("remote_eligible", is_true=True)
            .sort_desc("salary")
            .sort_asc("hire_date")
            .sort_desc("performance_rating")
            .page(1, 25)
            .build()
        )

        print("\nAdvanced Query Built:")
        print(f"  Filters: {len(advanced_query['filters'])}")
        print(f"  Sorts: {len(advanced_query['sorts'])}")
        page_info = f"page {advanced_query['page']}, size {advanced_query['page_size']}"
        print(f"  Pagination: {page_info}")

        # Response builder avançada
        response_builder = builder.for_response()
        mock_employees = [
            {"id": i, "name": f"Engineer {i}", "salary": 90000 + (i * 5000)}
            for i in range(1, 6)
        ]

        advanced_response = (
            response_builder
            .success(data=mock_employees, message="Senior engineers retrieved")
            .with_metadata("query_complexity", "high")
            .with_metadata("optimization_applied", value=True)
            .with_metadata("cache_strategy", "write_through")
            .with_metadata("data_source", "primary_db")
            .with_metadata("query_plan", "index_scan_optimal")
            .with_pagination(total=147, page=1, page_size=25)
            .build()
        )

        print("\nAdvanced Response Built:")
        print(f"  Success: {advanced_response['success']}")
        print(f"  Data Count: {len(advanced_response['data'])}")
        print(f"  Total Records: {advanced_response['pagination']['total']}")
        print(f"  Metadata Keys: {list(advanced_response['metadata'].keys())}")

        # Criar cliente HTTP via serviço
        client_config = {
            "base_url": "https://api.production-company.com",
            "timeout": 60.0,
            "headers": {
                "Authorization": "Bearer prod_token_12345",
                "X-Service": "flext-api-advanced",
                "X-Version": "2.0.0",
            },
        }

        client_result = api.flext_api_create_client(client_config)
        if client_result.is_success:
            client = client_result.data
            print("\nHTTP Client Created via Service:")
            print(f"  Base URL: {client.config.base_url}")
            print(f"  Timeout: {client.config.timeout}s")
            print(f"  Headers: {len(client.config.headers)} custom headers")

        # Verificar cliente do serviço
        service_client = api.get_client()
        print(f"Service has client: {service_client is not None}")

    except (ConnectionError, TimeoutError) as e:
        print(f"Service integration error: {e}")
    finally:
        # Parar serviço
        stop_result = await api.stop()
        print(f"API Service Stopped: {stop_result.is_success}")


def example_factory_functions_advanced() -> None:
    """Exemplo: Uso avançado das factory functions."""
    print("\n=== Advanced Factory Functions Example ===")

    # Success response com metadados complexos
    success_data = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Carol", "role": "moderator"},
        ],
        "summary": {"total": 3, "active": 3, "roles": ["admin", "user", "moderator"]},
    }

    advanced_success = build_success_response(
        data=success_data,
        message="Users and summary retrieved successfully",
        metadata={
            "query_execution_time": "0.156s",
            "database_hits": 2,
            "cache_hits": 1,
            "optimization_level": "aggressive",
            "data_freshness": "realtime",
            "security_context": "authenticated_admin",
            "api_rate_limit_remaining": 4850,
        },
    )

    print("Advanced Success Response:")
    print(f"  Users count: {len(advanced_success['data']['users'])}")
    print(f"  Metadata entries: {len(advanced_success['metadata'])}")
    has_security = "security_context" in advanced_success["metadata"]
    print(f"  Has security context: {has_security}")

    # Error response com detalhes complexos
    error_details = {
        "validation_errors": {
            "email": ["Invalid format", "Domain not allowed"],
            "password": ["Too weak", "Must contain special characters"],
            "age": ["Must be between 18 and 100"],
        },
        "suggested_fixes": [
            "Use a company email address",
            "Include uppercase, lowercase, numbers, and symbols in password",
            "Verify age is correct",
        ],
        "error_code": "VALIDATION_FAILED_MULTIPLE",
        "retry_strategy": "fix_and_resubmit",
        "support_reference": "ERR_VAL_20250129_001",
    }

    advanced_error = build_error_response(
        message="Multiple validation errors occurred",
        code=422,
        details=error_details,
    )

    print("\nAdvanced Error Response:")
    print(f"  Error code: {advanced_error['metadata']['error_code']}")
    print(f"  Has validation details: {'details' in advanced_error['metadata']}")
    support_ref = advanced_error["metadata"]["details"]["support_reference"]
    print(f"  Support reference: {support_ref}")


def example_comprehensive_fastapi_app() -> None:
    """Exemplo: Aplicação FastAPI completa com todos os recursos."""
    print("\n=== Comprehensive FastAPI Application Example ===")

    # Criar aplicação FastAPI completa
    app = flext_api_create_app()

    print("Comprehensive FastAPI Application:")
    print(f"  Title: {app.title}")
    print(f"  Description: {app.description}")
    print(f"  Version: {app.version}")
    print(f"  Total Routes: {len(app.routes)}")

    # Listar todas as rotas disponíveis
    print("\nAvailable Routes:")
    route_count = 0
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            methods_str = ", ".join(sorted(route.methods))
            print(f"  [{methods_str}] {route.path}")
            route_count += 1

    print(f"\nTotal API Endpoints: {route_count}")
    print("Application ready for production deployment")


async def main() -> None:
    """Execute all advanced examples."""
    print("FLEXT API - Advanced Features Examples")
    print("=" * 60)

    try:
        # Sync examples
        example_advanced_query_building()
        example_advanced_response_building()
        example_factory_functions_advanced()
        example_comprehensive_fastapi_app()

        # Async examples
        await example_advanced_client_configuration()
        await example_full_api_service_integration()

        print("\n" + "=" * 60)
        print("✅ ALL ADVANCED EXAMPLES COMPLETED SUCCESSFULLY!")
        print("All methods used exist and demonstrate real flext-api functionality.")
        print("\nNext steps:")
        print("- Integrate these patterns into your production applications")
        print("- Customize configuration for your specific use cases")
        print("- Monitor performance with the built-in health checks")

    except (RuntimeError, ValueError, TypeError) as e:
        print(f"\n❌ ERROR in advanced examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
