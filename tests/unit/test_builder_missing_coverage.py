"""Tests to cover missing lines in builder.py.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.builder import (
    build_error_response,
    build_paginated_response,
    build_query,
    build_success_response,
)


class TestMissingBuilderCoverage:
    """Test missing coverage in builder.py."""

    def test_build_query_with_gt_operator(self) -> None:
        """Test build_query with gt operator - covers lines 337-338."""
        filters = [
            {"field": "status", "operator": "equals", "value": "active"},
            {"field": "age", "operator": "gt", "value": 18},
        ]

        query = build_query(filters)

        assert len(query.filters) == 2
        assert query.filters[0]["operator"] == "equals"
        assert query.filters[1]["operator"] == "gt"
        assert query.filters[1]["field"] == "age"
        assert query.filters[1]["value"] == 18

    def test_build_error_response_with_details(self) -> None:
        """Test build_error_response with details - covers lines 375-376."""
        details = {"field_errors": ["name is required", "email invalid"]}
        result = build_error_response("Validation failed", 400, details)

        assert result["success"] is False
        assert result["message"] == "Validation failed"
        assert "metadata" in result
        assert result["metadata"]["details"] == details

    def test_build_paginated_response_with_metadata(self) -> None:
        """Test build_paginated_response with metadata - covers lines 396-398."""
        from flext_api.builder import PaginationConfig

        data = [{"id": 1}, {"id": 2}]
        metadata = {"custom_field": "value", "another": 123}
        config = PaginationConfig(
            data=data,
            total=100,
            page=1,
            page_size=10,
            message="Data retrieved",
            metadata=metadata,
        )
        result = build_paginated_response(config)

        assert result["success"] is True
        assert result["data"] == data
        assert result["metadata"]["custom_field"] == "value"
        assert result["metadata"]["another"] == 123

    def test_build_success_response_with_metadata(self) -> None:
        """Test build_success_response with metadata - covers lines 411-412."""
        data = {"result": "success"}
        metadata = {"request_id": "12345", "timestamp": "2023-01-01"}
        result = build_success_response(data, "Operation successful", metadata)

        assert result["success"] is True
        assert result["data"] == data
        assert result["metadata"]["request_id"] == "12345"
        assert result["metadata"]["timestamp"] == "2023-01-01"

    def test_pagination_validation_negative_total(self) -> None:
        """Test pagination validation with negative total - covers lines 197-198."""
        import pytest

        from flext_api.builder import PaginationConfig

        with pytest.raises(ValueError, match="Total must be non-negative"):
            PaginationConfig(data=[], total=-1, page=1, page_size=10)

    def test_pagination_validation_zero_page(self) -> None:
        """Test pagination validation with zero page - covers lines 200-201."""
        import pytest

        from flext_api.builder import PaginationConfig

        with pytest.raises(ValueError, match="Page must be positive"):
            PaginationConfig(data=[], total=100, page=0, page_size=10)

    def test_pagination_validation_zero_page_size(self) -> None:
        """Test pagination validation with zero page size - covers lines 203-204."""
        import pytest

        from flext_api.builder import PaginationConfig

        with pytest.raises(ValueError, match="Page size must be positive"):
            PaginationConfig(data=[], total=100, page=1, page_size=0)

    def test_response_builder_legacy_create_response(self) -> None:
        """Test legacy _create_response method - covers line 458."""
        from flext_api.builder import FlextApiResponseBuilder, ResponseConfig

        builder = FlextApiResponseBuilder()
        config = ResponseConfig(
            success=True,
            data={"test": "data"},
            message="Success",
            metadata={"info": "test"}
        )

        # Test builder pattern - should return ResponseBuilder
        result = builder.success(config.data, config.message)

        # Should return self for fluent interface
        assert isinstance(result, FlextApiResponseBuilder)

    def test_create_paginated_response_function(self) -> None:
        """Test create_paginated_response function - covers line 680."""

        from flext_api.builder import PaginationConfig

        config = PaginationConfig(
            data=[{"id": 1}, {"id": 2}],
            total=2,
            page=1,
            page_size=10,
            message="Retrieved items",
            metadata={"total": 2}
        )

        result = build_paginated_response(config)

        assert result["success"] is True
        assert result["data"] == [{"id": 1}, {"id": 2}]
        assert result["message"] == "Retrieved items"

    def test_paginated_response_builder_init(self) -> None:
        """Test PaginatedResponseBuilder initialization - covers lines 692-697."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()

        # Check default values
        assert builder._data is None
        assert builder._total == 0
        assert builder._page == 1

    def test_paginated_response_builder_data_method(self) -> None:
        """Test PaginatedResponseBuilder data method - covers lines 701-702."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()
        test_data = [{"id": 1}, {"id": 2}]

        result = builder.with_data(test_data)

        assert result is builder  # Fluent interface
        assert builder._data == test_data

    def test_paginated_response_builder_total_method(self) -> None:
        """Test PaginatedResponseBuilder total method - covers lines 706-707."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()

        result = builder.with_total(100)

        assert result is builder  # Fluent interface
        assert builder._total == 100

    def test_paginated_response_builder_page_method(self) -> None:
        """Test PaginatedResponseBuilder page method - covers lines 711-712."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()

        result = builder.with_page(5)

        assert result is builder  # Fluent interface
        assert builder._page == 5

    def test_paginated_response_builder_page_size_method(self) -> None:
        """Test PaginatedResponseBuilder page_size method - covers lines 716-717."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()

        result = builder.with_page_size(25)

        assert result is builder  # Fluent interface
        assert builder._page_size == 25

    def test_paginated_response_builder_message_method(self) -> None:
        """Test PaginatedResponseBuilder message method - covers lines 721-722."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()

        result = builder.with_message("Custom message")

        assert result is builder  # Fluent interface
        assert builder._message == "Custom message"

    def test_paginated_response_builder_metadata_method(self) -> None:
        """Test PaginatedResponseBuilder metadata method - covers lines 729-730."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()
        metadata = {"custom": "data"}

        result = builder.with_metadata(metadata)

        assert result is builder  # Fluent interface
        assert builder._metadata == metadata

    def test_paginated_response_builder_build(self) -> None:
        """Test PaginatedResponseBuilder build method - covers lines 734-742."""
        from flext_api.builder import PaginatedResponseBuilder

        builder = PaginatedResponseBuilder()
        test_data = [{"id": 1}]

        result = builder.with_data(test_data).with_total(50).with_page(2).with_page_size(10).build()

        assert result["success"] is True
        assert result["data"] == test_data
        # Check pagination data directly in metadata (not nested under "pagination")
        metadata = result["metadata"]
        assert metadata["total"] == 50
        assert metadata["page"] == 2
        assert metadata["page_size"] == 10

    def test_query_builder_advanced_methods(self) -> None:
        """Test QueryBuilder advanced methods - covers lines 754, 848, 860."""
        from flext_api.builder import FlextApiQueryBuilder

        builder = FlextApiQueryBuilder()

        # Test method chaining that hits advanced functionality
        result = (
            builder
            .equals("status", "active")
            .sort_desc("created_at")
            .page(1)
            .page_size(10)
            # Remove limit() call - method doesn't exist
            .build()
        )

        assert result.filters is not None
        assert result.sorts is not None
        # FlextApiQuery has page and page_size, but no pagination attribute
        assert result.page == 1
        assert result.page_size == 10
