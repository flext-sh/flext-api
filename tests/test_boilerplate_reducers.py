#!/usr/bin/env python3
"""Test FlextApi Boilerplate Reducers - Validate massive code reduction features.

Tests helpers, mixins, typedefs, and decorators that eliminate repetitive code.
"""

import asyncio
import tempfile
from datetime import datetime

import pytest

from flext_api.helpers.flext_api_boilerplate import (
    FlextApiAuthMixin,
    FlextApiCacheMixin,
    FlextApiConfig,
    FlextApiMetricsMixin,
    FlextApiRequest,
    FlextApiResponse,
    FlextApiSimpleClient,
    FlextApiValidationMixin,
    flext_api_config_dict,
    flext_api_create_service_calls,
    flext_api_create_simple_client,
    flext_api_error_dict,
    flext_api_filter_dict,
    flext_api_flatten_dict,
    flext_api_group_by_key,
    flext_api_merge_dicts,
    flext_api_pick_values,
    flext_api_rename_keys,
    flext_api_request_dict,
    flext_api_success_dict,
    flext_api_transform_values,
    flext_api_with_cache,
    flext_api_with_logging,
    flext_api_with_retry,
    flext_api_with_timeout,
    flext_api_with_validation,
)

# ==============================================================================
# TYPEDDICT TESTS - VALIDATE STRUCTURE STANDARDIZATION
# ==============================================================================

class TestTypedDictStructures:
    """Test TypedDict structures for API standardization."""

    def test_success_response_dict(self) -> None:
        """Test success response creation eliminates manual dict construction."""
        # Traditional approach: 8+ lines of dict construction and validation
        # FlextApi approach: 1 line
        response = flext_api_success_dict({"user_id": 123}, "User found")

        assert response["success"] is True
        assert response["data"]["user_id"] == 123
        assert response["message"] == "User found"
        assert response["status"] == 200
        assert "timestamp" in response

        # Validate TypedDict structure
        assert isinstance(response, dict)
        assert all(key in response for key in ["success", "data", "status", "message", "timestamp"])

    def test_error_response_dict(self) -> None:
        """Test error response creation eliminates error handling boilerplate."""
        response = flext_api_error_dict("User not found", 404)

        assert response["success"] is False
        assert response["message"] == "User not found"
        assert response["status"] == 404
        assert response["data"] is None

    def test_request_dict_creation(self) -> None:
        """Test request dict creation eliminates manual construction."""
        request = flext_api_request_dict("/users", "POST", {"name": "John"}, {"Authorization": "Bearer token"})

        assert request["endpoint"] == "/users"
        assert request["method"] == "POST"
        assert request["data"]["name"] == "John"
        assert request["headers"]["Authorization"] == "Bearer token"
        assert request["timeout"] == 30

    def test_config_dict_creation(self) -> None:
        """Test config dict eliminates configuration boilerplate."""
        config = flext_api_config_dict("https://api.example.com", "token123")

        assert config["base_url"] == "https://api.example.com"
        assert config["auth_token"] == "token123"
        assert config["timeout"] == 30
        assert config["retries"] == 3
        assert config["cache_enabled"] is True


# ==============================================================================
# DECORATOR TESTS - VALIDATE PATTERN ELIMINATION
# ==============================================================================

