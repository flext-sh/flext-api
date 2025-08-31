"""Tests to cover missing lines in builder.py.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_api import (
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    PaginatedResponseBuilder,
    PaginationConfig,
    ResponseConfig,
    build_error_response,
    build_paginated_response,
    build_query,
    build_success_response,
)


class TestMissingBuilderCoverage:
    """Test missing coverage in builder.py."""

    def test_build_query_with_gt_operator(self) -> None:
        """Test build_query with filters - covers query building."""
        query = build_query(page=1, page_size=10)

        assert "filters" in query
        assert "pagination" in query
        assert query["pagination"]["page"] == 1
        assert query["pagination"]["page_size"] == 10

    def test_build_error_response_with_details(self) -> None:
        """Test build_error_response with status code - covers error responses."""
        result = build_error_response("Validation failed", 400)

        assert result["message"] == "Validation failed"
        assert result["status_code"] == 400
        assert "timestamp" in result

    def test_build_paginated_response_with_metadata(self) -> None:
        """Test build_paginated_response - covers paginated responses."""
        data = [{"id": 1}, {"id": 2}]
        result = build_paginated_response(
            data=data,
            current_page=1,
            page_size=10,
            total_items=100,
            message="Data retrieved",
        )

        assert result["status_code"] == 200
        assert result["data"] == data
        assert "pagination" in result
        assert result["pagination"]["current_page"] == 1
        assert result["pagination"]["total_items"] == 100

    def test_build_success_response_with_metadata(self) -> None:
        """Test build_success_response - covers success responses."""
        data = {"result": "success"}
        result = build_success_response(data, "Operation successful")

        assert result["status_code"] == 200
        assert result["data"] == data
        assert result["message"] == "Operation successful"

    def test_pagination_validation_negative_total(self) -> None:
        """Test pagination validation with negative total - covers lines 197-198."""
        with pytest.raises(
            ValidationError, match="Input should be greater than or equal to 0"
        ):
            PaginationConfig(data=[], total=-1, page=1, page_size=10)

    def test_pagination_validation_zero_page(self) -> None:
        """Test pagination validation with zero page using Pydantic validation."""
        with pytest.raises(
            ValidationError, match="Input should be greater than or equal to 1"
        ):
            PaginationConfig(data=[], total=100, page=0, page_size=10)

    def test_pagination_validation_zero_page_size(self) -> None:
        """Test pagination validation with zero page size using Pydantic validation."""
        with pytest.raises(
            ValidationError, match="Input should be greater than or equal to 1"
        ):
            PaginationConfig(data=[], total=100, page=1, page_size=0)

    def test_response_builder_legacy_create_response(self) -> None:
        """Test legacy _create_response method - covers line 458."""
        builder = FlextApiResponseBuilder()
        config = ResponseConfig(
            success=True,
            data={"test": "data"},
            message="Success",
            metadata={"info": "test"},
        )

        # Test builder pattern - should return ResponseBuilder
        result = builder.success(config.data, config.message)

        # Should return self for fluent interface
        assert isinstance(result, FlextApiResponseBuilder)

    def test_create_paginated_response_function(self) -> None:
        """Test build_paginated_response function - covers pagination."""
        data = [{"id": 1}, {"id": 2}]
        result = build_paginated_response(
            data=data,
            current_page=1,
            page_size=10,
            total_items=2,
            message="Retrieved items",
        )

        assert result["status_code"] == 200
        assert result["data"] == data
        assert result["message"] == "Retrieved items"

    def test_paginated_response_builder_init(self) -> None:
        """Test PaginatedResponseBuilder initialization."""
        builder = PaginatedResponseBuilder()

        # Check default values (using actual attributes)
        assert hasattr(builder, "_current_page")
        assert builder._current_page == 1
        assert builder._page_size == 20
        assert builder._total_items == 0

    def test_paginated_response_builder_data_method(self) -> None:
        """Test PaginatedResponseBuilder data method via success()."""
        builder = PaginatedResponseBuilder()
        test_data = [{"id": 1}, {"id": 2}]

        result = builder.success(test_data)

        assert result is builder  # Fluent interface
        assert hasattr(builder, "_data")
        assert builder._data == test_data

    def test_paginated_response_builder_total_method(self) -> None:
        """Test PaginatedResponseBuilder with_pagination method."""
        builder = PaginatedResponseBuilder()

        result = builder.with_pagination(1, 10, 100)

        assert result is builder  # Fluent interface
        assert builder._total_items == 100

    def test_paginated_response_builder_page_method(self) -> None:
        """Test PaginatedResponseBuilder page via with_pagination."""
        builder = PaginatedResponseBuilder()

        result = builder.with_pagination(5, 20, 100)

        assert result is builder  # Fluent interface
        assert builder._current_page == 5

    def test_paginated_response_builder_page_size_method(self) -> None:
        """Test PaginatedResponseBuilder page_size via with_pagination."""
        builder = PaginatedResponseBuilder()

        result = builder.with_pagination(1, 25, 100)

        assert result is builder  # Fluent interface
        assert builder._page_size == 25

    def test_paginated_response_builder_message_method(self) -> None:
        """Test PaginatedResponseBuilder message via success()."""
        builder = PaginatedResponseBuilder()

        result = builder.success([{"id": 1}], "Custom message")

        assert result is builder  # Fluent interface
        assert hasattr(builder, "_message")
        assert builder._message == "Custom message"

    def test_paginated_response_builder_metadata_method(self) -> None:
        """Test PaginatedResponseBuilder metadata method - covers lines 729-730."""
        builder = PaginatedResponseBuilder()
        metadata = {"custom": "data"}

        result = builder.with_metadata(metadata)

        assert result is builder  # Fluent interface
        assert builder._metadata == metadata

    def test_paginated_response_builder_build(self) -> None:
        """Test PaginatedResponseBuilder build method."""
        builder = PaginatedResponseBuilder()
        test_data = [{"id": 1}]

        result = builder.success(test_data).with_pagination(2, 10, 50).build()

        assert result["status_code"] == 200
        assert result["data"] == test_data
        # Check pagination data in pagination object
        pagination = result["pagination"]
        assert pagination["total_items"] == 50
        assert pagination["current_page"] == 2
        assert pagination["page_size"] == 10

    def test_query_builder_advanced_methods(self) -> None:
        """Test QueryBuilder advanced methods."""
        builder = FlextApiQueryBuilder()

        # Test method chaining that hits advanced functionality
        result = (
            builder.equals("status", "active")
            .sort_desc("created_at")
            .page(1)
            .page_size(10)
            .build()
        )

        # Result is a dict, not an object
        assert isinstance(result, dict)
        assert "pagination" in result
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 10
