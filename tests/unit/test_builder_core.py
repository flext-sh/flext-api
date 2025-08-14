"""Test builder core functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api.builder import (
    FlextApiBuilder,
    FlextApiQuery,
    FlextApiQueryBuilder,
    FlextApiResponse,
    FlextApiResponseBuilder,
    PaginationConfig,
    build_error_response_object,
    build_paginated_response_object,
    build_query,
    build_success_response_object,
)

# Constants
EXPECTED_BULK_SIZE = 2


class TestFlextApiQuery:
    """Test FlextApiQuery dataclass."""

    def test_query_creation(self) -> None:
        """Test basic query creation."""
        query = FlextApiQuery()
        if query.page != 1:
            msg = f"Expected 1, got {query.page}"
            raise AssertionError(msg)
        assert query.page_size == 20
        assert isinstance(query.filters, list)
        assert isinstance(query.sorts, list)

    def test_query_with_custom_values(self) -> None:
        """Test query with custom values."""
        filters: list[dict[str, object]] = [
            {"field": "name", "operator": "equals", "value": "test"},
        ]
        sorts = [{"field": "created_at", "direction": "desc"}]

        query = FlextApiQuery(
            filters=filters,
            sorts=sorts,
            page=2,
            page_size=50,
        )

        if query.filters != filters:
            msg = f"Expected {filters}, got {query.filters}"
            raise AssertionError(msg)
        assert query.sorts == sorts
        if query.page != EXPECTED_BULK_SIZE:
            msg = f"Expected 2, got {query.page}"
            raise AssertionError(msg)
        assert query.page_size == 50

    def test_query_validation_negative_page(self) -> None:
        """Test query validation for negative page."""
        with pytest.raises(ValueError, match="Page must be greater than 0"):
            FlextApiQuery(page=0)

    def test_query_validation_negative_page_size(self) -> None:
        """Test query validation for negative page size."""
        with pytest.raises(ValueError, match="Page size must be greater than 0"):
            FlextApiQuery(page_size=0)

    def test_query_to_dict(self) -> None:
        """Test converting query to dictionary."""
        query = FlextApiQuery(page=2, page_size=10)
        result = query.to_dict()

        assert isinstance(result, dict)
        if result["page"] != EXPECTED_BULK_SIZE:
            msg = f"Expected 2, got {result['page']}"
            raise AssertionError(msg)
        assert result["page_size"] == 10
        if result["limit"] != 10:
            msg = f"Expected 10, got {result['limit']}"
            raise AssertionError(msg)
        assert result["offset"] == 10  # (page - 1) * page_size


class TestFlextApiResponse:
    """Test FlextApiResponse dataclass."""

    def test_response_creation(self) -> None:
        """Test basic response creation."""
        response = FlextApiResponse(success=True)
        if not response.success:
            msg = f"Expected True, got {response.success}"
            raise AssertionError(msg)
        if response.message != "":
            msg = f"Expected empty string, got {response.message}"
            raise AssertionError(msg)
        assert isinstance(response.metadata, dict)
        assert response.timestamp != ""

    def test_response_with_data(self) -> None:
        """Test response with data."""
        data = {"key": "value"}
        response = FlextApiResponse(success=True, data=data, message="Success")

        if not response.success:
            msg = f"Expected True, got {response.success}"
            raise AssertionError(msg)
        if response.data != data:
            msg = f"Expected {data}, got {response.data}"
            raise AssertionError(msg)
        assert response.message == "Success"

    def test_response_to_dict(self) -> None:
        """Test converting response to dictionary."""
        data = {"key": "value"}
        response = FlextApiResponse(success=True, data=data, message="Success")
        result = response.to_dict()

        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["data"] == data
        assert result["message"] == "Success"
        assert "timestamp" in result
        assert "metadata" in result


class TestFlextApiQueryBuilder:
    """Test FlextApiQueryBuilder."""

    def test_query_builder_creation(self) -> None:
        """Test query builder creation."""
        builder = FlextApiQueryBuilder()
        assert isinstance(builder, FlextApiQueryBuilder)

    def test_equals_filter(self) -> None:
        """Test equals filter."""
        builder = FlextApiQueryBuilder()
        query = builder.equals("name", "test").build()

        assert len(query.filters) == 1
        filter_obj = query.filters[0]
        assert filter_obj["field"] == "name"
        assert filter_obj["operator"] == "equals"
        assert filter_obj["value"] == "test"

    def test_greater_than_filter(self) -> None:
        """Test greater than filter."""
        builder = FlextApiQueryBuilder()
        query = builder.greater_than("age", 18).build()

        assert len(query.filters) == 1
        filter_obj = query.filters[0]
        assert filter_obj["field"] == "age"
        assert filter_obj["operator"] == "gt"
        assert filter_obj["value"] == 18

    def test_sort_desc(self) -> None:
        """Test descending sort."""
        builder = FlextApiQueryBuilder()
        query = builder.sort_desc("created_at").build()

        assert len(query.sorts) == 1
        sort_obj = query.sorts[0]
        assert sort_obj["field"] == "created_at"
        assert sort_obj["direction"] == "desc"

    def test_sort_asc(self) -> None:
        """Test ascending sort."""
        builder = FlextApiQueryBuilder()
        query = builder.sort_asc("name").build()

        assert len(query.sorts) == 1
        sort_obj = query.sorts[0]
        assert sort_obj["field"] == "name"
        assert sort_obj["direction"] == "asc"

    def test_pagination(self) -> None:
        """Test pagination."""
        builder = FlextApiQueryBuilder()
        query = builder.page(2).page_size(50).build()

        assert query.page == 2
        assert query.page_size == 50

    def test_pagination_validation(self) -> None:
        """Test pagination validation."""
        builder = FlextApiQueryBuilder()

        with pytest.raises(ValueError, match="Page must be greater than 0"):
            builder.page(0)

        with pytest.raises(ValueError, match="Page size must be greater than 0"):
            builder.page_size(0)

        # Test combined pagination method
        with pytest.raises(ValueError, match="Page must be greater than 0"):
            builder.pagination(page=0, size=10)

        with pytest.raises(ValueError, match="Page size must be greater than 0"):
            builder.pagination(page=1, size=0)

        # Test successful pagination
        query = builder.pagination(page=2, size=25).build()
        assert query.page == 2
        assert query.page_size == 25

    def test_empty_field_validation(self) -> None:
        """Test empty field validation."""
        builder = FlextApiQueryBuilder()

        with pytest.raises(ValueError, match="Field cannot be empty"):
            builder.equals("", "value")

        with pytest.raises(ValueError, match="Field cannot be empty"):
            builder.sort_asc("")

        with pytest.raises(ValueError, match="Field cannot be empty"):
            builder.greater_than("", 5)

        with pytest.raises(ValueError, match="Field cannot be empty"):
            builder.sort_desc("")

        with pytest.raises(ValueError, match="Field cannot be empty"):
            builder.greater_than("   ", 5)  # whitespace only

    def test_chained_operations(self) -> None:
        """Test chained operations."""
        builder = FlextApiQueryBuilder()
        query = (
            builder.equals("status", "active")
            .greater_than("age", 18)
            .sort_desc("created_at")
            .page(2)
            .page_size(25)
            .build()
        )

        assert len(query.filters) == 2
        assert len(query.sorts) == 1
        assert query.page == 2
        assert query.page_size == 25


class TestFlextApiResponseBuilder:
    """Test FlextApiResponseBuilder."""

    def test_response_builder_creation(self) -> None:
        """Test response builder creation."""
        builder = FlextApiResponseBuilder()
        assert isinstance(builder, FlextApiResponseBuilder)

    def test_success_response(self) -> None:
        """Test success response."""
        data = {"key": "value"}
        response = FlextApiResponseBuilder().success(data, "Success").build()

        assert response.success is True
        assert response.data == data
        assert response.message == "Success"

    def test_error_response(self) -> None:
        """Test error response."""
        response = FlextApiResponseBuilder().error("Error occurred").build()

        assert response.success is False
        assert response.message == "Error occurred"
        assert response.data is None

    def test_with_metadata(self) -> None:
        """Test response with metadata."""
        metadata: dict[str, object] = {"total": 100, "page": 1}
        response = FlextApiResponseBuilder().metadata(metadata).build()

        assert response.metadata == metadata

    def test_with_pagination(self) -> None:
        """Test response with pagination."""
        data = [{"id": 1}, {"id": 2}]
        response = (
            FlextApiResponseBuilder()
            .success(data, "Success")
            .pagination(page=2, page_size=10, total=100)
            .build()
        )

        assert response.success is True
        assert response.data == data
        assert response.metadata["page"] == 2
        assert response.metadata["page_size"] == 10
        assert response.metadata["total"] == 100

        # Test to_dict() with pagination
        response_dict = response.to_dict()
        assert "pagination" in response_dict
        assert response_dict["pagination"] == response.pagination

    def test_pagination_validation(self) -> None:
        """Test pagination validation."""
        builder = FlextApiResponseBuilder()

        with pytest.raises(ValueError, match="Page must be greater than 0"):
            builder.pagination(page=0, page_size=10, total=100)

        with pytest.raises(ValueError, match="Total must be positive"):
            builder.pagination(page=1, page_size=10, total=-1)

        with pytest.raises(ValueError, match="Page size must be greater than 0"):
            builder.pagination(page=1, page_size=0, total=100)


class TestFactoryFunctions:
    """Test factory functions."""

    def test_build_query(self) -> None:
        """Test build_query function."""
        query = build_query(
            filters=[{"field": "name", "operator": "equals", "value": "test"}],
        )

        assert isinstance(query, FlextApiQuery)
        assert len(query.filters) == 1

    def test_build_query_empty(self) -> None:
        """Test build_query with empty parameters."""
        query = build_query()

        assert isinstance(query, FlextApiQuery)
        assert query.page == 1
        assert query.page_size == 20

    def test_build_success_response(self) -> None:
        """Test build_success_response function."""
        data = {"key": "value"}
        response = build_success_response_object(data, "Success")

        assert isinstance(response, FlextApiResponse)
        assert response.success is True
        assert response.data == data
        assert response.message == "Success"

    def test_build_error_response(self) -> None:
        """Test build_error_response function."""
        response = build_error_response_object("Error occurred")

        assert isinstance(response, FlextApiResponse)
        assert response.success is False
        assert response.message == "Error occurred"

    def test_build_paginated_response(self) -> None:
        """Test build_paginated_response function."""
        data = [{"id": 1}, {"id": 2}]
        config = PaginationConfig(
            data=data,
            total=100,
            page=2,
            page_size=10,
            message="Success",
            metadata={},
        )
        response = build_paginated_response_object(config)

        assert isinstance(response, FlextApiResponse)
        assert response.success is True
        assert response.data == data
        assert response.metadata["page"] == 2
        assert response.metadata["page_size"] == 10
        assert response.metadata["total"] == 100


class TestFlextApiBuilder:
    """Test FlextApiBuilder."""

    def test_builder_creation(self) -> None:
        """Test builder creation."""
        builder = FlextApiBuilder()
        assert isinstance(builder, FlextApiBuilder)

    def test_for_query(self) -> None:
        """Test for_query method."""
        query_builder = FlextApiBuilder().for_query()
        assert isinstance(query_builder, FlextApiQueryBuilder)

    def test_for_response(self) -> None:
        """Test for_response method."""
        response_builder = FlextApiBuilder().for_response()
        assert isinstance(response_builder, FlextApiResponseBuilder)
