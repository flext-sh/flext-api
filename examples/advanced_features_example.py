#!/usr/bin/env python3
"""FLEXT API - Advanced Features Examples.

Este exemplo demonstra recursos avançados da FLEXT API com funcionalidade REAL.
Todos os métodos usados existem e funcionam.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from typing import cast

from flext_api import (
    ClientConfigDict,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    PaginationConfig,
    build_error_response,
    build_paginated_response as build_paginated,
    build_query,
    build_success_response,
    create_client,
    create_flext_api,
    create_flext_api_app,
)


def example_advanced_query_building() -> None:
    """Example: Advanced query construction using all features."""
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

    complex_query.to_dict()

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
    build_query(factory_filters)


def example_advanced_response_building() -> None:
    """Example: Advanced response construction with metadata and pagination."""
    # Response com metadados complexos
    rb = FlextApiResponseBuilder()
    (
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

    # Response paginada com metadados detalhados
    products = [
        {"id": i, "name": f"Product {i}", "price": 99.99 + i} for i in range(1, 21)
    ]

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

    (paginated_response.value if isinstance(paginated_response.value, list) else [])


async def example_advanced_client_configuration() -> None:
    """Example: Advanced HTTP client configuration with plugins."""
    # Client with multiple plugins using factory function

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

        # Health check detalhado
        client.health_check()

    except (ConnectionError, TimeoutError):
        pass
    finally:
        await client.stop()


async def example_full_api_service_integration() -> None:
    """Example: Complete API service integration with all components."""
    # Criar serviço completo
    api = create_flext_api()

    try:
        # Inicializar serviço
        await api.start_async()

        # Health check do serviço
        health_result = await api.health_check_async()
        if health_result.success and health_result.value is not None:
            pass

        # Obter builder e criar query complexa
        builder = api.get_builder()

        # Query builder avançada
        query_builder = builder.for_query()
        (
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

        (
            len(advanced_response.value)
            if isinstance(advanced_response.value, list)
            else 0
        )

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

        # ClientConfigDict imported at top for type casting
        client_result = api.create_client(cast("ClientConfigDict", client_config))
        if client_result.success and client_result.value is not None:
            pass

        # Verificar cliente do serviço
        api.get_client()

    except (ConnectionError, TimeoutError):
        pass
    finally:
        # Parar serviço
        await api.stop_async()


def example_factory_functions_advanced() -> None:
    """Example: Advanced usage of factory functions."""
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

    if isinstance(advanced_success.value, dict):
        users = advanced_success.value.get("users")
        if isinstance(users, list):
            len(users)

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

    details = advanced_error.metadata.get("details", {})
    (details.get("support_reference") if isinstance(details, dict) else None)


def example_comprehensive_fastapi_app() -> None:
    """Example: Complete FastAPI application with all features."""
    # Criar aplicação FastAPI completa
    app = create_flext_api_app()

    # Listar todas as rotas disponíveis
    route_count = 0
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            ", ".join(sorted(route.methods))
            route_count += 1


async def main() -> None:
    """Execute all advanced examples."""
    # Sync examples
    example_advanced_query_building()
    example_advanced_response_building()
    example_factory_functions_advanced()
    example_comprehensive_fastapi_app()

    # Async examples
    await example_advanced_client_configuration()
    await example_full_api_service_integration()


if __name__ == "__main__":
    asyncio.run(main())
