#!/usr/bin/env python3
"""Test FlextApi Mixins - Validate centralized mixin functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive tests for all mixin patterns - real functionality validation.
"""

import asyncio
import math
from datetime import datetime

import pytest

from flext_api.helpers.flext_api_mixins import (
    FlextApiApplicationClientMixin,
    FlextApiApplicationMixin,
    FlextApiAuthMixin,
    FlextApiBaseMixin,
    FlextApiCacheMixin,
    FlextApiClientMixin,
    FlextApiDataProcessingMixin,
    FlextApiMetricsMixin,
    FlextApiResultMixin,
    FlextApiValidationMixin,
    flext_api_create_application_mixin,
    flext_api_create_base_mixin,
    flext_api_create_client_mixin,
)


class TestFlextApiResultMixin:
    """Test FlextResult mixin for standardized result handling."""

    def test_result_mixin_success(self) -> None:
        """Test success result creation with real data."""

        class TestService(FlextApiResultMixin):
            pass

        service = TestService()
        result = service.flext_api_ok({"user_id": 123}, "User created")

        assert result.is_success
        assert result.data == {"user_id": 123}
        assert result.message == "User created"

    def test_result_mixin_failure(self) -> None:
        """Test failure result creation with error codes."""

        class TestService(FlextApiResultMixin):
            pass

        service = TestService()
        result = service.flext_api_fail("Database connection failed", "DB_ERROR")

        assert result.is_failure
        assert result.error == "Database connection failed"
        assert hasattr(result, "code") or "DB_ERROR" in str(result)

    def test_result_mixin_from_exception(self) -> None:
        """Test exception to result conversion."""

        class TestService(FlextApiResultMixin):
            pass

        service = TestService()
        test_exception = ValueError("Invalid input data")
        result = service.flext_api_from_exception(test_exception)

        assert result.is_failure
        assert "Operation failed: Invalid input data" in result.error

    @pytest.mark.asyncio
    async def test_safe_execute_async_success(self) -> None:
        """Test safe execution with async function success."""

        class TestService(FlextApiResultMixin):
            pass

        service = TestService()

        async def async_operation(value: int) -> int:
            await asyncio.sleep(0.01)
            return value * 2

        result = await service.flext_api_safe_execute(async_operation, 5)

        assert result.is_success
        assert result.data == 10

    @pytest.mark.asyncio
    async def test_safe_execute_sync_success(self) -> None:
        """Test safe execution with sync function."""

        class TestService(FlextApiResultMixin):
            pass

        service = TestService()

        def sync_operation(a: int, b: int) -> int:
            return a + b

        result = await service.flext_api_safe_execute(sync_operation, 3, 7)

        assert result.is_success
        assert result.data == 10

    @pytest.mark.asyncio
    async def test_safe_execute_failure(self) -> None:
        """Test safe execution with function that raises exception."""

        class TestService(FlextApiResultMixin):
            pass

        service = TestService()

        def failing_operation() -> str:
            msg = "Something went wrong"
            raise RuntimeError(msg)

        result = await service.flext_api_safe_execute(failing_operation)

        assert result.is_failure
        assert "Something went wrong" in result.error


class TestFlextApiCacheMixin:
    """Test cache mixin for caching functionality."""

    def test_cache_set_and_get(self) -> None:
        """Test basic cache set and get operations."""

        class CacheTestService(FlextApiCacheMixin):
            pass

        service = CacheTestService()

        # Set cache value
        test_data = {"user_id": 123, "name": "Test User"}
        service.flext_api_cache_set("user:123", test_data)

        # Get cache value
        cached_value = service.flext_api_cache_get("user:123")
        assert cached_value == test_data

    def test_cache_expiration(self) -> None:
        """Test cache expiration functionality."""
        import time

        class CacheTestService(FlextApiCacheMixin):
            def __init__(self) -> None:
                super().__init__()
                self._cache_ttl = 0.1  # Very short TTL for testing

        service = CacheTestService()

        # Set cache value
        service.flext_api_cache_set("expiring_key", "test_value")

        # Should be available immediately
        assert service.flext_api_cache_get("expiring_key") == "test_value"

        # Wait for expiration
        time.sleep(0.2)

        # Should be None after expiration
        assert service.flext_api_cache_get("expiring_key") is None

    def test_cache_with_custom_ttl(self) -> None:
        """Test cache with custom TTL setting."""

        class CacheTestService(FlextApiCacheMixin):
            pass

        service = CacheTestService()

        # Set with custom TTL
        service.flext_api_cache_set("custom_ttl_key", "value", ttl=600)

        # Verify TTL was updated
        assert service._cache_ttl == 600

    def test_cache_clear(self) -> None:
        """Test cache clearing functionality."""

        class CacheTestService(FlextApiCacheMixin):
            pass

        service = CacheTestService()

        # Set multiple values
        service.flext_api_cache_set("key1", "value1")
        service.flext_api_cache_set("key2", "value2")

        # Verify they exist
        assert service.flext_api_cache_get("key1") == "value1"
        assert service.flext_api_cache_get("key2") == "value2"

        # Clear cache
        service.flext_api_cache_clear()

        # Verify they're gone
        assert service.flext_api_cache_get("key1") is None
        assert service.flext_api_cache_get("key2") is None

    def test_cache_stats(self) -> None:
        """Test cache statistics functionality."""

        class CacheTestService(FlextApiCacheMixin):
            pass

        service = CacheTestService()

        # Add some cache entries
        service.flext_api_cache_set("stats_key1", "value1")
        service.flext_api_cache_set("stats_key2", {"complex": "data"})

        stats = service.flext_api_cache_stats()

        assert stats["total_entries"] == 2
        assert "cache_size_bytes" in stats
        assert "oldest_entry" in stats
        assert isinstance(stats["oldest_entry"], datetime)


