"""Comprehensive tests for FLEXT API exceptions.

Tests all exception classes with 100% coverage including:
- All exception classes creation and inheritance
- Context parameters and message formatting
- Error codes and proper initialization
- Integration with flext-core exception hierarchy

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)

from flext_api.exceptions import (
    FlextApiAuthenticationError,
    FlextApiBuilderError,
    FlextApiConfigurationError,
    FlextApiConnectionError,
    FlextApiError,
    FlextApiProcessingError,
    FlextApiRequestError,
    FlextApiResponseError,
    FlextApiStorageError,
    FlextApiTimeoutError,
    FlextApiValidationError,
)


class TestFlextApiError:
    """Test base FlextApiError class."""

    def test_basic_creation(self) -> None:
        """Test basic FlextApiError creation."""
        error = FlextApiError("Test error")

        assert str(error) == "[FLEXT_API_ERROR] Test error"
        assert isinstance(error, FlextError)
        assert error.error_code == "FLEXT_API_ERROR"

    def test_creation_with_endpoint(self) -> None:
        """Test FlextApiError with endpoint context."""
        error = FlextApiError("Error occurred", endpoint="/api/users")

        assert str(error) == "[FLEXT_API_ERROR] Error occurred"
        assert error.context["endpoint"] == "/api/users"

    def test_creation_with_additional_context(self) -> None:
        """Test FlextApiError with additional context kwargs."""
        error = FlextApiError(
            "Error occurred",
            endpoint="/api/users",
            user_id=123,
            action="create",
        )

        assert str(error) == "[FLEXT_API_ERROR] Error occurred"
        assert error.context["endpoint"] == "/api/users"
        assert error.context["user_id"] == 123
        assert error.context["action"] == "create"

    def test_default_message(self) -> None:
        """Test FlextApiError with default message."""
        error = FlextApiError()

        assert str(error) == "[FLEXT_API_ERROR] flext_api error"
        assert error.error_code == "FLEXT_API_ERROR"


class TestFlextApiValidationError:
    """Test FlextApiValidationError class."""

    def test_basic_creation(self) -> None:
        """Test basic validation error creation."""
        error = FlextApiValidationError("Invalid input")

        assert str(error) == "[FLEXT_3001] Invalid input"
        assert isinstance(error, FlextValidationError)

    def test_creation_with_field_and_value(self) -> None:
        """Test validation error with field and value context."""
        error = FlextApiValidationError("Field must be positive", field="age", value=-5)

        assert str(error) == "[FLEXT_3001] Field must be positive"
        assert error.validation_details["field"] == "age"
        assert error.validation_details["value"] == "-5"

    def test_creation_with_endpoint(self) -> None:
        """Test validation error with endpoint context."""
        error = FlextApiValidationError(
            "Invalid data",
            field="email",
            value="invalid-email",
            endpoint="/api/users",
        )

        assert str(error) == "[FLEXT_3001] Invalid data"
        assert error.validation_details["field"] == "email"
        assert error.validation_details["value"] == "invalid-email"
        assert error.context["endpoint"] == "/api/users"

    def test_long_value_truncation(self) -> None:
        """Test validation error truncates long values."""
        long_value = "x" * 200
        error = FlextApiValidationError(
            "Value too long",
            field="description",
            value=long_value,
        )

        assert str(error) == "[FLEXT_3001] Value too long"
        assert error.validation_details["field"] == "description"
        assert len(error.validation_details["value"]) == 100
        assert error.validation_details["value"] == "x" * 100

    def test_default_message(self) -> None:
        """Test validation error with default message."""
        error = FlextApiValidationError()

        assert str(error) == "[FLEXT_3001] API validation failed"


class TestFlextApiAuthenticationError:
    """Test FlextApiAuthenticationError class."""

    def test_basic_creation(self) -> None:
        """Test basic authentication error creation."""
        error = FlextApiAuthenticationError("Login failed")

        assert str(error) == "[AUTH_ERROR] flext_api: Login failed"
        assert isinstance(error, FlextAuthenticationError)

    def test_creation_with_auth_method(self) -> None:
        """Test authentication error with auth method context."""
        error = FlextApiAuthenticationError("Invalid token", auth_method="Bearer")

        assert str(error) == "[AUTH_ERROR] flext_api: Invalid token"
        assert error.context["auth_method"] == "Bearer"

    def test_creation_with_endpoint(self) -> None:
        """Test authentication error with endpoint context."""
        error = FlextApiAuthenticationError(
            "Access denied",
            auth_method="API Key",
            endpoint="/api/REDACTED_LDAP_BIND_PASSWORD",
        )

        assert str(error) == "[AUTH_ERROR] flext_api: Access denied"
        assert error.context["auth_method"] == "API Key"
        assert error.context["endpoint"] == "/api/REDACTED_LDAP_BIND_PASSWORD"

    def test_default_message(self) -> None:
        """Test authentication error with default message."""
        error = FlextApiAuthenticationError()

        assert str(error) == "[AUTH_ERROR] flext_api: flext_api authentication failed"


class TestFlextApiConfigurationError:
    """Test FlextApiConfigurationError class."""

    def test_basic_creation(self) -> None:
        """Test basic configuration error creation."""
        error = FlextApiConfigurationError("Invalid config")

        assert str(error) == "[CONFIG_ERROR] Invalid config"
        assert isinstance(error, FlextConfigurationError)

    def test_creation_with_config_key(self) -> None:
        """Test configuration error with config key context."""
        error = FlextApiConfigurationError(
            "Missing required setting",
            config_key="api_secret",
        )

        assert str(error) == "[CONFIG_ERROR] Missing required setting"
        assert error.context["config_key"] == "api_secret"

    def test_creation_with_additional_context(self) -> None:
        """Test configuration error with additional context."""
        error = FlextApiConfigurationError(
            "Invalid port",
            config_key="api_port",
            expected_type="int",
            actual_value="invalid",
        )

        assert str(error) == "[CONFIG_ERROR] Invalid port"
        assert error.context["config_key"] == "api_port"
        assert error.context["expected_type"] == "int"
        assert error.context["actual_value"] == "invalid"

    def test_default_message(self) -> None:
        """Test configuration error with default message."""
        error = FlextApiConfigurationError()

        assert str(error) == "[CONFIG_ERROR] API configuration error"


class TestFlextApiConnectionError:
    """Test FlextApiConnectionError class."""

    def test_basic_creation(self) -> None:
        """Test basic connection error creation."""
        error = FlextApiConnectionError("Connection refused")

        assert str(error) == "[FLEXT_2001] Connection refused"
        assert isinstance(error, FlextConnectionError)

    def test_creation_with_host_and_port(self) -> None:
        """Test connection error with host and port context."""
        error = FlextApiConnectionError(
            "Cannot connect to server",
            host="api.example.com",
            port=443,
        )

        assert str(error) == "[FLEXT_2001] Cannot connect to server"
        assert error.context["host"] == "api.example.com"
        assert error.context["port"] == 443

    def test_creation_with_additional_context(self) -> None:
        """Test connection error with additional context."""
        error = FlextApiConnectionError(
            "SSL handshake failed",
            host="secure.api.com",
            port=443,
            ssl_error="Certificate verification failed",
        )

        assert str(error) == "[FLEXT_2001] SSL handshake failed"
        assert error.context["host"] == "secure.api.com"
        assert error.context["port"] == 443
        assert error.context["ssl_error"] == "Certificate verification failed"

    def test_default_message(self) -> None:
        """Test connection error with default message."""
        error = FlextApiConnectionError()

        assert str(error) == "[FLEXT_2001] API connection error"


class TestFlextApiProcessingError:
    """Test FlextApiProcessingError class."""

    def test_basic_creation(self) -> None:
        """Test basic processing error creation."""
        error = FlextApiProcessingError("Processing failed")

        assert str(error) == "[PROCESSING_ERROR] Processing failed"
        assert isinstance(error, FlextProcessingError)

    def test_creation_with_operation(self) -> None:
        """Test processing error with operation context."""
        error = FlextApiProcessingError(
            "Data transformation failed",
            operation="json_transform",
        )

        assert str(error) == "[PROCESSING_ERROR] Data transformation failed"
        assert error.context["operation"] == "json_transform"

    def test_creation_with_endpoint(self) -> None:
        """Test processing error with endpoint context."""
        error = FlextApiProcessingError(
            "Query execution failed",
            operation="database_query",
            endpoint="/api/reports",
        )

        assert str(error) == "[PROCESSING_ERROR] Query execution failed"
        assert error.context["operation"] == "database_query"
        assert error.context["endpoint"] == "/api/reports"

    def test_default_message(self) -> None:
        """Test processing error with default message."""
        error = FlextApiProcessingError()

        assert str(error) == "[PROCESSING_ERROR] API processing error"


class TestFlextApiTimeoutError:
    """Test FlextApiTimeoutError class."""

    def test_basic_creation(self) -> None:
        """Test basic timeout error creation."""
        error = FlextApiTimeoutError("Request timed out")

        assert str(error) == "[FLEXT_2002] Request timed out"
        assert isinstance(error, FlextTimeoutError)

    def test_creation_with_endpoint_and_timeout(self) -> None:
        """Test timeout error with endpoint and timeout context."""
        error = FlextApiTimeoutError(
            "Operation exceeded timeout",
            endpoint="/api/data/export",
            timeout_seconds=30.5,
        )

        assert str(error) == "[FLEXT_2002] Operation exceeded timeout"
        assert error.context["endpoint"] == "/api/data/export"
        assert error.context["timeout_seconds"] == 30.5

    def test_creation_with_additional_context(self) -> None:
        """Test timeout error with additional context."""
        error = FlextApiTimeoutError(
            "Database query timeout",
            endpoint="/api/search",
            timeout_seconds=15.0,
            query_type="complex_join",
        )

        assert str(error) == "[FLEXT_2002] Database query timeout"
        assert error.context["endpoint"] == "/api/search"
        assert error.context["timeout_seconds"] == 15.0
        assert error.context["query_type"] == "complex_join"

    def test_default_message(self) -> None:
        """Test timeout error with default message."""
        error = FlextApiTimeoutError()

        assert str(error) == "[FLEXT_2002] API timeout error"


class TestFlextApiRequestError:
    """Test FlextApiRequestError class."""

    def test_basic_creation(self) -> None:
        """Test basic request error creation."""
        error = FlextApiRequestError("Bad request")

        assert str(error) == "[FLEXT_API_ERROR] API request: Bad request"
        assert isinstance(error, FlextApiError)

    def test_creation_with_method_and_endpoint(self) -> None:
        """Test request error with method and endpoint context."""
        error = FlextApiRequestError(
            "Invalid request format",
            method="POST",
            endpoint="/api/users",
        )

        assert str(error) == "[FLEXT_API_ERROR] API request: Invalid request format"
        assert error.context["method"] == "POST"
        assert error.context["endpoint"] == "/api/users"

    def test_creation_with_status_code(self) -> None:
        """Test request error with status code context."""
        error = FlextApiRequestError(
            "Client error",
            method="GET",
            endpoint="/api/data",
            status_code=400,
        )

        assert str(error) == "[FLEXT_API_ERROR] API request: Client error"
        assert error.context["method"] == "GET"
        assert error.context["endpoint"] == "/api/data"
        assert error.context["status_code"] == 400

    def test_default_message(self) -> None:
        """Test request error with default message."""
        error = FlextApiRequestError()

        assert str(error) == "[FLEXT_API_ERROR] API request: API request error"


class TestFlextApiResponseError:
    """Test FlextApiResponseError class."""

    def test_basic_creation(self) -> None:
        """Test basic response error creation."""
        error = FlextApiResponseError("Invalid response")

        assert str(error) == "[FLEXT_API_ERROR] API response: Invalid response"
        assert isinstance(error, FlextApiError)

    def test_creation_with_status_code(self) -> None:
        """Test response error with status code context."""
        error = FlextApiResponseError("Server error", status_code=500)

        assert str(error) == "[FLEXT_API_ERROR] API response: Server error"
        assert error.context["status_code"] == 500

    def test_creation_with_response_body(self) -> None:
        """Test response error with response body context."""
        error = FlextApiResponseError(
            "Parse error",
            status_code=422,
            response_body='{"error": "validation failed"}',
        )

        assert str(error) == "[FLEXT_API_ERROR] API response: Parse error"
        assert error.context["status_code"] == 422
        assert error.context["response_body"] == '{"error": "validation failed"}'

    def test_long_response_body_truncation(self) -> None:
        """Test response error truncates long response bodies."""
        long_body = "x" * 300
        error = FlextApiResponseError("Large response error", response_body=long_body)

        assert str(error) == "[FLEXT_API_ERROR] API response: Large response error"
        assert len(error.context["response_body"]) == 200
        assert error.context["response_body"] == "x" * 200

    def test_default_message(self) -> None:
        """Test response error with default message."""
        error = FlextApiResponseError()

        assert str(error) == "[FLEXT_API_ERROR] API response: API response error"


class TestFlextApiStorageError:
    """Test FlextApiStorageError class."""

    def test_basic_creation(self) -> None:
        """Test basic storage error creation."""
        error = FlextApiStorageError("Storage failed")

        assert str(error) == "[FLEXT_API_ERROR] API storage: Storage failed"
        assert isinstance(error, FlextApiError)

    def test_creation_with_storage_type(self) -> None:
        """Test storage error with storage type context."""
        error = FlextApiStorageError("Write operation failed", storage_type="redis")

        assert str(error) == "[FLEXT_API_ERROR] API storage: Write operation failed"
        assert error.context["storage_type"] == "redis"

    def test_creation_with_operation(self) -> None:
        """Test storage error with operation context."""
        error = FlextApiStorageError(
            "Cache miss",
            storage_type="memcached",
            operation="get",
        )

        assert str(error) == "[FLEXT_API_ERROR] API storage: Cache miss"
        assert error.context["storage_type"] == "memcached"
        assert error.context["operation"] == "get"

    def test_creation_with_additional_context(self) -> None:
        """Test storage error with additional context."""
        error = FlextApiStorageError(
            "Connection pool exhausted",
            storage_type="postgresql",
            operation="connect",
            pool_size=10,
            active_connections=10,
        )

        assert str(error) == "[FLEXT_API_ERROR] API storage: Connection pool exhausted"
        assert error.context["storage_type"] == "postgresql"
        assert error.context["operation"] == "connect"
        assert error.context["pool_size"] == 10
        assert error.context["active_connections"] == 10

    def test_default_message(self) -> None:
        """Test storage error with default message."""
        error = FlextApiStorageError()

        assert str(error) == "[FLEXT_API_ERROR] API storage: API storage error"


class TestFlextApiBuilderError:
    """Test FlextApiBuilderError class."""

    def test_basic_creation(self) -> None:
        """Test basic builder error creation."""
        error = FlextApiBuilderError("Builder failed")

        assert str(error) == "[FLEXT_API_ERROR] API builder: Builder failed"
        assert isinstance(error, FlextApiError)

    def test_creation_with_builder_step(self) -> None:
        """Test builder error with builder step context."""
        error = FlextApiBuilderError(
            "Invalid query construction",
            builder_step="filter_validation",
        )

        assert str(error) == "[FLEXT_API_ERROR] API builder: Invalid query construction"
        assert error.context["builder_step"] == "filter_validation"

    def test_creation_with_additional_context(self) -> None:
        """Test builder error with additional context."""
        error = FlextApiBuilderError(
            "Response build failed",
            builder_step="pagination",
            expected_type="int",
            actual_value="invalid",
        )

        assert str(error) == "[FLEXT_API_ERROR] API builder: Response build failed"
        assert error.context["builder_step"] == "pagination"
        assert error.context["expected_type"] == "int"
        assert error.context["actual_value"] == "invalid"

    def test_default_message(self) -> None:
        """Test builder error with default message."""
        error = FlextApiBuilderError()

        assert str(error) == "[FLEXT_API_ERROR] API builder: API builder error"


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_flext_api_error_hierarchy(self) -> None:
        """Test FlextApiError inherits from FlextError."""
        error = FlextApiError("Test")

        assert isinstance(error, FlextError)
        assert isinstance(error, Exception)

    def test_all_specific_errors_inherit_from_correct_base(self) -> None:
        """Test all specific errors inherit from correct flext-core exceptions."""
        # Test inheritance chain
        validation_error = FlextApiValidationError("Test")
        assert isinstance(validation_error, FlextValidationError)
        assert isinstance(validation_error, FlextError)

        auth_error = FlextApiAuthenticationError("Test")
        assert isinstance(auth_error, FlextAuthenticationError)
        assert isinstance(auth_error, FlextError)

        config_error = FlextApiConfigurationError("Test")
        assert isinstance(config_error, FlextConfigurationError)
        assert isinstance(config_error, FlextError)

        connection_error = FlextApiConnectionError("Test")
        assert isinstance(connection_error, FlextConnectionError)
        assert isinstance(connection_error, FlextError)

        processing_error = FlextApiProcessingError("Test")
        assert isinstance(processing_error, FlextProcessingError)
        assert isinstance(processing_error, FlextError)

        timeout_error = FlextApiTimeoutError("Test")
        assert isinstance(timeout_error, FlextTimeoutError)
        assert isinstance(timeout_error, FlextError)

    def test_api_specific_errors_inherit_from_api_error(self) -> None:
        """Test API-specific errors inherit from FlextApiError."""
        request_error = FlextApiRequestError("Test")
        assert isinstance(request_error, FlextApiError)
        assert isinstance(request_error, FlextError)

        response_error = FlextApiResponseError("Test")
        assert isinstance(response_error, FlextApiError)
        assert isinstance(response_error, FlextError)

        storage_error = FlextApiStorageError("Test")
        assert isinstance(storage_error, FlextApiError)
        assert isinstance(storage_error, FlextError)

        builder_error = FlextApiBuilderError("Test")
        assert isinstance(builder_error, FlextApiError)
        assert isinstance(builder_error, FlextError)


class TestExceptionModuleExports:
    """Test module exports and __all__ completeness."""

    def test_all_exceptions_in_module_all(self) -> None:
        """Test all exception classes are in __all__ export."""
        from flext_api.exceptions import __all__

        expected_exports = {
            "FlextApiAuthenticationError",
            "FlextApiBuilderError",
            "FlextApiConfigurationError",
            "FlextApiConnectionError",
            "FlextApiError",
            "FlextApiProcessingError",
            "FlextApiRequestError",
            "FlextApiResponseError",
            "FlextApiStorageError",
            "FlextApiTimeoutError",
            "FlextApiValidationError",
        }

        assert set(__all__) == expected_exports

    def test_all_exports_importable(self) -> None:
        """Test all exported exceptions can be imported."""
        from flext_api.exceptions import (
            FlextApiAuthenticationError,
            FlextApiBuilderError,
            FlextApiConfigurationError,
            FlextApiConnectionError,
            FlextApiError,
            FlextApiProcessingError,
            FlextApiRequestError,
            FlextApiResponseError,
            FlextApiStorageError,
            FlextApiTimeoutError,
            FlextApiValidationError,
        )

        # Verify all are exception classes
        exception_classes = [
            FlextApiError,
            FlextApiValidationError,
            FlextApiAuthenticationError,
            FlextApiConfigurationError,
            FlextApiConnectionError,
            FlextApiProcessingError,
            FlextApiTimeoutError,
            FlextApiRequestError,
            FlextApiResponseError,
            FlextApiStorageError,
            FlextApiBuilderError,
        ]

        for exc_class in exception_classes:
            assert issubclass(exc_class, Exception)
            # Test each can be instantiated
            instance = exc_class("Test message")
            assert isinstance(instance, Exception)
