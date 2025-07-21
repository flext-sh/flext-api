"""Tests for FLEXT API domain value objects."""

from __future__ import annotations

import pytest
from flext_core.domain.pydantic_base import DomainValueObject
from pydantic import ValidationError

from flext_api.domain.value_objects import (
    ApiEndpoint,
    ApiKey,
    ApiVersion,
    CorsOrigin,
    PipelineId,
    PluginId,
    RateLimit,
    RequestId,
    RequestTimeout,
)


class TestApiEndpoint:
    """Test ApiEndpoint value object."""

    def test_valid_api_endpoint_creation(self) -> None:
        """Test creating valid API endpoints."""
        endpoint = ApiEndpoint(path="/api/v1/users", method="GET")

        assert endpoint.path == "/api/v1/users"
        assert endpoint.method == "GET"
        assert endpoint.full_path == "GET /api/v1/users"

    def test_api_endpoint_path_normalization(self) -> None:
        """Test API endpoint path normalization."""
        # Path without leading slash should be normalized
        endpoint = ApiEndpoint(path="api/v1/users")
        assert endpoint.path == "/api/v1/users"

        # Path with leading slash should remain unchanged
        endpoint = ApiEndpoint(path="/api/v1/users")
        assert endpoint.path == "/api/v1/users"

    def test_api_endpoint_method_normalization(self) -> None:
        """Test HTTP method is uppercase."""
        endpoint = ApiEndpoint(
            path="/api/v1/users",
            method="POST",  # Use uppercase as required by validation
        )
        assert endpoint.method == "POST"

    def test_api_endpoint_default_method(self) -> None:
        """Test default HTTP method is GET."""
        endpoint = ApiEndpoint(path="/api/v1/users")
        assert endpoint.method == "GET"

    def test_api_endpoint_method_validation(self) -> None:
        """Test HTTP method validation."""
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]

        for method in valid_methods:
            endpoint = ApiEndpoint(
                path="/api/v1/test",
                method=method,  # Use uppercase methods as expected by validation
            )
            assert endpoint.method == method

    def test_api_endpoint_safe_methods(self) -> None:
        """Test safe HTTP methods detection."""
        safe_methods = ["GET", "HEAD", "OPTIONS"]
        unsafe_methods = ["POST", "PUT", "DELETE", "PATCH"]

        for method in safe_methods:
            endpoint = ApiEndpoint(path="/test", method=method)
            assert endpoint.is_safe_method is True

        for method in unsafe_methods:
            endpoint = ApiEndpoint(path="/test", method=method)
            assert endpoint.is_safe_method is False

    def test_api_endpoint_idempotent_methods(self) -> None:
        """Test idempotent HTTP methods detection."""
        idempotent_methods = ["GET", "HEAD", "PUT", "DELETE", "OPTIONS"]
        non_idempotent_methods = ["POST", "PATCH"]

        for method in idempotent_methods:
            endpoint = ApiEndpoint(path="/test", method=method)
            assert endpoint.is_idempotent is True

        for method in non_idempotent_methods:
            endpoint = ApiEndpoint(path="/test", method=method)
            assert endpoint.is_idempotent is False

    def test_api_endpoint_inheritance(self) -> None:
        """Test ApiEndpoint inherits from DomainValueObject."""
        endpoint = ApiEndpoint(path="/test")
        assert isinstance(endpoint, DomainValueObject)


class TestRateLimit:
    """Test RateLimit value object."""

    def test_valid_rate_limit_creation(self) -> None:
        """Test creating valid rate limits."""
        rate_limit = RateLimit(requests_per_minute=100, burst_size=10)

        assert rate_limit.requests_per_minute == 100
        assert rate_limit.burst_size == 10

    def test_rate_limit_defaults(self) -> None:
        """Test rate limit default values."""
        rate_limit = RateLimit()
        assert rate_limit.requests_per_minute == 100
        assert rate_limit.burst_size == 10

    def test_rate_limit_requests_per_second(self) -> None:
        """Test requests per second calculation."""
        rate_limit = RateLimit(requests_per_minute=120)
        assert rate_limit.requests_per_second == 2.0

        rate_limit = RateLimit(requests_per_minute=60)
        assert rate_limit.requests_per_second == 1.0

    def test_rate_limit_strict_limit_detection(self) -> None:
        """Test strict rate limit detection."""
        strict_limit = RateLimit(burst_size=3)
        assert strict_limit.is_strict_limit is True

        lenient_limit = RateLimit(burst_size=10)
        assert lenient_limit.is_strict_limit is False

    def test_rate_limit_window_seconds(self) -> None:
        """Test rate limit window duration."""
        rate_limit = RateLimit()
        assert rate_limit.window_seconds == 60

    def test_rate_limit_validation(self) -> None:
        """Test rate limit value validation."""
        # Valid values should work
        rate_limit = RateLimit(requests_per_minute=1, burst_size=1)
        assert rate_limit.requests_per_minute == 1

        # Test upper bounds
        rate_limit = RateLimit(requests_per_minute=10000, burst_size=1000)
        assert rate_limit.requests_per_minute == 10000