class TestFlextApiMetricsMixin:
    """Test metrics mixin for metrics tracking."""

    def test_metrics_initialization(self) -> None:
        """Test metrics mixin initialization."""

        class MetricsTestService(FlextApiMetricsMixin):
            pass

        service = MetricsTestService()
        metrics = service.flext_api_metrics_get()

        expected_metrics = [
            "total_requests",
            "successful_requests",
            "failed_requests",
            "success_rate",
            "avg_response_time_ms",
            "cache_hit_rate",
        ]

        for metric in expected_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))

    def test_record_successful_request(self) -> None:
        """Test recording successful request metrics."""

        class MetricsTestService(FlextApiMetricsMixin):
            pass

        service = MetricsTestService()

        # Record successful request
        service.flext_api_metrics_record_request(True, 150.5)

        metrics = service.flext_api_metrics_get()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 0
        assert metrics["success_rate"] == 100.0
        assert metrics["avg_response_time_ms"] == 150.5

    def test_record_failed_request(self) -> None:
        """Test recording failed request metrics."""

        class MetricsTestService(FlextApiMetricsMixin):
            pass

        service = MetricsTestService()

        # Record failed request
        service.flext_api_metrics_record_request(False, 75.2)

        metrics = service.flext_api_metrics_get()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 0
        assert metrics["failed_requests"] == 1
        assert metrics["success_rate"] == 0.0
        assert metrics["avg_response_time_ms"] == 75.2

    def test_mixed_request_metrics(self) -> None:
        """Test metrics with mixed successful and failed requests."""

        class MetricsTestService(FlextApiMetricsMixin):
            pass

        service = MetricsTestService()

        # Record multiple requests
        service.flext_api_metrics_record_request(True, 100.0)  # Success
        service.flext_api_metrics_record_request(True, 200.0)  # Success
        service.flext_api_metrics_record_request(False, 50.0)  # Failure
        service.flext_api_metrics_record_request(True, 150.0)  # Success

        metrics = service.flext_api_metrics_get()
        assert metrics["total_requests"] == 4
        assert metrics["successful_requests"] == 3
        assert metrics["failed_requests"] == 1
        assert metrics["success_rate"] == 75.0  # 3/4 * 100
        assert metrics["avg_response_time_ms"] == 125.0  # (100+200+50+150)/4

    def test_cache_hit_metrics(self) -> None:
        """Test cache hit rate metrics."""

        class MetricsTestService(FlextApiMetricsMixin):
            pass

        service = MetricsTestService()

        # Record requests with cache information
        service.flext_api_metrics_record_request(True, 50.0, cached=True)  # Cache hit
        service.flext_api_metrics_record_request(
            True,
            150.0,
            cached=False,
        )  # Cache miss
        service.flext_api_metrics_record_request(True, 75.0, cached=True)  # Cache hit

        metrics = service.flext_api_metrics_get()
        assert metrics["cache_hit_rate"] == 66.66666666666666  # 2/3 * 100

    def test_metrics_reset(self) -> None:
        """Test metrics reset functionality."""

        class MetricsTestService(FlextApiMetricsMixin):
            pass

        service = MetricsTestService()

        # Record some metrics
        service.flext_api_metrics_record_request(True, 100.0)
        service.flext_api_metrics_record_request(False, 200.0)

        # Verify metrics exist
        metrics_before = service.flext_api_metrics_get()
        assert metrics_before["total_requests"] == 2

        # Reset metrics
        service.flext_api_metrics_reset()

        # Verify metrics are reset
        metrics_after = service.flext_api_metrics_get()
        assert metrics_after["total_requests"] == 0
        assert metrics_after["successful_requests"] == 0
        assert metrics_after["failed_requests"] == 0


