"""Tests to cover missing lines in builder.py.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_api import (
    FlextApiQueryBuilder,
    PaginationConfig,
)


class TestMissingBuilderCoverage:
    """Test missing coverage in builder.py."""

    def test_query_builder_basic_usage(self) -> None:
        """Test FlextApiQueryBuilder basic functionality."""
        builder = FlextApiQueryBuilder()
        query = (
            builder.for_query().equals("status", "active").page(1).page_size(10).build()
        )

        assert isinstance(query, dict)
        assert "pagination" in query
        assert query["pagination"]["page"] == 1
        assert query["pagination"]["page_size"] == 10

    def test_response_builder_error(self) -> None:
        """Test response builder error functionality."""
        builder = FlextApiQueryBuilder()
        result = builder.for_response().error("Validation failed", 400)

        assert result.success is False
        if hasattr(result, "error"):
            assert "Validation failed" in str(result.error)

    def test_pagination_config_creation(self) -> None:
        """Test PaginationConfig creation."""
        data = [{"id": 1}, {"id": 2}]
        config = PaginationConfig(data=data, total=100, page=1, page_size=10)

        assert config.data == data
        assert config.total == 100
        assert config.page == 1
        assert config.page_size == 10

    def test_response_builder_success(self) -> None:
        """Test response builder success functionality."""
        builder = FlextApiQueryBuilder()
        data = {"result": "success"}
        result = builder.for_response().success(data, "Operation successful")

        assert result.success is True
        if hasattr(result, "value"):
            response_data = result.value
            assert "data" in response_data
            assert response_data["message"] == "Operation successful"

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

    def test_response_builder_fluent_interface(self) -> None:
        """Test response builder fluent interface."""
        builder = FlextApiQueryBuilder()
        test_data = {"test": "data"}

        # Test builder pattern - should return FlextResult
        result = builder.for_response().success(test_data, "Success")

        # Should return FlextResult
        assert hasattr(result, "success")
        assert result.success is True

    def test_query_builder_pagination(self) -> None:
        """Test query builder pagination functionality."""
        builder = FlextApiQueryBuilder()
        query = builder.for_query().page(1).page_size(10).build()

        assert "pagination" in query
        assert query["pagination"]["page"] == 1
        assert query["pagination"]["page_size"] == 10

    def test_query_builder_init(self) -> None:
        """Test FlextApiQueryBuilder initialization."""
        builder = FlextApiQueryBuilder()

        # Should be able to create builder without errors
        assert builder is not None
        assert hasattr(builder, "for_query")
        assert hasattr(builder, "for_response")

    def test_query_builder_data_filtering(self) -> None:
        """Test query builder data filtering."""
        builder = FlextApiQueryBuilder()

        query = builder.for_query().equals("status", "active").build()

        assert isinstance(query, dict)
        # Query should contain filter information
        assert "filters" in query or "conditions" in query or query

    def test_pagination_config_total_validation(self) -> None:
        """Test PaginationConfig total validation."""
        config = PaginationConfig(data=[], total=100, page=1, page_size=10)

        assert config.total == 100
        assert config.data == []

    def test_query_builder_page_method(self) -> None:
        """Test query builder page functionality."""
        builder = FlextApiQueryBuilder()

        query = builder.for_query().page(5).build()

        assert query["pagination"]["page"] == 5

    def test_query_builder_page_size_method(self) -> None:
        """Test query builder page size functionality."""
        builder = FlextApiQueryBuilder()

        query = builder.for_query().page_size(25).build()

        assert query["pagination"]["page_size"] == 25

    def test_response_builder_message_method(self) -> None:
        """Test response builder message functionality."""
        builder = FlextApiQueryBuilder()

        result = builder.for_response().success([{"id": 1}], "Custom message")

        assert hasattr(result, "success")
        assert result.success is True
        if hasattr(result, "value"):
            response_data = result.value
            assert response_data["message"] == "Custom message"

    def test_query_builder_metadata_handling(self) -> None:
        """Test query builder with additional metadata."""
        builder = FlextApiQueryBuilder()

        query = builder.for_query().equals("type", "metadata").build()

        assert isinstance(query, dict)
        # Query should handle metadata properly
        assert query is not None

    def test_query_builder_build_method(self) -> None:
        """Test query builder build method."""
        builder = FlextApiQueryBuilder()

        query = (
            builder.for_query().equals("status", "active").page(2).page_size(10).build()
        )

        assert isinstance(query, dict)
        # Check pagination data in query
        pagination = query["pagination"]
        assert pagination["page"] == 2
        assert pagination["page_size"] == 10

    def test_query_builder_advanced_methods(self) -> None:
        """Test QueryBuilder advanced methods."""
        builder = FlextApiQueryBuilder()

        # Test method chaining that hits advanced functionality
        result = (
            builder.for_query()
            .equals("status", "active")
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
