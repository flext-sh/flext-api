"""Tests for FlextApiQueryBuilder core functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""


from flext_api.core.query import (
    FlextApiQueryBuilder,
    FlextApiQueryOperator,
)


class TestFlextApiQueryOperator:
    """Test query operators enum."""

    def test_operator_values(self):
        """Test operator enum values."""
        assert FlextApiQueryOperator.EQUALS.value == "eq"
        assert FlextApiQueryOperator.NOT_EQUALS.value == "ne"
        assert FlextApiQueryOperator.GREATER_THAN.value == "gt"
        assert FlextApiQueryOperator.LESS_THAN.value == "lt"
        assert FlextApiQueryOperator.LIKE.value == "like"
        assert FlextApiQueryOperator.IN.value == "in"
        assert FlextApiQueryOperator.BETWEEN.value == "between"
        assert FlextApiQueryOperator.IS_NULL.value == "is_null"
        assert FlextApiQueryOperator.IS_NOT_NULL.value == "is_not_null"


class TestFlextApiQueryBuilder:
    """Test query builder functionality."""

    def test_initialization(self):
        """Test query builder initialization."""
        qb = FlextApiQueryBuilder()

        assert qb._filters == []
        assert qb._sorts == []
        assert qb._limit is None
        assert qb._offset is None
        assert qb._page is None
        assert qb._page_size is None

    def test_basic_filter(self):
        """Test basic filter functionality."""
        qb = FlextApiQueryBuilder()
        result = qb.filter("name", FlextApiQueryOperator.EQUALS, "John").build()

        expected = {
            "filters": [{"field": "name", "operator": "eq", "value": "John"}],
            "sorts": [],
        }

        assert result == expected

    def test_filter_with_string_operator(self):
        """Test filter with string operator."""
        qb = FlextApiQueryBuilder()
        result = qb.filter("age", "gte", 18).build()

        expected = {
            "filters": [{"field": "age", "operator": "gte", "value": 18}],
            "sorts": [],
        }

        assert result == expected

    def test_filter_without_value(self):
        """Test filter without value (for IS_NULL, etc)."""
        qb = FlextApiQueryBuilder()
        result = qb.filter("deleted_at", FlextApiQueryOperator.IS_NULL).build()

        expected = {
            "filters": [{"field": "deleted_at", "operator": "is_null"}],
            "sorts": [],
        }

        assert result == expected

    def test_multiple_filters(self):
        """Test multiple filters."""
        qb = FlextApiQueryBuilder()
        result = (
            qb.filter("name", FlextApiQueryOperator.EQUALS, "John")
            .filter("age", FlextApiQueryOperator.GREATER_THAN, 18)
            .filter("active", "eq", True)
            .build()
        )

        assert len(result["filters"]) == 3
        assert result["filters"][0]["field"] == "name"
        assert result["filters"][1]["field"] == "age"
        assert result["filters"][2]["field"] == "active"

    def test_basic_sort(self):
        """Test basic sort functionality."""
        qb = FlextApiQueryBuilder()
        result = qb.sort("created_at", "desc").build()

        expected = {
            "filters": [],
            "sorts": [{"field": "created_at", "direction": "desc"}],
        }

        assert result == expected

    def test_default_sort_direction(self):
        """Test default sort direction."""
        qb = FlextApiQueryBuilder()
        result = qb.sort("name").build()

        expected = {
            "filters": [],
            "sorts": [{"field": "name", "direction": "asc"}],
        }

        assert result == expected

    def test_multiple_sorts(self):
        """Test multiple sorts."""
        qb = FlextApiQueryBuilder()
        result = (
            qb.sort("priority", "desc")
            .sort("created_at", "asc")
            .build()
        )

        assert len(result["sorts"]) == 2
        assert result["sorts"][0]["field"] == "priority"
        assert result["sorts"][1]["field"] == "created_at"

    def test_limit_and_offset(self):
        """Test limit and offset."""
        qb = FlextApiQueryBuilder()
        result = qb.limit(10).offset(20).build()

        assert result["limit"] == 10
        assert result["offset"] == 20

    def test_pagination(self):
        """Test pagination."""
        qb = FlextApiQueryBuilder()
        result = qb.page(2, 25).build()

        assert result["page"] == 2
        assert result["page_size"] == 25

    def test_pagination_with_default_size(self):
        """Test pagination with default page size."""
        qb = FlextApiQueryBuilder()
        result = qb.page(1).build()

        assert result["page"] == 1
        assert result["page_size"] == 20

    def test_convenience_methods(self):
        """Test convenience methods."""
        qb = FlextApiQueryBuilder()
        result = (
            qb.equals("name", "John")
            .like("email", "%@example.com")
            .greater_than("age", 18)
            .between("score", 80, 100)
            .is_null("deleted_at")
            .is_not_null("confirmed_at")
            .build()
        )

        filters = result["filters"]
        assert len(filters) == 6

        # Check each filter
        assert filters[0] == {"field": "name", "operator": "eq", "value": "John"}
        assert filters[1] == {"field": "email", "operator": "like", "value": "%@example.com"}
        assert filters[2] == {"field": "age", "operator": "gt", "value": 18}
        assert filters[3] == {"field": "score", "operator": "between", "value": [80, 100]}
        assert filters[4] == {"field": "deleted_at", "operator": "is_null"}
        assert filters[5] == {"field": "confirmed_at", "operator": "is_not_null"}

    def test_convenience_sort_methods(self):
        """Test convenience sort methods."""
        qb = FlextApiQueryBuilder()
        result = (
            qb.sort_asc("name")
            .sort_desc("created_at")
            .build()
        )

        sorts = result["sorts"]
        assert len(sorts) == 2
        assert sorts[0] == {"field": "name", "direction": "asc"}
        assert sorts[1] == {"field": "created_at", "direction": "desc"}

    def test_complex_query(self):
        """Test complex query with all features."""
        qb = FlextApiQueryBuilder()
        result = (
            qb.equals("status", "active")
            .like("name", "John%")
            .greater_than("age", 18)
            .is_not_null("email")
            .sort_desc("priority")
            .sort_asc("name")
            .page(2, 50)
            .build()
        )

        # Verify structure
        assert len(result["filters"]) == 4
        assert len(result["sorts"]) == 2
        assert result["page"] == 2
        assert result["page_size"] == 50

        # Verify filter content
        filters = result["filters"]
        assert filters[0]["field"] == "status"
        assert filters[1]["field"] == "name"
        assert filters[2]["field"] == "age"
        assert filters[3]["field"] == "email"

    def test_reset_functionality(self):
        """Test reset functionality."""
        qb = FlextApiQueryBuilder()

        # Build complex query
        qb.equals("name", "John").sort("created_at").limit(10).page(2)
        complex_result = qb.build()

        # Verify it has content
        assert len(complex_result["filters"]) > 0
        assert len(complex_result["sorts"]) > 0
        assert "limit" in complex_result
        assert "page" in complex_result

        # Reset and build empty query
        empty_result = qb.reset().build()

        # Verify reset worked
        assert empty_result["filters"] == []
        assert empty_result["sorts"] == []
        assert "limit" not in empty_result
        assert "offset" not in empty_result
        assert "page" not in empty_result
        assert "page_size" not in empty_result

    def test_fluent_interface(self):
        """Test fluent interface returns self."""
        qb = FlextApiQueryBuilder()

        # All methods should return self for chaining
        assert qb.filter("name", "eq", "John") is qb
        assert qb.sort("created_at") is qb
        assert qb.limit(10) is qb
        assert qb.offset(5) is qb
        assert qb.page(1) is qb

        # Convenience methods too
        assert qb.equals("id", 1) is qb
        assert qb.like("email", "%test%") is qb
        assert qb.sort_asc("name") is qb
        assert qb.reset() is qb

    def test_empty_build(self):
        """Test building empty query."""
        qb = FlextApiQueryBuilder()
        result = qb.build()

        expected = {
            "filters": [],
            "sorts": [],
        }

        assert result == expected

    def test_only_optional_fields_included(self):
        """Test that optional fields are only included when set."""
        qb = FlextApiQueryBuilder()

        # Only set limit
        result = qb.limit(5).build()
        assert "limit" in result
        assert "offset" not in result
        assert "page" not in result
        assert "page_size" not in result

        # Reset and only set offset
        result = qb.reset().offset(10).build()
        assert "offset" in result
        assert "limit" not in result
        assert "page" not in result
        assert "page_size" not in result

    def test_reusable_builder(self):
        """Test that builder can be reused."""
        qb = FlextApiQueryBuilder()

        # Build first query
        result1 = qb.equals("type", "user").build()
        assert len(result1["filters"]) == 1

        # Add more conditions and build again
        result2 = qb.equals("active", True).build()
        assert len(result2["filters"]) == 2

        # Reset and build new query
        result3 = qb.reset().like("name", "test%").build()
        assert len(result3["filters"]) == 1
        assert result3["filters"][0]["field"] == "name"