class TestFlextApiAuthMixin:
    """Test authentication mixin functionality."""

    def test_set_bearer_token(self) -> None:
        """Test setting bearer token authentication."""

        class AuthTestService(FlextApiAuthMixin):
            pass

        service = AuthTestService()
        service.flext_api_auth_set_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

        headers = service.flext_api_auth_get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

    def test_set_api_key_default_header(self) -> None:
        """Test setting API key with default header name."""

        class AuthTestService(FlextApiAuthMixin):
            pass

        service = AuthTestService()
        service.flext_api_auth_set_api_key("api_key_12345")

        headers = service.flext_api_auth_get_headers()
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "api_key_12345"

    def test_set_api_key_custom_header(self) -> None:
        """Test setting API key with custom header name."""

        class AuthTestService(FlextApiAuthMixin):
            pass

        service = AuthTestService()
        service.flext_api_auth_set_api_key("secret_key_67890", "X-Custom-Key")

        headers = service.flext_api_auth_get_headers()
        assert "X-Custom-Key" in headers
        assert headers["X-Custom-Key"] == "secret_key_67890"

    def test_clear_authentication(self) -> None:
        """Test clearing all authentication data."""

        class AuthTestService(FlextApiAuthMixin):
            pass

        service = AuthTestService()

        # Set both token and API key
        service.flext_api_auth_set_token("test_token")
        service.flext_api_auth_set_api_key("test_api_key")

        # Verify they're set
        headers_before = service.flext_api_auth_get_headers()
        assert len(headers_before) == 2

        # Clear authentication
        service.flext_api_auth_clear()

        # Verify they're cleared
        headers_after = service.flext_api_auth_get_headers()
        assert len(headers_after) == 0
        assert service._auth_token == ""
        assert service._api_key == ""


class TestFlextApiValidationMixin:
    """Test validation mixin functionality."""

    def test_add_and_check_validation_rule(self) -> None:
        """Test adding and checking validation rules."""

        class ValidationTestService(FlextApiValidationMixin):
            pass

        service = ValidationTestService()

        # Add validation rule
        def is_positive_number(value: object) -> bool:
            return isinstance(value, (int, float)) and value > 0

        service.flext_api_validation_add_rule("positive_number", is_positive_number)

        # Test valid data
        assert service.flext_api_validation_check("positive_number", 42) is True
        assert service.flext_api_validation_check("positive_number", math.pi) is True

        # Test invalid data
        assert service.flext_api_validation_check("positive_number", -5) is False
        assert (
            service.flext_api_validation_check("positive_number", "not_a_number")
            is False
        )

    def test_check_nonexistent_rule(self) -> None:
        """Test checking against nonexistent validation rule."""

        class ValidationTestService(FlextApiValidationMixin):
            pass

        service = ValidationTestService()

        # Should return True for nonexistent rules (permissive)
        assert (
            service.flext_api_validation_check("nonexistent_rule", "any_data") is True
        )

    def test_check_all_rules(self) -> None:
        """Test checking against all validation rules."""

        class ValidationTestService(FlextApiValidationMixin):
            pass

        service = ValidationTestService()

        # Add multiple rules
        service.flext_api_validation_add_rule("is_string", lambda x: isinstance(x, str))
        service.flext_api_validation_add_rule("min_length", lambda x: len(x) >= 3)
        service.flext_api_validation_add_rule(
            "contains_letter",
            lambda x: any(c.isalpha() for c in x),
        )

        # Test data that passes all rules
        assert service.flext_api_validation_check_all("hello") is True

        # Test data that fails some rules
        assert service.flext_api_validation_check_all("hi") is False  # Too short
        assert service.flext_api_validation_check_all("123") is False  # No letters
        assert service.flext_api_validation_check_all(123) is False  # Not a string

    def test_get_validation_rules(self) -> None:
        """Test getting list of validation rule names."""

        class ValidationTestService(FlextApiValidationMixin):
            pass

        service = ValidationTestService()

        # Add some rules
        service.flext_api_validation_add_rule("rule1", lambda x: True)
        service.flext_api_validation_add_rule("rule2", lambda x: True)
        service.flext_api_validation_add_rule("rule3", lambda x: True)

        rules = service.flext_api_validation_get_rules()
        assert len(rules) == 3
        assert "rule1" in rules
        assert "rule2" in rules
        assert "rule3" in rules


