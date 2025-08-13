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
    build_query,
    build_success_response,
    create_flext_api,
    create_flext_api_app,
)


def example_advanced_query_building() -> None:
    """Example: Advanced query construction using all features."""
    print("=== Advanced Query Building Example ===")

    # Query complexa com múltiplos filtros e ordenação
    qb = FlextApiQueryBuilder()
    complex_query = (
        qb.equals("status", "active")
        .equals("type", "premium")
        .greater_than("created_at", "2024-01-01")
        .greater_than("score", 8.5)
        .equals("verified", value=True)
        .sort_desc("created_at")
        .sort_asc("name")
        .sort_desc("score")
        .page(3)
        .page_size(50)  # Página 3, 50 itens por página
        .build()
    )

    print("Complex Query with Multiple Filters:")
    print(f"  Filters: {len(complex_query.filters)}")
    print(f"  Sorts: {len(complex_query.sorts)}")
    print(f"  Page: {complex_query.page}, Size: {complex_query.page_size}")
    as_dict = complex_query.to_dict()
    print(f"  Offset: {as_dict['offset']}, Limit: {as_dict['limit']}")

    # Construir query usando factory function com filtros
    search_filters = {
        "category": "electronics",
        "brand": "apple",
        "in_stock": True,
        "rating": 5,
    }
    factory_filters = [
        {"field": k, "value": v, "operator": "eq"} for k, v in search_filters.items()
    ]
    factory_query = build_query(factory_filters)
    print(f"\nFactory Query: {len(factory_query.filters)} filters applied")
    print(f"Query structure: {factory_query}")


def example_advanced_response_building() -> None:
    """Example: Advanced response construction with metadata and pagination."""
    print("\n=== Advanced Response Building Example ===")

    # Response com metadados complexos
    rb = FlextApiResponseBuilder()
    complex_response = (
        rb.success(data={"results": [], "summary": {"total": 0, "categories": 3}})
        .metadata(
            {
                "query_id": "qry_12345",
                "execution_time_ms": 234,
                "cache_hit": True,
                "database_queries": 2,
                "facets": {"categories": ["electronics", "books", "clothing"]},
                "suggestions": ["apple", "samsung", "google"],
            },
        )
        .build()
    )

    print("Complex Response with Rich Metadata:")
    print(f"  Success: {complex_response.success}")
    print(f"  Metadata keys: {list(complex_response.metadata.keys())}")
    print(f"  Has suggestions: {'suggestions' in complex_response.metadata}")

    # Response paginada com metadados detalhados
    products = [
        {"id": i, "name": f"Product {i}", "price": 99.99 + i} for i in range(1, 21)
    ]

    from flext_api.api_client import (
        PaginationConfig,
        build_paginated_response as build_paginated,
    )

    paginated_response = build_paginated(
        PaginationConfig(
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
        ),
    )

    print("\nPaginated Response:")
    data_list = (
        paginated_response.data if isinstance(paginated_response.data, list) else []
    )
    print(f"  Data items: {len(data_list)}")
    pagination = paginated_response.pagination or {}
    print(f"  Total pages: {pagination.get('total_pages')}")
    print(f"  Has next: {pagination.get('has_next')}")
    print(f"  Has previous: {pagination.get('has_previous')}")
    print(f"  Metadata: {list(paginated_response.metadata.keys())}")


