"""Performance benchmarks for FLEXT API components.

Benchmarks the key operations for performance regression testing.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from collections.abc import Callable
from typing import TypeVar

from flext_api import (
    FlextApi,
    FlextApiClient,
    FlextApiModels,
    create_flext_api,
)

T = TypeVar("T")


class TestAPIPerformanceBenchmarks:
    """Performance benchmarks for API operations."""

    def test_api_creation_benchmark(
        self, benchmark: Callable[[Callable[[], FlextApi]], FlextApi]
    ) -> None:
        """Benchmark API instance creation."""

        def create_api() -> FlextApi:
            return create_flext_api()

        result = benchmark(create_api)
        assert result is not None

    def test_query_building_benchmark(
        self,
        benchmark: Callable[
            [Callable[[], FlextApiModels.QueryBuilder]], FlextApiModels.QueryBuilder
        ],
    ) -> None:
        """Benchmark query building operations."""

        def build_complex_query() -> FlextApiModels.QueryBuilder:
            models = FlextApiModels()
            builder = models.QueryBuilder()
            # Add filters
            builder.add_filter("status", "active")
            builder.add_filter("category", "premium")
            builder.add_filter("created_at", "2024-01-01")
            builder.add_filter("limit", 50)
            return builder

        result = benchmark(build_complex_query)
        assert result is not None
        assert len(result.filters) > 0

    def test_response_building_benchmark(
        self, benchmark: Callable[[Callable[[], object]], object]
    ) -> None:
        """Benchmark response building operations."""

        def build_complex_response() -> object:
            models = FlextApiModels()
            builder = models.ResponseBuilder()
            response_result = builder.success(
                data={"items": list(range(100)), "total": 100},
                message="Data retrieved successfully",
            )
            return response_result.data if response_result.success else None

        result = benchmark(build_complex_response)
        assert result is not None
        assert isinstance(result, dict)

    def test_builder_pattern_benchmark(
        self,
        benchmark: Callable[
            [Callable[[], tuple[FlextApiModels.QueryBuilder, object]]],
            tuple[FlextApiModels.QueryBuilder, object],
        ],
    ) -> None:
        """Benchmark builder pattern operations."""

        def complex_builder_operations() -> tuple[FlextApiModels.QueryBuilder, object]:
            models = FlextApiModels()

            # Query building
            query_builder = models.QueryBuilder()
            query_builder.add_filter("status", "published")
            query_builder.add_filter("created_at", "2024-01-01")
            query_builder.sort_by = "updated_at"
            query_builder.sort_order = "desc"
            query_builder.page = 2
            query_builder.page_size = 25

            # Response building
            response_builder = models.ResponseBuilder()
            response_result = response_builder.success(data={"items": list(range(25))})
            response_data = response_result.data if response_result.success else None

            return query_builder, response_data

        query, response = benchmark(complex_builder_operations)
        assert query is not None
        assert response is not None

    def test_client_creation_benchmark(
        self, benchmark: Callable[[Callable[[], FlextApiClient]], FlextApiClient]
    ) -> None:
        """Benchmark HTTP client creation."""

        def create_configured_client() -> FlextApiClient:
            api = create_flext_api()
            client_result = api.create_client(
                {
                    "base_url": "https://api.example.com",
                    "timeout": 30.0,
                    "max_retries": 3,
                }
            )
            return (
                client_result.data
                if client_result.success
                else FlextApiClient(base_url="https://fallback.com")
            )

        result = benchmark(create_configured_client)
        assert result is not None
        assert result.base_url == "https://api.example.com"

    def test_multiple_queries_benchmark(
        self,
        benchmark: Callable[
            [Callable[[], list[FlextApiModels.QueryBuilder]]],
            list[FlextApiModels.QueryBuilder],
        ],
    ) -> None:
        """Benchmark multiple query operations."""

        def build_multiple_queries() -> list[FlextApiModels.QueryBuilder]:
            queries = []
            models = FlextApiModels()

            for i in range(100):
                query_builder = models.QueryBuilder()
                query_builder.add_filter("id", i)
                query_builder.add_filter(
                    "status", "active" if i % 2 == 0 else "inactive"
                )
                query_builder.add_filter("priority", "high" if i % 3 == 0 else "normal")
                queries.append(query_builder)
            return queries

        result = benchmark(build_multiple_queries)
        assert len(result) == 100
        assert all(len(q.filters) > 0 for q in result)

    def test_large_response_benchmark(
        self, benchmark: Callable[[Callable[[], object]], object]
    ) -> None:
        """Benchmark large response building."""

        def build_large_response() -> object:
            # Simulate large dataset response
            large_data = {
                "items": [
                    {"id": i, "name": f"Item {i}", "value": i * 2} for i in range(1000)
                ],
                "metadata": {f"key_{i}": f"value_{i}" for i in range(50)},
                "total": 1000,
            }

            models = FlextApiModels()
            builder = models.ResponseBuilder()
            response_result = builder.success(
                data=large_data, message="Large dataset retrieved"
            )
            return response_result.data if response_result.success else None

        result = benchmark(build_large_response)
        assert result is not None
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert len(result["data"]["items"]) == 1000

    def test_paginated_response_benchmark(
        self,
        benchmark: Callable[[Callable[[], list[object]]], list[object]],
    ) -> None:
        """Benchmark paginated response operations."""

        def build_paginated_responses() -> list[object]:
            responses = []
            models = FlextApiModels()

            for page in range(1, 11):  # 10 pages
                builder = models.ResponseBuilder()
                response_result = builder.success(
                    data={"items": list(range((page - 1) * 20, page * 20))},
                    message=f"Page {page} of 10",
                )
                if response_result.success:
                    responses.append(response_result.data)
            return responses

        result = benchmark(build_paginated_responses)
        assert len(result) == 10
        assert all(isinstance(r, dict) and r.get("status") == "success" for r in result)
