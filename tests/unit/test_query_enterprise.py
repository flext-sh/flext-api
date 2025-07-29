"""ENTERPRISE UNIT TESTS - FlextApiQueryBuilder.

Tests every operator, method, and edge case of FlextApiQueryBuilder.
Validates complex queries, chaining, pagination, sorting, and real-world scenarios.
NO MOCKS - only real functionality validation.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from flext_api.query import FlextApiQueryBuilder, FlextApiQueryOperator


class TestFlextApiQueryBuilderBasic:
    """Basic query builder functionality tests."""

    def test_query_builder_initialization(self):
        """Test query builder initialization."""
        qb = FlextApiQueryBuilder()
        
        assert qb._filters == []
        assert qb._sorts == []
        assert qb._page is None
        assert qb._page_size is None
        assert qb._limit is None

    def test_query_operators_enum(self):
        """Test all query operators are available."""
        operators = [
            FlextApiQueryOperator.EQUALS,
            FlextApiQueryOperator.NOT_EQUALS,
            FlextApiQueryOperator.GREATER_THAN,
            FlextApiQueryOperator.GREATER_THAN_OR_EQUAL,
            FlextApiQueryOperator.LESS_THAN,
            FlextApiQueryOperator.LESS_THAN_OR_EQUAL,
            FlextApiQueryOperator.LIKE,
            FlextApiQueryOperator.ILIKE,
            FlextApiQueryOperator.IN,
            FlextApiQueryOperator.NOT_IN,
            FlextApiQueryOperator.BETWEEN,
            FlextApiQueryOperator.IS_NULL,
            FlextApiQueryOperator.IS_NOT_NULL,
        ]
        
        assert len(operators) == 13
        
        # Verify enum values
        assert FlextApiQueryOperator.EQUALS.value == "eq"
        assert FlextApiQueryOperator.GREATER_THAN.value == "gt"
        assert FlextApiQueryOperator.LIKE.value == "like"
        assert FlextApiQueryOperator.IN.value == "in"


class TestFlextApiQueryBuilderFilters:
    """Filter functionality tests."""

    def test_equals_filter(self):
        """Test equals filter."""
        qb = FlextApiQueryBuilder()
        result = qb.equals("status", "active").build()
        
        expected = {
            "filters": [{"field": "status", "operator": "eq", "value": "active"}],
            "sorts": [],
            "page": None,
            "page_size": None,
            "limit": None,
        }
        
        assert result == expected

    def test_not_equals_filter(self):
        """Test not equals filter."""
        qb = FlextApiQueryBuilder()
        result = qb.not_equals("status", "inactive").build()
        
        assert result["filters"][0]["operator"] == "ne"
        assert result["filters"][0]["value"] == "inactive"

    def test_comparison_filters(self):
        """Test all comparison filters."""
        qb = FlextApiQueryBuilder()
        
        qb.greater_than("age", 18)
        qb.greater_than_or_equal("score", 80)
        qb.less_than("price", 100.50)
        qb.less_than_or_equal("discount", 25)
        
        result = qb.build()
        filters = result["filters"]
        
        assert len(filters) == 4
        assert filters[0] == {"field": "age", "operator": "gt", "value": 18}
        assert filters[1] == {"field": "score", "operator": "gte", "value": 80}
        assert filters[2] == {"field": "price", "operator": "lt", "value": 100.50}
        assert filters[3] == {"field": "discount", "operator": "lte", "value": 25}

    def test_like_filters(self):
        """Test LIKE and ILIKE filters."""
        qb = FlextApiQueryBuilder()
        
        qb.like("name", "John%")
        qb.ilike("description", "%important%")
        
        result = qb.build()
        filters = result["filters"]
        
        assert len(filters) == 2
        assert filters[0] == {"field": "name", "operator": "like", "value": "John%"}
        assert filters[1] == {"field": "description", "operator": "ilike", "value": "%important%"}

    def test_in_filters(self):
        """Test IN and NOT IN filters."""
        qb = FlextApiQueryBuilder()
        
        qb.in_list("category", ["tech", "business", "science"])
        qb.not_in_list("status", ["deleted", "archived"])
        
        result = qb.build()
        filters = result["filters"]
        
        assert len(filters) == 2
        assert filters[0] == {"field": "category", "operator": "in", "value": ["tech", "business", "science"]}
        assert filters[1] == {"field": "status", "operator": "not_in", "value": ["deleted", "archived"]}

    def test_between_filter(self):
        """Test BETWEEN filter."""
        qb = FlextApiQueryBuilder()
        
        qb.between("price", 10.0, 100.0)
        qb.between("created_at", "2023-01-01", "2023-12-31")
        
        result = qb.build()
        filters = result["filters"]
        
        assert len(filters) == 2
        assert filters[0] == {"field": "price", "operator": "between", "value": [10.0, 100.0]}
        assert filters[1] == {"field": "created_at", "operator": "between", "value": ["2023-01-01", "2023-12-31"]}

    def test_null_filters(self):
        """Test IS NULL and IS NOT NULL filters."""
        qb = FlextApiQueryBuilder()
        
        qb.is_null("deleted_at")
        qb.is_not_null("email")
        
        result = qb.build()
        filters = result["filters"]
        
        assert len(filters) == 2
        assert filters[0] == {"field": "deleted_at", "operator": "is_null"}
        assert filters[1] == {"field": "email", "operator": "is_not_null"}
        
        # Verify no 'value' key for null operators
        assert "value" not in filters[0]
        assert "value" not in filters[1]

    def test_generic_filter_method(self):
        """Test generic filter method with all operators."""
        qb = FlextApiQueryBuilder()
        
        qb.filter("name", FlextApiQueryOperator.LIKE, "%John%")
        qb.filter("age", FlextApiQueryOperator.GREATER_THAN, 25)
        qb.filter("active", FlextApiQueryOperator.EQUALS, True)
        
        result = qb.build()
        filters = result["filters"]
        
        assert len(filters) == 3
        assert filters[0] == {"field": "name", "operator": "like", "value": "%John%"}
        assert filters[1] == {"field": "age", "operator": "gt", "value": 25}
        assert filters[2] == {"field": "active", "operator": "eq", "value": True}


class TestFlextApiQueryBuilderSorting:
    """Sorting functionality tests."""

    def test_sort_ascending(self):
        """Test ascending sort."""
        qb = FlextApiQueryBuilder()
        result = qb.sort_asc("name").build()
        
        expected_sort = {"field": "name", "direction": "asc"}
        assert result["sorts"] == [expected_sort]

    def test_sort_descending(self):
        """Test descending sort."""
        qb = FlextApiQueryBuilder()
        result = qb.sort_desc("created_at").build()
        
        expected_sort = {"field": "created_at", "direction": "desc"}
        assert result["sorts"] == [expected_sort]

    def test_generic_sort_method(self):
        """Test generic sort method."""
        qb = FlextApiQueryBuilder()
        
        qb.sort("priority", "desc")
        qb.sort("name", "asc")
        
        result = qb.build()
        sorts = result["sorts"]
        
        assert len(sorts) == 2
        assert sorts[0] == {"field": "priority", "direction": "desc"}
        assert sorts[1] == {"field": "name", "direction": "asc"}

    def test_multiple_sorts_order(self):
        """Test multiple sorts maintain order."""
        qb = FlextApiQueryBuilder()
        
        qb.sort_desc("priority")
        qb.sort_asc("name")
        qb.sort_desc("created_at")
        
        result = qb.build()
        sorts = result["sorts"]
        
        assert len(sorts) == 3
        assert sorts[0]["field"] == "priority"
        assert sorts[1]["field"] == "name"
        assert sorts[2]["field"] == "created_at"


class TestFlextApiQueryBuilderPagination:
    """Pagination functionality tests."""

    def test_page_method(self):
        """Test page method with page and size."""
        qb = FlextApiQueryBuilder()
        result = qb.page(3, 25).build()
        
        assert result["page"] == 3
        assert result["page_size"] == 25

    def test_limit_method(self):
        """Test limit method."""
        qb = FlextApiQueryBuilder()
        result = qb.limit(100).build()
        
        assert result["limit"] == 100

    def test_page_and_limit_together(self):
        """Test page and limit can coexist."""
        qb = FlextApiQueryBuilder()
        result = qb.page(2, 20).limit(50).build()
        
        assert result["page"] == 2
        assert result["page_size"] == 20
        assert result["limit"] == 50


class TestFlextApiQueryBuilderChaining:
    """Method chaining tests."""

    def test_fluent_interface_chaining(self):
        """Test fluent interface allows method chaining."""
        qb = FlextApiQueryBuilder()
        
        result = (qb
                 .equals("status", "active")
                 .greater_than("age", 18)
                 .like("name", "John%")
                 .sort_desc("created_at")
                 .sort_asc("name")
                 .page(2, 20)
                 .limit(100)
                 .build())
        
        assert len(result["filters"]) == 3
        assert len(result["sorts"]) == 2
        assert result["page"] == 2
        assert result["page_size"] == 20
        assert result["limit"] == 100

    def test_complex_query_building(self):
        """Test building complex real-world query."""
        qb = FlextApiQueryBuilder()
        
        result = (qb
                 .equals("department", "engineering")
                 .in_list("role", ["senior", "lead", "principal"])
                 .greater_than_or_equal("salary", 80000)
                 .between("hire_date", "2020-01-01", "2023-12-31")
                 .is_not_null("email")
                 .like("skills", "%python%")
                 .not_equals("status", "terminated")
                 .sort_desc("salary")
                 .sort_asc("last_name")
                 .page(1, 50)
                 .build())
        
        filters = result["filters"]
        assert len(filters) == 7
        
        # Verify specific filters
        dept_filter = next(f for f in filters if f["field"] == "department")
        assert dept_filter == {"field": "department", "operator": "eq", "value": "engineering"}
        
        role_filter = next(f for f in filters if f["field"] == "role")
        assert role_filter == {"field": "role", "operator": "in", "value": ["senior", "lead", "principal"]}
        
        salary_filter = next(f for f in filters if f["field"] == "salary")
        assert salary_filter == {"field": "salary", "operator": "gte", "value": 80000}
        
        # Verify sorts
        assert len(result["sorts"]) == 2
        assert result["sorts"][0] == {"field": "salary", "direction": "desc"}
        assert result["sorts"][1] == {"field": "last_name", "direction": "asc"}


class TestFlextApiQueryBuilderReset:
    """Reset functionality tests."""

    def test_reset_method(self):
        """Test reset method clears all state."""
        qb = FlextApiQueryBuilder()
        
        # Build complex query
        qb.equals("status", "active")
        qb.sort_desc("created_at")
        qb.page(3, 25)
        qb.limit(100)
        
        # Verify query has content
        result1 = qb.build()
        assert len(result1["filters"]) == 1
        assert len(result1["sorts"]) == 1
        assert result1["page"] == 3
        assert result1["limit"] == 100
        
        # Reset and verify empty
        qb.reset()
        result2 = qb.build()
        
        assert result2["filters"] == []
        assert result2["sorts"] == []
        assert result2["page"] is None
        assert result2["page_size"] is None
        assert result2["limit"] is None

    def test_reset_returns_self(self):
        """Test reset returns self for chaining."""
        qb = FlextApiQueryBuilder()
        
        result = (qb
                 .equals("test", "value")
                 .reset()
                 .equals("new", "query")
                 .build())
        
        # Should only have the filter added after reset
        assert len(result["filters"]) == 1
        assert result["filters"][0] == {"field": "new", "operator": "eq", "value": "query"}


class TestFlextApiQueryBuilderEdgeCases:
    """Edge cases and data type handling."""

    def test_various_data_types(self):
        """Test query builder with various Python data types."""
        qb = FlextApiQueryBuilder()
        
        # Test different value types
        qb.equals("string_field", "text")
        qb.equals("int_field", 42)
        qb.equals("float_field", 3.14159)
        qb.equals("bool_field", True)
        qb.equals("none_field", None)
        qb.equals("date_field", datetime(2023, 12, 25))
        qb.equals("decimal_field", Decimal("99.99"))
        
        result = qb.build()
        filters = result["filters"]
        
        assert len(filters) == 7
        
        # Verify all types are preserved
        values = [f["value"] for f in filters]
        assert "text" in values
        assert 42 in values
        assert 3.14159 in values
        assert True in values
        assert None in values
        assert datetime(2023, 12, 25) in values
        assert Decimal("99.99") in values

    def test_empty_collections(self):
        """Test handling of empty collections."""
        qb = FlextApiQueryBuilder()
        
        qb.in_list("tags", [])
        qb.between("range", [], [])  # This should handle gracefully
        
        result = qb.build()
        filters = result["filters"]
        
        # Empty list should still create filter
        assert len(filters) >= 1
        assert filters[0]["value"] == []

    def test_special_characters_in_strings(self):
        """Test handling of special characters."""
        qb = FlextApiQueryBuilder()
        
        special_values = [
            "unicode_测试",
            "emoji_😀",
            "sql_injection'; DROP TABLE users; --",
            "json_{\"key\": \"value\"}",
            "newlines\n\r\ttabs",
            "quotes'\"mixed",
        ]
        
        for i, value in enumerate(special_values):
            qb.equals(f"field_{i}", value)
        
        result = qb.build()
        filters = result["filters"]
        
        # All special characters should be preserved
        assert len(filters) == len(special_values)
        for i, expected_value in enumerate(special_values):
            assert filters[i]["value"] == expected_value

    def test_field_name_validation(self):
        """Test field names are preserved correctly."""
        qb = FlextApiQueryBuilder()
        
        field_names = [
            "simple_field",
            "field.with.dots",
            "field-with-dashes",
            "field_with_underscores",
            "CamelCaseField",
            "field123",
            "123field",
            "field with spaces",
        ]
        
        for field_name in field_names:
            qb.equals(field_name, "test")
        
        result = qb.build()
        filters = result["filters"]
        
        actual_fields = [f["field"] for f in filters]
        assert actual_fields == field_names


class TestFlextApiQueryBuilderRealWorldScenarios:
    """Real-world usage scenario tests."""

    def test_user_search_query(self):
        """Test typical user search query."""
        qb = FlextApiQueryBuilder()
        
        # Search for active users in engineering or product departments,
        # hired in the last 2 years, with Python skills
        result = (qb
                 .equals("status", "active")
                 .in_list("department", ["engineering", "product"])
                 .greater_than_or_equal("hire_date", "2022-01-01")
                 .like("skills", "%python%")
                 .is_not_null("email")
                 .not_equals("role", "intern")
                 .sort_desc("hire_date")
                 .sort_asc("last_name")
                 .page(1, 25)
                 .build())
        
        assert len(result["filters"]) == 6
        assert len(result["sorts"]) == 2
        assert result["page"] == 1
        assert result["page_size"] == 25

    def test_product_catalog_query(self):
        """Test e-commerce product catalog query."""
        qb = FlextApiQueryBuilder()
        
        # Search for electronics under $500, in stock, with good ratings
        result = (qb
                 .equals("category", "electronics")
                 .less_than_or_equal("price", 500.00)
                 .greater_than("stock_quantity", 0)
                 .greater_than_or_equal("rating", 4.0)
                 .not_in_list("status", ["discontinued", "recall"])
                 .like("tags", "%bestseller%")
                 .sort_desc("rating")
                 .sort_asc("price")
                 .page(1, 12)
                 .build())
        
        filters = result["filters"]
        
        # Verify specific business logic
        price_filter = next(f for f in filters if f["field"] == "price")
        assert price_filter["operator"] == "lte"
        assert price_filter["value"] == 500.00
        
        stock_filter = next(f for f in filters if f["field"] == "stock_quantity")
        assert stock_filter["operator"] == "gt"
        assert stock_filter["value"] == 0

    def test_analytics_date_range_query(self):
        """Test analytics query with date ranges and aggregation hints."""
        qb = FlextApiQueryBuilder()
        
        # Monthly sales report for specific regions
        result = (qb
                 .between("order_date", "2023-01-01", "2023-12-31")
                 .in_list("region", ["US-WEST", "US-EAST", "EU"])
                 .equals("order_status", "completed")
                 .greater_than("total_amount", 0)
                 .is_not_null("customer_id")
                 .sort_desc("order_date")
                 .sort_desc("total_amount")
                 .limit(1000)
                 .build())
        
        # Verify date range handling
        date_filter = next(f for f in result["filters"] if f["field"] == "order_date")
        assert date_filter["operator"] == "between"
        assert date_filter["value"] == ["2023-01-01", "2023-12-31"]

    def test_query_builder_reuse(self):
        """Test reusing query builder for similar queries."""
        qb = FlextApiQueryBuilder()
        
        # Base query for active users
        base_query = (qb
                     .equals("status", "active")
                     .is_not_null("email")
                     .sort_asc("last_name"))
        
        # Admin users query
        admin_result = (base_query
                       .equals("role", "admin")
                       .build())
        
        # Reset and build regular users query
        regular_result = (qb
                         .reset()
                         .equals("status", "active")
                         .is_not_null("email")
                         .equals("role", "user")
                         .greater_than("last_login", "2023-01-01")
                         .sort_asc("last_name")
                         .build())
        
        # Verify different queries were built
        admin_role_filter = next(f for f in admin_result["filters"] if f["field"] == "role")
        assert admin_role_filter["value"] == "admin"
        
        regular_role_filter = next(f for f in regular_result["filters"] if f["field"] == "role")
        assert regular_role_filter["value"] == "user"
        
        # Regular query should have additional filter
        assert len(regular_result["filters"]) > len(admin_result["filters"])