class TestFlextApiApplicationMixin:
    """Test application mixin for common application patterns."""

    def test_request_context_management(self) -> None:
        """Test request context setting and getting."""

        class AppTestService(FlextApiApplicationMixin):
            pass

        service = AppTestService()

        # Set context values
        service.flext_api_app_set_context("user_id", 12345)
        service.flext_api_app_set_context("correlation_id", "req_abcd1234")

        # Get context values
        assert service.flext_api_app_get_context("user_id") == 12345
        assert service.flext_api_app_get_context("correlation_id") == "req_abcd1234"
        assert service.flext_api_app_get_context("nonexistent") is None

    def test_default_headers_management(self) -> None:
        """Test default headers setting and getting."""

        class AppTestService(FlextApiApplicationMixin):
            pass

        service = AppTestService()

        # Check default headers exist
        default_headers = service.flext_api_app_get_default_headers()
        assert "User-Agent" in default_headers
        assert "Accept" in default_headers
        assert "Content-Type" in default_headers

        # Add custom default header
        service.flext_api_app_set_default_header("X-Custom-Header", "custom_value")

        updated_headers = service.flext_api_app_get_default_headers()
        assert "X-Custom-Header" in updated_headers
        assert updated_headers["X-Custom-Header"] == "custom_value"

    def test_create_request_headers_with_context(self) -> None:
        """Test creating request headers with context information."""

        class AppTestService(FlextApiApplicationMixin):
            pass

        service = AppTestService()

        # Set context
        service.flext_api_app_set_context("user_id", "user_789")
        service.flext_api_app_set_context("correlation_id", "corr_xyz")

        # Create headers with additional headers
        additional = {"Authorization": "Bearer token123"}
        headers = service.flext_api_app_create_request_headers(additional)

        # Check all headers are present
        assert headers["User-Agent"] == "FlextApi/1.0"  # Default
        assert headers["Authorization"] == "Bearer token123"  # Additional
        assert headers["X-User-ID"] == "user_789"  # From context
        assert headers["X-Correlation-ID"] == "corr_xyz"  # From context

    def test_create_request_headers_without_context(self) -> None:
        """Test creating request headers without context."""

        class AppTestService(FlextApiApplicationMixin):
            pass

        service = AppTestService()

        headers = service.flext_api_app_create_request_headers()

        # Should have defaults but no context headers
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Content-Type" in headers
        assert "X-User-ID" not in headers
        assert "X-Correlation-ID" not in headers


class TestFlextApiDataProcessingMixin:
    """Test data processing mixin functionality."""

    def test_extract_nested_field_success(self) -> None:
        """Test extracting nested field using dot notation."""

        class DataTestService(FlextApiDataProcessingMixin):
            pass

        service = DataTestService()

        nested_data = {
            "user": {
                "profile": {"name": "John Doe", "email": "john@example.com"},
                "preferences": {"theme": "dark"},
            },
        }

        # Test various nested extractions
        assert (
            service.flext_api_data_extract_field(nested_data, "user.profile.name")
            == "John Doe"
        )
        assert (
            service.flext_api_data_extract_field(nested_data, "user.profile.email")
            == "john@example.com"
        )
        assert (
            service.flext_api_data_extract_field(nested_data, "user.preferences.theme")
            == "dark"
        )

    def test_extract_nested_field_with_default(self) -> None:
        """Test extracting nonexistent nested field with default value."""

        class DataTestService(FlextApiDataProcessingMixin):
            pass

        service = DataTestService()

        data = {"user": {"name": "John"}}

        # Test with default value
        result = service.flext_api_data_extract_field(
            data,
            "user.email",
            "no_email@example.com",
        )
        assert result == "no_email@example.com"

        # Test deeply nested nonexistent path
        result = service.flext_api_data_extract_field(
            data,
            "user.profile.avatar.url",
            "default_avatar.png",
        )
        assert result == "default_avatar.png"

    def test_transform_response_success(self) -> None:
        """Test transforming response data with successful transformation."""

        class DataTestService(FlextApiDataProcessingMixin):
            pass

        service = DataTestService()

        response = {
            "success": True,
            "data": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
            "status": 200,
            "message": "Users retrieved",
        }

        # Transform to extract just names
        def extract_names(data: list[dict[str, str]]) -> list[str]:
            return [item["name"] for item in data]

        transformed = service.flext_api_data_transform_response(response, extract_names)

        assert transformed["success"] is True
        assert transformed["data"] == ["John", "Jane"]
        assert transformed["status"] == 200

    def test_transform_response_failure(self) -> None:
        """Test transforming response with transformation error."""

        class DataTestService(FlextApiDataProcessingMixin):
            pass

        service = DataTestService()

        response = {
            "success": True,
            "data": {"users": [{"name": "John"}]},
            "status": 200,
            "message": "Success",
        }

        # Transformer that will fail
        def failing_transformer(data: dict[str, object]) -> object:
            return data["nonexistent_key"]  # This will raise KeyError

        transformed = service.flext_api_data_transform_response(
            response,
            failing_transformer,
        )

        assert transformed["success"] is False
        assert transformed["status"] == 500
        assert "Transformation failed" in transformed["message"]

    def test_paginate_request_generation(self) -> None:
        """Test generating paginated request configurations."""

        class DataTestService(FlextApiDataProcessingMixin):
            pass

        service = DataTestService()

        requests = service.flext_api_data_paginate_request(
            "/api/users",
            page_size=25,
            max_pages=3,
        )

        assert len(requests) == 3

        # Check first page
        assert requests[0]["endpoint"] == "/api/users?page=1&size=25"
        assert requests[0]["method"] == "GET"
        assert requests[0]["key"] == "page_1"

        # Check last page
        assert requests[2]["endpoint"] == "/api/users?page=3&size=25"
        assert requests[2]["key"] == "page_3"


