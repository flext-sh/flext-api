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
            [Callable[[], FlextApiModels.HttpQuery]], FlextApiModels.HttpQuery
        ],
    ) -> None:
        """Benchmark query building operations."""

        def build_complex_query() -> FlextApiModels.HttpQuery:
            builder = FlextApiModels.for_query()
            # Add filters using proper API
            return (
                builder.equals("status", "active")
                .equals("category", "premium")
                .equals("created_at", "2024-01-01")
            )

        result = benchmark(build_complex_query)
        assert result is not None

    def test_response_building_benchmark(
        self, benchmark: Callable[[Callable[[], object]], object]
    ) -> None:
        """Benchmark response building operations."""

        def build_complex_response() -> object:
            builder = FlextApiModels.for_query()
            response_result = builder.for_response().success(
                data={"items": list(range(100)), "total": 100},
                message="Data retrieved successfully",
            )
            return response_result.value if response_result.success else None

        result = benchmark(build_complex_response)
        assert result is not None
        assert isinstance(result, dict)

    def test_builder_pattern_benchmark(
        self,
        benchmark: Callable[
            [Callable[[], tuple[FlextApiModels.HttpQuery, object]]],
            tuple[FlextApiModels.HttpQuery, object],
        ],
    ) -> None:
        """Benchmark builder pattern operations."""

        def complex_builder_operations() -> tuple[FlextApiModels.HttpQuery, object]:
            builder = FlextApiModels.for_query()

            # Query building
            query = (
                builder.equals("status", "published")
                .equals("created_at", "2024-01-01")
                .sort_desc("updated_at")
                .page(2)
                .page_size(25)
            )

            # Response building
            response_result = builder.for_response().success(
                data={"items": list(range(25))}
            )
            response_data = response_result.value if response_result.success else None

            return query, response_data

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
                client_result.value
                if client_result.success
                else FlextApiClient(base_url="https://fallback.com")
            )

        result = benchmark(create_configured_client)
        assert result is not None
        assert result.base_url == "https://api.example.com"

    def test_multiple_queries_benchmark(
        self,
        benchmark: Callable[
            [Callable[[], list[FlextApiModels.HttpQuery]]],
            list[FlextApiModels.HttpQuery],
        ],
    ) -> None:
        """Benchmark multiple query operations."""

        def build_multiple_queries() -> list[FlextApiModels.HttpQuery]:
            queries = []

            for i in range(100):
                builder = FlextApiModels.for_query()
                query = (
                    builder.equals("id", str(i))
                    .equals("status", "active" if i % 2 == 0 else "inactive")
                    .equals("priority", "high" if i % 3 == 0 else "normal")
                )
                queries.append(query)
            return queries

        result = benchmark(build_multiple_queries)
        assert len(result) == 100
        assert all(q is not None for q in result)

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

            builder = FlextApiModels.for_query()
            response_result = builder.for_response().success(
                data=large_data, message="Large dataset retrieved"
            )
            return response_result.value if response_result.success else None

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

            for page in range(1, 11):  # 10 pages
                builder = FlextApiModels.for_query()
                response_result = builder.for_response().success(
                    data={"items": list(range((page - 1) * 20, page * 20))},
                    message=f"Page {page} of 10",
                )
                if response_result.success:
                    responses.append(response_result.value)
            return responses

        result = benchmark(build_paginated_responses)
        assert len(result) == 10
        assert all(isinstance(r, dict) for r in result)