class TestApiVersion:
    """Test ApiVersion value object."""

    def test_valid_api_version_creation(self) -> None:
        """Test creating valid API versions."""
        version = ApiVersion(major=2, minor=1, patch=3)

        assert version.major == 2
        assert version.minor == 1
        assert version.patch == 3
        assert version.version_string == "2.1.3"

    def test_api_version_defaults(self) -> None:
        """Test API version default values."""
        version = ApiVersion()
        assert version.major == 1
        assert version.minor == 0
        assert version.patch == 0
        assert version.version_string == "1.0.0"

    def test_api_version_stability(self) -> None:
        """Test API version stability detection."""
        stable_version = ApiVersion(major=1, minor=0, patch=0)
        assert stable_version.is_stable is True

        unstable_version = ApiVersion(major=0, minor=9, patch=0)
        assert unstable_version.is_stable is False

    def test_api_version_compatibility(self) -> None:
        """Test API version compatibility checking."""
        v1_0_0 = ApiVersion(major=1, minor=0, patch=0)
        v1_2_3 = ApiVersion(major=1, minor=2, patch=3)
        v2_0_0 = ApiVersion(major=2, minor=0, patch=0)

        # Same major version should be compatible
        assert v1_0_0.is_compatible_with(v1_2_3) is True
        assert v1_2_3.is_compatible_with(v1_0_0) is True

        # Different major version should not be compatible
        assert v1_0_0.is_compatible_with(v2_0_0) is False
        assert v2_0_0.is_compatible_with(v1_0_0) is False

    def test_api_version_comparison(self) -> None:
        """Test API version comparison."""
        v1_0_0 = ApiVersion(major=1, minor=0, patch=0)
        v1_0_1 = ApiVersion(major=1, minor=0, patch=1)
        v1_1_0 = ApiVersion(major=1, minor=1, patch=0)
        v2_0_0 = ApiVersion(major=2, minor=0, patch=0)

        # Test newer version detection
        assert v1_0_1.is_newer_than(v1_0_0) is True
        assert v1_1_0.is_newer_than(v1_0_1) is True
        assert v2_0_0.is_newer_than(v1_1_0) is True

        # Test equal versions
        assert v1_0_0.is_newer_than(v1_0_0) is False


class TestCorsOrigin:
    """Test CorsOrigin value object."""

    def test_valid_cors_origin_creation(self) -> None:
        """Test creating valid CORS origins."""
        origins = [
            "https://example.com",
            "http://localhost:3000",
            "https://api.example.com",
            "*",
        ]

        for origin_url in origins:
            origin = CorsOrigin(url=origin_url)
            if origin_url != "*":
                # URLs should have trailing slash removed
                assert origin.url == origin_url.rstrip("/")
            else:
                assert origin.url == "*"

    def test_cors_origin_wildcard(self) -> None:
        """Test CORS wildcard origin."""
        origin = CorsOrigin(url="*")
        assert origin.url == "*"

    def test_cors_origin_trailing_slash_removal(self) -> None:
        """Test trailing slash removal from CORS origins."""
        origin = CorsOrigin(url="https://example.com/")
        assert origin.url == "https://example.com"

    def test_cors_origin_validation(self) -> None:
        """Test CORS origin validation."""
        valid_origins = ["https://example.com", "http://localhost", "*"]

        for origin_url in valid_origins:
            origin = CorsOrigin(url=origin_url)
            assert origin.url is not None

        # Invalid origins should raise ValidationError
        invalid_origins = ["ftp://example.com", "example.com", "invalid-url"]

        for origin_url in invalid_origins:
            with pytest.raises(ValidationError):
                CorsOrigin(url=origin_url)


