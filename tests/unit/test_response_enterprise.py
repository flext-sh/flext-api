"""ENTERPRISE UNIT TESTS - FlextApiResponseBuilder.

Tests every method, metadata handling, pagination, FlextResult integration,
and real-world response scenarios of FlextApiResponseBuilder.
NO MOCKS - only real functionality validation.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from flext_api.response import (
    FlextApiResponseBuilder,
    success_response,
    error_response,
    paginated_response,
)
from flext_core import FlextResult


class TestFlextApiResponseBuilderBasic:
    """Basic response builder functionality tests."""

    def test_response_builder_initialization(self):
        """Test response builder initialization."""
        rb = FlextApiResponseBuilder()
        
        # Should start with empty state
        assert hasattr(rb, '_success')
        assert hasattr(rb, '_data')
        assert hasattr(rb, '_message')
        assert hasattr(rb, '_error_code')
        assert hasattr(rb, '_metadata')
        assert hasattr(rb, '_pagination')
        assert hasattr(rb, '_timestamp')

    def test_success_response_creation(self):
        """Test creating successful response."""
        rb = FlextApiResponseBuilder()
        
        test_data = {"id": 123, "name": "Test User", "active": True}
        result = rb.success(test_data, "User retrieved successfully").build()
        
        assert result["success"] is True
        assert result["data"] == test_data
        assert result["message"] == "User retrieved successfully"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
        
        # Parse timestamp to verify format
        timestamp = datetime.fromisoformat(result["timestamp"])
        assert isinstance(timestamp, datetime)

    def test_error_response_creation(self):
        """Test creating error response."""
        rb = FlextApiResponseBuilder()
        
        result = rb.error("User not found", 404).build()
        
        assert result["success"] is False
        assert result["message"] == "User not found"
        assert result["error_code"] == 404
        assert "timestamp" in result
        assert "data" not in result  # Error responses shouldn't have data


class TestFlextApiResponseBuilderMetadata:
    """Metadata handling tests."""

    def test_single_metadata_addition(self):
        """Test adding single metadata item."""
        rb = FlextApiResponseBuilder()
        
        result = (rb
                 .success({"test": "data"})
                 .with_metadata("execution_time_ms", 125)
                 .build())
        
        assert "metadata" in result
        assert result["metadata"]["execution_time_ms"] == 125

    def test_multiple_metadata_addition(self):
        """Test adding multiple metadata items."""
        rb = FlextApiResponseBuilder()
        
        result = (rb
                 .success({"users": []})
                 .with_metadata("query_time_ms", 45)
                 .with_metadata("cache_hit", False)
                 .with_metadata("database_server", "primary-db-01")
                 .with_metadata("api_version", "2.1.0")
                 .build())
        
        metadata = result["metadata"]
        assert len(metadata) == 4
        assert metadata["query_time_ms"] == 45
        assert metadata["cache_hit"] is False
        assert metadata["database_server"] == "primary-db-01"
        assert metadata["api_version"] == "2.1.0"

    def test_metadata_with_various_types(self):
        """Test metadata with different data types."""
        rb = FlextApiResponseBuilder()
        
        complex_metadata = {
            "string_value": "test",
            "int_value": 42,
            "float_value": 3.14159,
            "bool_value": True,
            "list_value": [1, 2, 3],
            "dict_value": {"nested": "object"},
            "none_value": None,
            "datetime_value": datetime.now(timezone.utc),
        }
        
        for key, value in complex_metadata.items():
            rb.with_metadata(key, value)
        
        result = rb.success({"test": "data"}).build()
        
        for key, expected_value in complex_metadata.items():
            assert result["metadata"][key] == expected_value

    def test_metadata_overwrite(self):
        """Test metadata key overwriting."""
        rb = FlextApiResponseBuilder()
        
        result = (rb
                 .success({})
                 .with_metadata("version", "1.0")
                 .with_metadata("version", "2.0")  # Overwrite
                 .build())
        
        assert result["metadata"]["version"] == "2.0"


class TestFlextApiResponseBuilderPagination:
    """Pagination functionality tests."""

    def test_basic_pagination(self):
        """Test basic pagination information."""
        rb = FlextApiResponseBuilder()
        
        result = (rb
                 .success([{"id": 1}, {"id": 2}, {"id": 3}])
                 .with_pagination(total=100, page=3, page_size=25)
                 .build())
        
        pagination = result["pagination"]
        assert pagination["total"] == 100
        assert pagination["page"] == 3
        assert pagination["page_size"] == 25
        assert pagination["total_pages"] == 4  # 100 / 25 = 4

    def test_pagination_edge_cases(self):
        """Test pagination with edge cases."""
        rb = FlextApiResponseBuilder()
        
        # Test with 0 total
        result1 = (rb
                  .success([])
                  .with_pagination(total=0, page=1, page_size=10)
                  .build())
        
        assert result1["pagination"]["total_pages"] == 0
        
        # Test with exact division
        rb = FlextApiResponseBuilder()
        result2 = (rb
                  .success([])
                  .with_pagination(total=50, page=1, page_size=10)
                  .build())
        
        assert result2["pagination"]["total_pages"] == 5
        
        # Test with remainder
        rb = FlextApiResponseBuilder()
        result3 = (rb
                  .success([])
                  .with_pagination(total=53, page=1, page_size=10)
                  .build())
        
        assert result3["pagination"]["total_pages"] == 6  # Ceiling of 53/10

    def test_pagination_with_metadata(self):
        """Test pagination combined with metadata."""
        rb = FlextApiResponseBuilder()
        
        result = (rb
                 .success([{"user": "data"}])
                 .with_pagination(total=1000, page=5, page_size=20)
                 .with_metadata("query_complexity", "high")
                 .with_metadata("cache_status", "miss")
                 .build())
        
        assert "pagination" in result
        assert "metadata" in result
        assert len(result["metadata"]) == 2
        assert result["pagination"]["total"] == 1000


class TestFlextApiResponseBuilderFlextResultIntegration:
    """FlextResult integration tests."""

    def test_from_flext_result_success(self):
        """Test creating response from successful FlextResult."""
        rb = FlextApiResponseBuilder()
        
        # Create successful FlextResult
        test_data = {"users": [{"id": 1, "name": "John"}]}
        flext_result = FlextResult.ok(test_data)
        
        result = rb.from_flext_result(flext_result).build()
        
        assert result["success"] is True
        assert result["data"] == test_data
        assert result["message"] == "Operation successful"

    def test_from_flext_result_failure(self):
        """Test creating response from failed FlextResult."""
        rb = FlextApiResponseBuilder()
        
        # Create failed FlextResult
        flext_result = FlextResult.fail("Database connection failed")
        
        result = rb.from_flext_result(flext_result).build()
        
        assert result["success"] is False
        assert result["message"] == "Database connection failed"
        assert "data" not in result

    def test_from_flext_result_with_additional_metadata(self):
        """Test FlextResult integration with additional metadata."""
        rb = FlextApiResponseBuilder()
        
        flext_result = FlextResult.ok({"processed": True})
        
        result = (rb
                 .from_flext_result(flext_result)
                 .with_metadata("processing_time", 250)
                 .with_metadata("worker_id", "worker-03")
                 .build())
        
        assert result["success"] is True
        assert result["data"] == {"processed": True}
        assert result["metadata"]["processing_time"] == 250
        assert result["metadata"]["worker_id"] == "worker-03"


class TestFlextApiResponseBuilderChaining:
    """Method chaining tests."""

    def test_fluent_interface_chaining(self):
        """Test fluent interface allows method chaining."""
        rb = FlextApiResponseBuilder()
        
        result = (rb
                 .success({"items": [1, 2, 3]})
                 .with_metadata("total_count", 3)
                 .with_metadata("source", "database")
                 .with_pagination(total=100, page=1, page_size=3)
                 .build())
        
        assert result["success"] is True
        assert result["data"]["items"] == [1, 2, 3]
        assert len(result["metadata"]) == 2
        assert "pagination" in result

    def test_complex_response_building(self):
        """Test building complex response with all features."""
        rb = FlextApiResponseBuilder()
        
        # Simulate complex API response
        user_data = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"},
                {"id": 3, "name": "Charlie", "role": "user"},
            ]
        }
        
        result = (rb
                 .success(user_data, "Users retrieved successfully")
                 .with_pagination(total=156, page=2, page_size=3)
                 .with_metadata("query_execution_time_ms", 87)
                 .with_metadata("cache_hit", False)
                 .with_metadata("database_queries", 2)
                 .with_metadata("applied_filters", ["active", "verified"])
                 .with_metadata("sort_order", "name_asc")
                 .build())
        
        # Verify all components
        assert result["success"] is True
        assert result["message"] == "Users retrieved successfully"
        assert len(result["data"]["users"]) == 3
        assert result["pagination"]["total"] == 156
        assert result["pagination"]["total_pages"] == 52  # 156 / 3 = 52
        assert len(result["metadata"]) == 5


class TestFlextApiResponseBuilderFactoryFunctions:
    """Factory function tests."""

    def test_success_response_factory(self):
        """Test success_response factory function."""
        data = {"message": "Hello World"}
        result = success_response(data, "Request processed")
        
        assert result["success"] is True
        assert result["data"] == data
        assert result["message"] == "Request processed"
        assert "timestamp" in result

    def test_error_response_factory(self):
        """Test error_response factory function."""
        result = error_response("Invalid input", 400)
        
        assert result["success"] is False
        assert result["message"] == "Invalid input"
        assert result["error_code"] == 400
        assert "timestamp" in result

    def test_paginated_response_factory(self):
        """Test paginated_response factory function."""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = paginated_response(items, total=50, page=1, page_size=3)
        
        assert result["success"] is True
        assert result["data"] == items
        assert result["pagination"]["total"] == 50
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 3
        assert result["pagination"]["total_pages"] == 17  # Ceiling of 50/3


class TestFlextApiResponseBuilderRealWorldScenarios:
    """Real-world usage scenario tests."""

    def test_api_endpoint_success_response(self):
        """Test typical API endpoint success response."""
        # Simulate user list endpoint response
        users = [
            {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
            {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "user"},
            {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "role": "user"},
        ]
        
        rb = FlextApiResponseBuilder()
        result = (rb
                 .success({"users": users}, "Users retrieved successfully")
                 .with_pagination(total=127, page=1, page_size=3)
                 .with_metadata("query_time_ms", 45)
                 .with_metadata("filters_applied", ["active_only", "verified_email"])
                 .with_metadata("sort_by", "name")
                 .with_metadata("api_version", "v2.1")
                 .build())
        
        # Verify realistic API response structure
        assert result["success"] is True
        assert len(result["data"]["users"]) == 3
        assert result["data"]["users"][0]["name"] == "Alice Johnson"
        assert result["pagination"]["total_pages"] == 43  # 127 / 3 = 42.33... -> 43

    def test_api_endpoint_error_response(self):
        """Test typical API endpoint error response."""
        rb = FlextApiResponseBuilder()
        
        result = (rb
                 .error("Authentication failed", 401)
                 .with_metadata("error_code", "AUTH_INVALID_TOKEN")
                 .with_metadata("retry_after_seconds", 300)
                 .with_metadata("support_contact", "support@example.com")
                 .build())
        
        assert result["success"] is False
        assert result["error_code"] == 401
        assert result["message"] == "Authentication failed"
        assert result["metadata"]["error_code"] == "AUTH_INVALID_TOKEN"

    def test_database_query_response(self):
        """Test response from database query operation."""
        # Simulate database query results
        query_results = {
            "products": [
                {"id": 101, "name": "Laptop", "price": 999.99, "stock": 15},
                {"id": 102, "name": "Mouse", "price": 29.99, "stock": 150},
            ]
        }
        
        rb = FlextApiResponseBuilder()
        result = (rb
                 .success(query_results, "Products retrieved")
                 .with_pagination(total=1250, page=5, page_size=2)
                 .with_metadata("database_server", "primary-db-01")
                 .with_metadata("query_plan", "index_scan")
                 .with_metadata("execution_time_ms", 23)
                 .with_metadata("rows_examined", 1250)
                 .with_metadata("rows_returned", 2)
                 .build())
        
        # Verify database-specific metadata
        assert result["metadata"]["database_server"] == "primary-db-01"
        assert result["metadata"]["query_plan"] == "index_scan"
        assert result["metadata"]["rows_examined"] == 1250
        assert result["metadata"]["rows_returned"] == 2

    def test_microservice_response_with_tracing(self):
        """Test microservice response with distributed tracing info."""
        service_data = {"orders": [{"id": "ord_123", "status": "completed"}]}
        
        rb = FlextApiResponseBuilder()
        result = (rb
                 .success(service_data, "Orders processed")
                 .with_metadata("trace_id", "trace_abc123def456")
                 .with_metadata("span_id", "span_789xyz")
                 .with_metadata("service_name", "order-service")
                 .with_metadata("service_version", "1.3.2")
                 .with_metadata("request_id", "req_uuid_001")
                 .with_metadata("correlation_id", "corr_uuid_002")
                 .with_metadata("upstream_services", ["user-service", "payment-service"])
                 .build())
        
        # Verify tracing metadata
        metadata = result["metadata"]
        assert "trace_id" in metadata
        assert "span_id" in metadata
        assert metadata["service_name"] == "order-service"
        assert isinstance(metadata["upstream_services"], list)
        assert len(metadata["upstream_services"]) == 2

    def test_analytics_response_with_metrics(self):
        """Test analytics response with detailed metrics."""
        analytics_data = {
            "summary": {
                "total_users": 1250,
                "active_users": 892,
                "conversion_rate": 0.234
            },
            "breakdown": [
                {"category": "mobile", "count": 650},
                {"category": "desktop", "count": 600}
            ]
        }
        
        rb = FlextApiResponseBuilder()
        result = (rb
                 .success(analytics_data, "Analytics data processed")
                 .with_metadata("date_range", "2023-01-01 to 2023-12-31")
                 .with_metadata("calculation_method", "sliding_window")
                 .with_metadata("data_freshness_minutes", 5)
                 .with_metadata("sample_size", 125000)
                 .with_metadata("confidence_interval", 0.95)
                 .with_metadata("last_updated", datetime.now(timezone.utc).isoformat())
                 .build())
        
        # Verify analytics-specific structure
        assert result["data"]["summary"]["total_users"] == 1250
        assert result["data"]["summary"]["conversion_rate"] == 0.234
        assert len(result["data"]["breakdown"]) == 2
        assert result["metadata"]["confidence_interval"] == 0.95

    def test_error_response_with_validation_details(self):
        """Test error response with detailed validation information."""
        rb = FlextApiResponseBuilder()
        
        validation_errors = [
            {"field": "email", "message": "Invalid email format", "code": "INVALID_EMAIL"},
            {"field": "age", "message": "Must be between 18 and 120", "code": "AGE_OUT_OF_RANGE"},
            {"field": "password", "message": "Must contain special characters", "code": "WEAK_PASSWORD"}
        ]
        
        result = (rb
                 .error("Validation failed", 422)
                 .with_metadata("validation_errors", validation_errors)
                 .with_metadata("error_count", len(validation_errors))
                 .with_metadata("request_body_size", 1024)
                 .with_metadata("validation_time_ms", 12)
                 .build())
        
        assert result["error_code"] == 422
        assert len(result["metadata"]["validation_errors"]) == 3
        assert result["metadata"]["error_count"] == 3
        
        # Verify specific validation error structure
        email_error = result["metadata"]["validation_errors"][0]
        assert email_error["field"] == "email"
        assert email_error["code"] == "INVALID_EMAIL"


class TestFlextApiResponseBuilderEdgeCases:
    """Edge cases and error handling tests."""

    def test_none_data_handling(self):
        """Test handling of None data."""
        rb = FlextApiResponseBuilder()
        
        result = rb.success(None, "No data available").build()
        
        assert result["success"] is True
        assert result["data"] is None
        assert result["message"] == "No data available"

    def test_empty_collections_handling(self):
        """Test handling of empty collections."""
        rb = FlextApiResponseBuilder()
        
        # Empty list
        result1 = rb.success([], "No items found").build()
        assert result1["data"] == []
        
        # Empty dict
        rb = FlextApiResponseBuilder()
        result2 = rb.success({}, "Empty object").build()
        assert result2["data"] == {}

    def test_large_data_structures(self):
        """Test handling of large data structures."""
        # Create large dataset
        large_data = {
            "items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        }
        
        rb = FlextApiResponseBuilder()
        result = (rb
                 .success(large_data, "Large dataset retrieved")
                 .with_pagination(total=10000, page=1, page_size=1000)
                 .with_metadata("dataset_size", len(large_data["items"]))
                 .build())
        
        assert len(result["data"]["items"]) == 1000
        assert result["metadata"]["dataset_size"] == 1000
        assert result["pagination"]["total"] == 10000

    def test_special_characters_in_messages(self):
        """Test handling of special characters in messages."""
        rb = FlextApiResponseBuilder()
        
        special_messages = [
            "Success with unicode: 测试成功",
            "Emoji support: ✅ 🎉 🚀",
            "JSON characters: {\"test\": \"value\"}",
            "SQL injection attempt: '; DROP TABLE users; --",
            "Newlines and\ttabs\r\nincluded",
        ]
        
        for message in special_messages:
            result = rb.success({"test": True}, message).build()
            assert result["message"] == message
            # Reset builder for next test
            rb = FlextApiResponseBuilder()

    def test_timestamp_consistency(self):
        """Test timestamp consistency across builds."""
        rb = FlextApiResponseBuilder()
        
        # Build response
        result1 = rb.success({"test": 1}).build()
        timestamp1 = result1["timestamp"]
        
        # Small delay and build again (same builder instance)
        import time
        time.sleep(0.01)
        
        # Create new builder for fair test
        rb2 = FlextApiResponseBuilder()
        result2 = rb2.success({"test": 2}).build()
        timestamp2 = result2["timestamp"]
        
        # Timestamps should be different (different builder instances)
        assert timestamp1 != timestamp2
        
        # Both should be valid ISO format
        datetime.fromisoformat(timestamp1)
        datetime.fromisoformat(timestamp2)