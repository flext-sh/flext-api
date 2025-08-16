"""Performance benchmarks for FLEXT API components.

Benchmarks the key operations for performance regression testing.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_api import (
    FlextApi,
    FlextApiBuilder,
    FlextApiClient,
    FlextApiQuery,
    FlextApiResponse,
    build_query,
    build_success_response,
    create_client,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class TestAPIPerformanceBenchmarks:
    """Performance benchmarks for API operations."""

    def test_api_creation_benchmark(self, benchmark: Callable[[Any], Any]) -> None:
        """Benchmark API instance creation."""
        result = benchmark(FlextApi)
        assert result is not None

    def test_query_building_benchmark(self, benchmark: Callable[[Any], Any]) -> None:
        """Benchmark query building operations."""

        def build_complex_query() -> FlextApiQuery:
            return build_query(
                {
                    "status": "active",
                    "category": "premium",
                    "created_at": "2024-01-01",
                    "limit": 50,
                },
            )

        result = benchmark(build_complex_query)
        assert result is not None
        assert len(result.filters) > 0

    def test_response_building_benchmark(self, benchmark: Callable[[Any], Any]) -> None:
        """Benchmark response building operations."""

        def build_complex_response() -> dict[str, object]:
            return build_success_response(
                data={"items": list(range(100)), "total": 100},
                message="Data retrieved successfully",
                metadata={
                    "query_time": "0.042s",
                    "cache_hit": True,
                    "source": "database",
                },
            )

        result = benchmark(build_complex_response)
        assert result is not None
        assert result["success"] is True

    def test_builder_pattern_benchmark(self, benchmark: Callable[[Any], Any]) -> None:
        """Benchmark builder pattern operations."""

        def complex_builder_operations() -> tuple[FlextApiQuery, FlextApiResponse]:
            builder = FlextApiBuilder()

            query = (
                builder.for_query()
                .equals("status", "published")
                .greater_than("created_at", "2024-01-01")
                .sort_desc("updated_at")
                .page(2)
                .page_size(25)
                .build()
            )

            response = (
                builder.for_response()
                .success(data={"items": list(range(25))})
                .with_pagination(total=100, page=2, page_size=25)
                .with_metadata("query_time", "0.042s")
                .build()
            )

            return query, response

        query, response = benchmark(complex_builder_operations)
        assert query is not None
        assert response is not None

    def test_client_creation_benchmark(self, benchmark: Callable[[Any], Any]) -> None:
        """Benchmark HTTP client creation."""

        def create_configured_client() -> FlextApiClient:
            return create_client(
                {
                    "base_url": "https://api.example.com",
                    "timeout": 30.0,
                    "headers": {
                        "Content-Type": "application/json",
                        "User-Agent": "FlextAPI/1.0.0",
                    },
                    "max_retries": 3,
                },
            )

        result = benchmark(create_configured_client)
        assert result is not None
        assert result.config.base_url == "https://api.example.com"

    def test_multiple_queries_benchmark(self, benchmark: Callable[[Any], Any]) -> None:
        """Benchmark multiple query operations."""

        def build_multiple_queries() -> list[FlextApiQuery]:
            queries = []
            for i in range(100):
                query = build_query(
                    {
                        "id": i,
                        "status": "active" if i % 2 == 0 else "inactive",
                        "priority": "high" if i % 3 == 0 else "normal",
                    },
                )
                queries.append(query)
            return queries

        result = benchmark(build_multiple_queries)
        assert len(result) == 100
        assert all(len(q.filters) > 0 for q in result)

    def test_large_response_benchmark(self, benchmark: Callable[[Any], Any]) -> None:
        """Benchmark large response building."""

        def build_large_response() -> dict[str, object]:
            # Simulate large dataset response
            large_data = {
                "items": [
                    {"id": i, "name": f"Item {i}", "value": i * 2} for i in range(1000)
                ],
                "metadata": {f"key_{i}": f"value_{i}" for i in range(50)},
                "total": 1000,
            }

            return build_success_response(
                data=large_data,
                message="Large dataset retrieved",
                metadata={"processing_time": "1.234s"},
            )

        result = benchmark(build_large_response)
        assert result["success"] is True
        assert len(result["data"]["items"]) == 1000

    def test_paginated_response_benchmark(
        self,
        benchmark: Callable[[Any], Any],
    ) -> None:
        """Benchmark paginated response operations."""

        def build_paginated_responses() -> list[FlextApiResponse]:
            responses = []
            for page in range(1, 11):  # 10 pages
                builder = FlextApiBuilder()
                response = (
                    builder.for_response()
                    .success(data={"items": list(range((page - 1) * 20, page * 20))})
                    .with_pagination(total=200, page=page, page_size=20)
                    .with_metadata("page_info", f"Page {page} of 10")
                    .build()
                )
                responses.append(response)
            return responses

        result = benchmark(build_paginated_responses)
        assert len(result) == 10
        assert all(r.success for r in result)