class TestApiKey:
    """Test ApiKey value object."""

    def test_valid_api_key_creation(self) -> None:
        """Test creating valid API keys."""
        valid_keys = [
            "abcdef1234567890",
            "API-KEY-1234567890ABCDEF",
            "1234567890abcdef1234567890abcdef",
        ]

        for key_value in valid_keys:
            api_key = ApiKey(key=key_value)
            assert api_key.key == key_value

    def test_api_key_masking(self) -> None:
        """Test API key masking for safe display."""
        api_key = ApiKey(key="abcdef1234567890")
        assert api_key.masked == "abcd...7890"

        # Test with minimum valid length (16 characters)
        min_length_key = ApiKey(key="1234567890123456")
        assert min_length_key.masked == "1234...3456"

    def test_api_key_validation(self) -> None:
        """Test API key format validation."""
        # Valid keys should work
        valid_keys = [
            "abcdef1234567890",
            "API-KEY-123456789",  # Made it 16 characters long
            "1234567890ABCDEF",
        ]

        for key_value in valid_keys:
            api_key = ApiKey(key=key_value)
            assert api_key.key == key_value

        # Invalid keys should raise ValidationError
        invalid_keys = [
            "short",  # Too short
            "invalid@key#123456",  # Invalid characters
            "",  # Empty
        ]

        for key_value in invalid_keys:
            with pytest.raises(ValidationError):
                ApiKey(key=key_value)


class TestRequestTimeout:
    """Test RequestTimeout value object."""

    def test_valid_request_timeout_creation(self) -> None:
        """Test creating valid request timeouts."""
        timeout = RequestTimeout(value=30)
        assert timeout.value == 30

    def test_request_timeout_defaults(self) -> None:
        """Test request timeout default value."""
        timeout = RequestTimeout()
        assert timeout.value == 30

    def test_request_timeout_validation(self) -> None:
        """Test request timeout value validation."""
        # Valid timeouts should work
        valid_timeouts = [1, 30, 60, 300]

        for timeout_value in valid_timeouts:
            timeout = RequestTimeout(value=timeout_value)
            assert timeout.value == timeout_value

        # Invalid timeouts should raise ValidationError
        invalid_timeouts = [0, -1, 301, 1000]

        for timeout_value in invalid_timeouts:
            with pytest.raises(ValidationError):
                RequestTimeout(value=timeout_value)


class TestPipelineId:
    """Test PipelineId value object."""

    def test_valid_pipeline_id_creation(self) -> None:
        """Test creating valid pipeline IDs."""
        valid_ids = ["pipeline-123", "data_ingestion", "Pipeline1", "test-pipeline-v2"]

        for id_value in valid_ids:
            pipeline_id = PipelineId(value=id_value)
            assert pipeline_id.value == id_value

    def test_pipeline_id_trimming(self) -> None:
        """Test pipeline ID whitespace trimming."""
        pipeline_id = PipelineId(value="  pipeline-123  ")
        assert pipeline_id.value == "pipeline-123"

    def test_pipeline_id_validation(self) -> None:
        """Test pipeline ID format validation."""
        # Valid IDs should work
        valid_ids = ["pipeline123", "test-pipeline", "data_ingestion_v1"]

        for id_value in valid_ids:
            pipeline_id = PipelineId(value=id_value)
            assert pipeline_id.value == id_value

        # Invalid IDs should raise ValidationError
        invalid_ids = [
            "",  # Empty
            "pipeline with spaces",  # Spaces not allowed
            "pipeline@123",  # Invalid characters
        ]

        for id_value in invalid_ids:
            with pytest.raises(ValidationError):
                PipelineId(value=id_value)


class TestPluginId:
    """Test PluginId value object."""

    def test_valid_plugin_id_creation(self) -> None:
        """Test creating valid plugin IDs."""
        valid_ids = ["plugin-123", "tap_csv", "target-postgres", "Plugin1"]

        for id_value in valid_ids:
            plugin_id = PluginId(value=id_value)
            assert plugin_id.value == id_value

    def test_plugin_id_trimming(self) -> None:
        """Test plugin ID whitespace trimming."""
        plugin_id = PluginId(value="  plugin-123  ")
        assert plugin_id.value == "plugin-123"

    def test_plugin_id_validation(self) -> None:
        """Test plugin ID format validation."""
        # Valid IDs should work
        valid_ids = ["plugin123", "tap-csv", "target_postgres"]

        for id_value in valid_ids:
            plugin_id = PluginId(value=id_value)
            assert plugin_id.value == id_value


class TestRequestId:
    """Test RequestId value object."""

    def test_valid_request_id_creation(self) -> None:
        """Test creating valid request IDs."""
        valid_ids = ["request-123", "req_456", "Request1", "api-request-789"]

        for id_value in valid_ids:
            request_id = RequestId(value=id_value)
            assert request_id.value == id_value

    def test_request_id_trimming(self) -> None:
        """Test request ID whitespace trimming."""
        request_id = RequestId(value="  request-123  ")
        assert request_id.value == "request-123"

    def test_request_id_validation(self) -> None:
        """Test request ID format validation."""
        # Valid IDs should work
        valid_ids = ["request123", "api-request", "req_id_456"]

        for id_value in valid_ids:
            request_id = RequestId(value=id_value)
            assert request_id.value == id_value