async def example_advanced_client_configuration() -> None:
    """Example: Advanced HTTP client configuration with plugins."""
    print("\n=== Advanced Client Configuration Example ===")

    # Client with multiple plugins using factory function
    from flext_api import create_client

    client = create_client(
        {
            "base_url": "https://api.github.com",
            "timeout": 45.0,
            "headers": {
                "User-Agent": "FlextAPI-Advanced/2.0.0",
                "Accept": "application/vnd.github.v3+json",
                "X-Request-ID": "req_advanced_example_001",
            },
            "max_retries": 5,
        },
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
        health_data = client.health_check()
        print("\nClient Health Status:")
        print(f"  Status: {health_data['status']}")

        print("  Advanced client ready for production use")

    except (ConnectionError, TimeoutError) as e:
        print(f"Client configuration error: {e}")
    finally:
        await client.stop()


async def example_full_api_service_integration() -> None:
    """Example: Complete API service integration with all components."""
    print("\n=== Full API Service Integration Example ===")

    # Criar serviço completo
    api = create_flext_api()

    try:
        # Inicializar serviço
        start_result = await api.start()
        print(f"API Service Started: {start_result.success}")

        # Health check do serviço
        health_result = await api.health_check()
        if health_result.success and health_result.data is not None:
            health_data = health_result.data
            print(f"Service Health: {health_data['status']}")
            print(f"Client Configured: {health_data.get('client_configured', False)}")

        # Obter builder e criar query complexa
        builder = api.get_builder()

        # Query builder avançada
        query_builder = builder.for_query()
        advanced_query = (
            query_builder.equals("department", "engineering")
            .equals("level", "senior")
            .greater_than("experience_years", 5)
            .greater_than("salary", 80000)
            .equals("remote_eligible", value=True)
            .sort_desc("salary")
            .sort_asc("hire_date")
            .sort_desc("performance_rating")
            .page(1)
            .page_size(25)
            .build()
        )

        print("\nAdvanced Query Built:")
        print(f"  Filters: {len(advanced_query.filters)}")
        print(f"  Sorts: {len(advanced_query.sorts)}")
        page_info = f"page {advanced_query.page}, size {advanced_query.page_size}"
        print(f"  Pagination: {page_info}")

        # Response builder avançada
        response_builder = builder.for_response()
        mock_employees = [
            {"id": i, "name": f"Engineer {i}", "salary": 90000 + (i * 5000)}
            for i in range(1, 6)
        ]

        advanced_response = (
            response_builder.success(
                data=mock_employees,
                message="Senior engineers retrieved",
            )
            .metadata(
                {
                    "query_complexity": "high",
                    "optimization_applied": True,
                    "cache_strategy": "write_through",
                    "data_source": "primary_db",
                    "query_plan": "index_scan_optimal",
                },
            )
            .pagination(page=1, page_size=25, total=147)
            .build()
        )

        print("\nAdvanced Response Built:")
        print(f"  Success: {advanced_response.success}")
        data_count = (
            len(advanced_response.data)
            if isinstance(advanced_response.data, list)
            else 0
        )
        print(f"  Data Count: {data_count}")
        pag = advanced_response.pagination or {}
        print(f"  Total Records: {pag.get('total')}")
        print(f"  Metadata Keys: {list(advanced_response.metadata.keys())}")

        # Criar cliente HTTP via serviço
        client_config = {
            "base_url": "https://api.production-company.com",
            "timeout": 60.0,
            "headers": {
                "Authorization": "Bearer prod_token_12345",
                "X-Service": "flext-api-advanced",
                "X-Version": "0.9.0",
            },
        }

        client_result = api.flext_api_create_client(client_config)
        if client_result.success and client_result.data is not None:
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
        print(f"API Service Stopped: {stop_result.success}")


def example_factory_functions_advanced() -> None:
    """Example: Advanced usage of factory functions."""
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
    users_count = 0
    if isinstance(advanced_success.data, dict):
        users = advanced_success.data.get("users")
        if isinstance(users, list):
            users_count = len(users)
    print(f"  Users count: {users_count}")
    print(f"  Metadata entries: {len(advanced_success.metadata)}")
    has_security = "security_context" in advanced_success.metadata
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
        error="Multiple validation errors occurred",
        status_code=422,
        metadata={"error_code": "VALIDATION_FAILED_MULTIPLE", "details": error_details},
    )

    print("\nAdvanced Error Response:")
    print(f"  Error code: {advanced_error.metadata.get('error_code')}")
    print(f"  Has validation details: {'details' in advanced_error.metadata}")
    details = advanced_error.metadata.get("details", {})
    support_ref = (
        details.get("support_reference") if isinstance(details, dict) else None
    )
    print(f"  Support reference: {support_ref}")


def example_comprehensive_fastapi_app() -> None:
    """Example: Complete FastAPI application with all features."""
    print("\n=== Comprehensive FastAPI Application Example ===")

    # Criar aplicação FastAPI completa
    app = create_flext_api_app()

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