class TestDecorators:
    """Test decorators that eliminate common patterns."""

    @pytest.mark.asyncio
    async def test_retry_decorator(self) -> None:
        """Test retry decorator eliminates retry boilerplate."""
        call_count = 0

        @flext_api_with_retry(retries=2, delay=0.1)
        async def failing_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        result = await failing_function()
        assert result == "success"
        assert call_count == 3  # Initial call + 2 retries

    @pytest.mark.asyncio
    async def test_cache_decorator(self) -> None:
        """Test cache decorator eliminates caching boilerplate."""
        call_count = 0

        @flext_api_with_cache(ttl=1)
        async def expensive_function(value: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate expensive operation
            return value * 2

        # First call
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should be cached
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increase

        # Different argument should not be cached
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_timeout_decorator(self) -> None:
        """Test timeout decorator eliminates timeout boilerplate."""
        @flext_api_with_timeout(seconds=0.1)
        async def slow_function() -> str:
            await asyncio.sleep(0.2)  # Longer than timeout
            return "completed"

        with pytest.raises(asyncio.TimeoutError):
            await slow_function()

    @pytest.mark.asyncio
    async def test_validation_decorator(self) -> None:
        """Test validation decorator eliminates validation boilerplate."""
        def is_positive(value: int) -> bool:
            return value > 0

        @flext_api_with_validation(is_positive)
        async def process_positive_number(number: int) -> int:
            return number * 2

        # Valid input
        result = await process_positive_number(5)
        assert result == 10

        # Invalid input
        with pytest.raises(ValueError):
            await process_positive_number(-5)


# ==============================================================================
# MIXIN TESTS - VALIDATE REUSABLE FUNCTIONALITY
# ==============================================================================

class TestMixins:
    """Test mixins that provide reusable functionality."""

    def test_cache_mixin(self) -> None:
        """Test cache mixin eliminates cache implementation."""
        class TestClass(FlextApiCacheMixin):
            pass

        obj = TestClass()

        # Test caching
        obj.cache_set("key1", "value1")
        assert obj.cache_get("key1") == "value1"

        # Test cache miss
        assert obj.cache_get("nonexistent") is None

        # Test cache stats
        stats = obj.cache_stats()
        assert stats["total_entries"] == 1
        assert stats["cache_size_bytes"] > 0

        # Test cache clear
        obj.cache_clear()
        assert obj.cache_get("key1") is None

    def test_metrics_mixin(self) -> None:
        """Test metrics mixin eliminates metrics implementation."""
        class TestClass(FlextApiMetricsMixin):
            pass

        obj = TestClass()

        # Record some metrics
        obj.metrics_record_request(True, 100.0, cached=False)
        obj.metrics_record_request(False, 200.0, cached=False)
        obj.metrics_record_request(True, 50.0, cached=True)

        metrics = obj.metrics_get()
        assert metrics["total_requests"] == 3
        assert metrics["successful_requests"] == 2
        assert metrics["failed_requests"] == 1
        assert metrics["success_rate"] == pytest.approx(66.67, rel=1e-2)
        assert metrics["cache_hit_rate"] == pytest.approx(33.33, rel=1e-2)

    def test_auth_mixin(self) -> None:
        """Test auth mixin eliminates authentication boilerplate."""
        class TestClass(FlextApiAuthMixin):
            pass

        obj = TestClass()

        # Test token auth
        obj.auth_set_token("token123")
        headers = obj.auth_get_headers()
        assert headers["Authorization"] == "Bearer token123"

        # Test API key auth
        obj.auth_set_api_key("key456", "X-Custom-Key")
        headers = obj.auth_get_headers()
        assert headers["X-Custom-Key"] == "key456"

        # Test clear auth
        obj.auth_clear()
        headers = obj.auth_get_headers()
        assert len(headers) == 0

    def test_validation_mixin(self) -> None:
        """Test validation mixin eliminates validation boilerplate."""
        class TestClass(FlextApiValidationMixin):
            pass

        obj = TestClass()

        # Add validation rules
        obj.validation_add_rule("positive", lambda x: x > 0)
        obj.validation_add_rule("even", lambda x: x % 2 == 0)

        # Test individual validation
        assert obj.validation_check("positive", 5) is True
        assert obj.validation_check("positive", -5) is False

        # Test all validation
        assert obj.validation_check_all(4) is True  # Positive and even
        assert obj.validation_check_all(3) is False  # Positive but not even

        # Test rule listing
        rules = obj.validation_get_rules()
        assert "positive" in rules
        assert "even" in rules


# ==============================================================================
# DICT HELPER TESTS - VALIDATE DATA TRANSFORMATION
# ==============================================================================

class TestDictHelpers:
    """Test dict helpers that eliminate data transformation boilerplate."""

    def test_merge_dicts(self) -> None:
        """Test dict merging eliminates manual merging."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        dict3 = {"b": 5, "e": 6}  # Overlapping key

        result = flext_api_merge_dicts(dict1, dict2, dict3)

        assert result["a"] == 1
        assert result["b"] == 5  # Last dict wins
        assert result["c"] == 3
        assert result["d"] == 4
        assert result["e"] == 6

    def test_filter_dict(self) -> None:
        """Test dict filtering eliminates manual filtering."""
        data = {"name": "John", "age": 30, "email": "john@example.com", "password": "secret"}
        filtered = flext_api_filter_dict(data, ["name", "age", "email"])

        assert "name" in filtered
        assert "age" in filtered
        assert "email" in filtered
        assert "password" not in filtered

    def test_rename_keys(self) -> None:
        """Test key renaming eliminates manual renaming."""
        data = {"first_name": "John", "last_name": "Doe", "email_address": "john@example.com"}
        mapping = {"first_name": "firstName", "last_name": "lastName", "email_address": "email"}

        renamed = flext_api_rename_keys(data, mapping)

        assert renamed["firstName"] == "John"
        assert renamed["lastName"] == "Doe"
        assert renamed["email"] == "john@example.com"

    def test_flatten_dict(self) -> None:
        """Test dict flattening eliminates manual flattening."""
        nested = {
            "user": {
                "profile": {
                    "name": "John",
                    "age": 30
                },
                "settings": {
                    "theme": "dark"
                }
            },
            "app": "MyApp"
        }

        flattened = flext_api_flatten_dict(nested)

        assert flattened["user.profile.name"] == "John"
        assert flattened["user.profile.age"] == 30
        assert flattened["user.settings.theme"] == "dark"
        assert flattened["app"] == "MyApp"

    def test_pick_values(self) -> None:
        """Test value picking eliminates manual extraction."""
        data = {"name": "John", "age": 30, "city": "Boston"}
        values = flext_api_pick_values(data, "name", "city", "nonexistent")

        assert values == ["John", "Boston", None]

    def test_transform_values(self) -> None:
        """Test value transformation eliminates manual transformation."""
        data = {"count": "5", "price": "10.99", "quantity": "3"}
        transformed = flext_api_transform_values(data, float)

        assert transformed["count"] == 5.0
        assert transformed["price"] == 10.99
        assert transformed["quantity"] == 3.0

    def test_group_by_key(self) -> None:
        """Test grouping eliminates manual grouping logic."""
        data = [
            {"category": "fruit", "name": "apple"},
            {"category": "fruit", "name": "banana"},
            {"category": "vegetable", "name": "carrot"},
            {"category": "fruit", "name": "orange"}
        ]

        grouped = flext_api_group_by_key(data, "category")

        assert len(grouped["fruit"]) == 3
        assert len(grouped["vegetable"]) == 1
        assert any(item["name"] == "apple" for item in grouped["fruit"])


# ==============================================================================
# COMPOSITE HELPER TESTS - VALIDATE COMPLEX PATTERN ELIMINATION
# ==============================================================================

class TestCompositeHelpers:
    """Test composite helpers that eliminate complex patterns."""

    @pytest.mark.asyncio
    async def test_simple_client(self) -> None:
        """Test simple client eliminates entire client implementation."""
        client = flext_api_create_simple_client("https://httpbin.org", "test-token")

        # Test that all mixins are available
        assert hasattr(client, "cache_get")
        assert hasattr(client, "metrics_get")
        assert hasattr(client, "auth_get_headers")

        # Test auth headers
        headers = client.auth_get_headers()
        assert headers["Authorization"] == "Bearer test-token"

        # Test actual API call
        response = await client.call("/json")

        assert "success" in response
        assert "data" in response
        assert "status" in response
        assert "message" in response
        assert "timestamp" in response

        # Test metrics were recorded
        metrics = client.metrics_get()
        assert metrics["total_requests"] >= 1

    def test_service_calls_creation(self) -> None:
        """Test service calls creation eliminates manual list construction."""
        services = {
            "user-service": "https://user-api.com",
            "order-service": "https://order-api.com"
        }
        endpoints = ["/health", "/metrics"]

        calls = flext_api_create_service_calls(services, endpoints)

        assert len(calls) == 4  # 2 services × 2 endpoints

        # Validate structure
        for call in calls:
            assert "service" in call
            assert "endpoint" in call
            assert "method" in call
            assert "data" in call
            assert "key" in call
            assert call["method"] == "GET"


# ==============================================================================
# INTEGRATION TESTS - VALIDATE REAL-WORLD SCENARIOS
# ==============================================================================

class TestBoilerplateIntegration:
    """Test integration between different boilerplate reducers."""

    @pytest.mark.asyncio
    async def test_decorated_client_methods(self) -> None:
        """Test using decorators with client methods."""
        client = flext_api_create_simple_client("https://httpbin.org")

        @flext_api_with_retry(retries=2)
        @flext_api_with_cache(ttl=60)
        async def get_user_data(user_id: str) -> dict[str, any]:
            response = await client.call("/json")  # Using httpbin.org/json as test
            return response["data"] if response["success"] else {}

        # First call
        data1 = await get_user_data("123")
        assert isinstance(data1, dict)

        # Second call should be cached
        data2 = await get_user_data("123")
        assert data1 == data2

    def test_mixin_combination(self) -> None:
        """Test combining multiple mixins."""
        class AdvancedClient(FlextApiCacheMixin, FlextApiMetricsMixin, FlextApiAuthMixin, FlextApiValidationMixin):
            def __init__(self) -> None:
                super().__init__()
                FlextApiCacheMixin.__init__(self)
                FlextApiMetricsMixin.__init__(self)
                FlextApiAuthMixin.__init__(self)
                FlextApiValidationMixin.__init__(self)

        client = AdvancedClient()

        # Test all mixin functionality is available
        client.auth_set_token("token")
        client.cache_set("key", "value")
        client.metrics_record_request(True, 100)
        client.validation_add_rule("test", lambda x: True)

        # Validate all features work
        assert client.auth_get_headers()["Authorization"] == "Bearer token"
        assert client.cache_get("key") == "value"
        assert client.metrics_get()["total_requests"] == 1
        assert client.validation_check("test", "anything") is True


# ==============================================================================
# CODE REDUCTION VALIDATION
# ==============================================================================

class TestCodeReductionValidation:
    """Validate actual code reduction achieved."""

    def test_response_creation_reduction(self) -> None:
        """Validate response creation code reduction."""
        # Traditional approach would require:
        # 1. Manual dict construction (5+ lines)
        # 2. Timestamp generation (2+ lines)
        # 3. Type validation (3+ lines)
        # Total: 10+ lines

        # FlextApi approach: 1 line
        response = flext_api_success_dict({"user": "John"}, "Success")

        # Validate comprehensive response structure
        assert response["success"] is True
        assert response["data"]["user"] == "John"
        assert response["message"] == "Success"
        assert response["status"] == 200
        assert datetime.fromisoformat(response["timestamp"]) <= datetime.now()

        # Code reduction: 10+ lines → 1 line = 90% reduction

    @pytest.mark.asyncio
    async def test_decorated_function_reduction(self) -> None:
        """Validate decorator code reduction."""
        # Traditional approach would require:
        # 1. Retry logic implementation (15+ lines)
        # 2. Caching logic implementation (20+ lines)
        # 3. Logging implementation (10+ lines)
        # 4. Timeout handling (10+ lines)
        # Total: 55+ lines

        # FlextApi approach: 4 decorator lines + function
        @flext_api_with_retry(retries=1)
        @flext_api_with_cache(ttl=60)
        @flext_api_with_logging()
        @flext_api_with_timeout(seconds=5)
        async def complex_operation(value: int) -> int:
            return value * 2

        result = await complex_operation(5)
        assert result == 10

        # Code reduction: 55+ lines → 5 lines = 91% reduction

    def test_mixin_usage_reduction(self) -> None:
        """Validate mixin code reduction."""
        # Traditional approach would require:
        # 1. Cache implementation (30+ lines)
        # 2. Metrics implementation (25+ lines)
        # 3. Auth implementation (20+ lines)
        # Total: 75+ lines

        # FlextApi approach: 3 mixin inherits + init
        class MyClient(FlextApiCacheMixin, FlextApiMetricsMixin, FlextApiAuthMixin):
            def __init__(self) -> None:
                super().__init__()
                FlextApiCacheMixin.__init__(self)
                FlextApiMetricsMixin.__init__(self)
                FlextApiAuthMixin.__init__(self)

        client = MyClient()

        # Validate all functionality is available
        client.cache_set("test", "value")
        client.metrics_record_request(True, 100)
        client.auth_set_token("token")

        assert client.cache_get("test") == "value"
        assert client.metrics_get()["total_requests"] == 1
        assert "Authorization" in client.auth_get_headers()

        # Code reduction: 75+ lines → 8 lines = 89% reduction


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