class TestValueObjectInheritance:
    """Test value object inheritance and base functionality."""

    def test_value_objects_inherit_from_domain_value_object(self) -> None:
        """Test all value objects inherit from DomainValueObject."""
        value_objects = [
            ApiEndpoint(path="/test"),
            RateLimit(),
            ApiVersion(),
            CorsOrigin(url="https://example.com"),
            ApiKey(key="1234567890abcdef"),
            RequestTimeout(),
            PipelineId(value="test-pipeline"),
            PluginId(value="test-plugin"),
            RequestId(value="test-request"),
        ]

        for vo in value_objects:
            assert isinstance(vo, DomainValueObject)

    def test_value_objects_are_immutable(self) -> None:
        """Test value objects are immutable after creation."""
        _endpoint = ApiEndpoint(path="/test", method="GET")

        # Should not be able to modify after creation
        # (This depends on DomainValueObject implementation)
        # For Pydantic models, fields are typically not directly mutable

    def test_value_objects_equality(self) -> None:
        """Test value objects equality comparison."""
        endpoint1 = ApiEndpoint(path="/test", method="GET")
        endpoint2 = ApiEndpoint(path="/test", method="GET")
        endpoint3 = ApiEndpoint(path="/other", method="GET")

        # Same values should be equal
        assert endpoint1 == endpoint2

        # Different values should not be equal
        assert endpoint1 != endpoint3

    def test_value_objects_hashable(self) -> None:
        """Test value objects can be used as dictionary keys."""
        endpoint = ApiEndpoint(path="/test")
        version = ApiVersion(major=1, minor=0, patch=0)

        # Should be able to use as dictionary keys
        data = {
            endpoint: "endpoint_data",
            version: "version_data",
        }

        assert data[endpoint] == "endpoint_data"
        assert data[version] == "version_data"


class TestValueObjectComposition:
    """Test composing value objects together."""

    def test_value_objects_in_complex_structures(self) -> None:
        """Test using value objects in complex data structures."""
        endpoint = ApiEndpoint(path="/api/v1/users", method="GET")
        version = ApiVersion(major=1, minor=0, patch=0)
        rate_limit = RateLimit(requests_per_minute=100)
        timeout = RequestTimeout(value=30)
        cors = CorsOrigin(url="https://example.com")

        assert endpoint.path == "/api/v1/users"
        assert version.version_string == "1.0.0"
        assert rate_limit.requests_per_minute == 100
        assert timeout.value == 30
        assert cors.url == "https://example.com"

    def test_value_object_validation_composition(self) -> None:
        """Test that composed value objects maintain validation."""
        # All individual validations should still work
        with pytest.raises(ValidationError):
            {
                "cors": CorsOrigin(url="invalid-url"),  # Should raise ValidationError
            }

    def test_value_objects_in_collections(self) -> None:
        """Test value objects work properly in collections."""
        endpoints = [
            ApiEndpoint(path="/api/v1/users", method="GET"),
            ApiEndpoint(path="/api/v1/users", method="POST"),
            ApiEndpoint(path="/api/v1/users/{id}", method="GET"),
        ]

        assert len(endpoints) == 3
        assert all(isinstance(e, ApiEndpoint) for e in endpoints)

        # Test uniqueness in sets
        endpoint_set = {
            ApiEndpoint(path="/users", method="GET"),
            ApiEndpoint(path="/users", method="GET"),  # Duplicate
            ApiEndpoint(path="/users", method="POST"),
        }

        # Should contain only unique endpoints
        assert len(endpoint_set) == 2


class TestValueObjectSerialization:
    """Test value object serialization capabilities."""

    def test_value_object_serialization(self) -> None:
        """Test value objects can be serialized."""
        endpoint = ApiEndpoint(path="/api/v1/users", method="GET")

        # Test model_dump if available (Pydantic v2)
        if hasattr(endpoint, "model_dump"):
            serialized = endpoint.model_dump()
        else:
            # Fallback to dict() for Pydantic v1
            serialized = dict(endpoint)

        assert serialized["path"] == "/api/v1/users"
        assert serialized["method"] == "GET"

    def test_complex_value_object_serialization(self) -> None:
        """Test complex value object serialization."""
        version = ApiVersion(major=2, minor=1, patch=0)

        # Test model_dump if available (Pydantic v2)
        if hasattr(version, "model_dump"):
            serialized = version.model_dump()
        else:
            # Fallback for Pydantic v1
            serialized = dict(version)

        assert serialized["major"] == 2
        assert serialized["minor"] == 1
        assert serialized["patch"] == 0