class TestCompositeMixins:
    """Test composite mixins that combine multiple patterns."""

    def test_base_mixin_composition(self) -> None:
        """Test FlextApiBaseMixin combines essential patterns."""

        class BaseTestService(FlextApiBaseMixin):
            pass

        service = BaseTestService()

        # Should have FlextResult methods
        result = service.flext_api_ok("test_data")
        assert result.is_success

        # Should have cache methods
        service.flext_api_cache_set("test_key", "test_value")
        assert service.flext_api_cache_get("test_key") == "test_value"

        # Should have metrics methods
        service.flext_api_metrics_record_request(True, 100.0)
        metrics = service.flext_api_metrics_get()
        assert metrics["total_requests"] == 1

    def test_client_mixin_composition(self) -> None:
        """Test FlextApiClientMixin combines client-related patterns."""

        class ClientTestService(FlextApiClientMixin):
            pass

        service = ClientTestService()

        # Should have all base mixin functionality
        result = service.flext_api_ok("test")
        assert result.is_success

        # Should have auth functionality
        service.flext_api_auth_set_token("test_token")
        headers = service.flext_api_auth_get_headers()
        assert "Authorization" in headers

        # Should have validation functionality
        service.flext_api_validation_add_rule("test_rule", lambda x: True)
        assert "test_rule" in service.flext_api_validation_get_rules()

    def test_application_client_mixin_composition(self) -> None:
        """Test FlextApiApplicationClientMixin combines all patterns."""

        class FullTestService(FlextApiApplicationClientMixin):
            pass

        service = FullTestService()

        # Should have client functionality
        service.flext_api_auth_set_token("token")
        assert "Authorization" in service.flext_api_auth_get_headers()

        # Should have application functionality
        service.flext_api_app_set_context("user_id", 123)
        assert service.flext_api_app_get_context("user_id") == 123

        # Should have data processing functionality
        data = {"nested": {"value": "test"}}
        extracted = service.flext_api_data_extract_field(data, "nested.value")
        assert extracted == "test"


class TestFactoryFunctions:
    """Test factory functions for simplified mixin creation."""

    def test_create_base_mixin(self) -> None:
        """Test base mixin factory function."""
        base_mixin = flext_api_create_base_mixin()

        assert isinstance(base_mixin, FlextApiBaseMixin)

        # Test essential functionality
        result = base_mixin.flext_api_ok("test_data")
        assert result.is_success
        assert result.data == "test_data"

    def test_create_client_mixin(self) -> None:
        """Test client mixin factory function."""
        client_mixin = flext_api_create_client_mixin()

        assert isinstance(client_mixin, FlextApiClientMixin)

        # Test client-specific functionality
        client_mixin.flext_api_auth_set_api_key("test_key")
        headers = client_mixin.flext_api_auth_get_headers()
        assert headers["X-API-Key"] == "test_key"

    def test_create_application_mixin(self) -> None:
        """Test application mixin factory function."""
        app_mixin = flext_api_create_application_mixin()

        assert isinstance(app_mixin, FlextApiApplicationClientMixin)

        # Test complete functionality
        app_mixin.flext_api_app_set_context("test_key", "test_value")
        assert app_mixin.flext_api_app_get_context("test_key") == "test_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
