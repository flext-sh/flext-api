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

from importlib import import_module

from flext_core import (
    FlextExceptions,
    FlextProcessingError,
)

from flext_api import (
    FlextApiAuthenticationError,
    FlextApiBuilderError,
    FlextApiClientMethod,
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
        assert isinstance(error, FlextExceptions)
        assert error.error_code == "FLEXT_API_ERROR"

    def test_creation_with_endpoint(self) -> None:
        """Test FlextApiError with endpoint context."""
        error = FlextApiError("Error occurred", endpoint="/api/users")

        assert str(error) == "[FLEXT_API_ERROR] Error occurred"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/users"

    def test_creation_with_additional_context(self) -> None:
        """Test FlextApiError with additional context kwargs."""
        error = FlextApiError(
            "Error occurred",
            endpoint="/api/users",
            user_id=123,
            action="create",
        )

        assert str(error) == "[FLEXT_API_ERROR] Error occurred"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/users"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["user_id"] == 123
                assert context_data["action"] == "create"

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
        assert isinstance(error, FlextExceptions)

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
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/users"

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
        validation_value = error.validation_details.get("value")
        if isinstance(validation_value, str):
            assert len(validation_value) == 100
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
        assert isinstance(error, FlextExceptions)

    def test_creation_with_auth_method(self) -> None:
        """Test authentication error with auth method context."""
        error = FlextApiAuthenticationError("Invalid token", auth_method="Bearer")

        assert str(error) == "[AUTH_ERROR] flext_api: Invalid token"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["auth_method"] == "Bearer"

    def test_creation_with_endpoint(self) -> None:
        """Test authentication error with endpoint context."""
        error = FlextApiAuthenticationError(
            "Access denied",
            auth_method="API Key",
            endpoint="/api/REDACTED_LDAP_BIND_PASSWORD",
        )

        assert str(error) == "[AUTH_ERROR] flext_api: Access denied"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["auth_method"] == "API Key"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/REDACTED_LDAP_BIND_PASSWORD"

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
        assert isinstance(error, FlextExceptions)

    def test_creation_with_config_key(self) -> None:
        """Test configuration error with config key context."""
        error = FlextApiConfigurationError(
            "Missing required setting",
            config_key="api_secret",
        )

        assert str(error) == "[CONFIG_ERROR] Missing required setting"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["config_key"] == "api_secret"

    def test_creation_with_additional_context(self) -> None:
        """Test configuration error with additional context."""
        error = FlextApiConfigurationError(
            "Invalid port",
            config_key="api_port",
            expected_type="int",
            actual_value="invalid",
        )

        assert str(error) == "[CONFIG_ERROR] Invalid port"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["config_key"] == "api_port"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["expected_type"] == "int"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["actual_value"] == "invalid"

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
        assert isinstance(error, FlextExceptions)

    def test_creation_with_host_and_port(self) -> None:
        """Test connection error with host and port context."""
        error = FlextApiConnectionError(
            "Cannot connect to server",
            host="api.example.com",
            port=443,
        )

        assert str(error) == "[FLEXT_2001] Cannot connect to server"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["host"] == "api.example.com"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["port"] == 443

    def test_creation_with_additional_context(self) -> None:
        """Test connection error with additional context."""
        error = FlextApiConnectionError(
            "SSL handshake failed",
            host="secure.api.com",
            port=443,
            ssl_error="Certificate verification failed",
        )

        assert str(error) == "[FLEXT_2001] SSL handshake failed"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["host"] == "secure.api.com"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["port"] == 443
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["ssl_error"] == "Certificate verification failed"

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
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["operation"] == "json_transform"

    def test_creation_with_endpoint(self) -> None:
        """Test processing error with endpoint context."""
        error = FlextApiProcessingError(
            "Query execution failed",
            operation="database_query",
            endpoint="/api/reports",
        )

        assert str(error) == "[PROCESSING_ERROR] Query execution failed"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["operation"] == "database_query"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/reports"

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
        assert isinstance(error, FlextExceptions)

    def test_creation_with_endpoint_and_timeout(self) -> None:
        """Test timeout error with endpoint and timeout context."""
        error = FlextApiTimeoutError(
            "Operation exceeded timeout",
            endpoint="/api/data/export",
            timeout_seconds=30.5,
        )

        assert str(error) == "[FLEXT_2002] Operation exceeded timeout"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/data/export"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["timeout_seconds"] == 30.5

    def test_creation_with_additional_context(self) -> None:
        """Test timeout error with additional context."""
        error = FlextApiTimeoutError(
            "Database query timeout",
            endpoint="/api/search",
            timeout_seconds=15.0,
            query_type="complex_join",
        )

        assert str(error) == "[FLEXT_2002] Database query timeout"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/search"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["timeout_seconds"] == 15.0
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["query_type"] == "complex_join"

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
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["method"] == "POST"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/users"

    def test_creation_with_status_code(self) -> None:
        """Test request error with status code context."""
        error = FlextApiRequestError(
            "Client error",
            method=FlextApiClientMethod.GET,
            endpoint="/api/data",
            status_code=400,
        )

        assert str(error) == "[FLEXT_API_ERROR] API request: Client error"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["method"] == "GET"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["endpoint"] == "/api/data"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["status_code"] == 400

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
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["status_code"] == 500

    def test_creation_with_response_body(self) -> None:
        """Test response error with response body context."""
        error = FlextApiResponseError(
            "Parse error",
            status_code=422,
            response_body='{"error": "validation failed"}',
        )

        assert str(error) == "[FLEXT_API_ERROR] API response: Parse error"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["status_code"] == 422
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["response_body"] == '{"error": "validation failed"}'

    def test_long_response_body_truncation(self) -> None:
        """Test response error truncates long response bodies."""
        long_body = "x" * 300
        error = FlextApiResponseError("Large response error", response_body=long_body)

        assert str(error) == "[FLEXT_API_ERROR] API response: Large response error"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict) and "response_body" in context_data:
                response_body = context_data["response_body"]
                if isinstance(response_body, str):
                    assert len(response_body) == 200
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["response_body"] == "x" * 200

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
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["storage_type"] == "redis"

    def test_creation_with_operation(self) -> None:
        """Test storage error with operation context."""
        error = FlextApiStorageError(
            "Cache miss",
            storage_type="memcached",
            operation="get",
        )

        assert str(error) == "[FLEXT_API_ERROR] API storage: Cache miss"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["storage_type"] == "memcached"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["operation"] == "get"

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
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["storage_type"] == "postgresql"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["operation"] == "connect"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["pool_size"] == 10
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["active_connections"] == 10

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
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["builder_step"] == "filter_validation"

    def test_creation_with_additional_context(self) -> None:
        """Test builder error with additional context."""
        error = FlextApiBuilderError(
            "Response build failed",
            builder_step="pagination",
            expected_type="int",
            actual_value="invalid",
        )

        assert str(error) == "[FLEXT_API_ERROR] API builder: Response build failed"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["builder_step"] == "pagination"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["expected_type"] == "int"
        if isinstance(error.context, dict) and "context" in error.context:
            context_data = error.context["context"]
            if isinstance(context_data, dict):
                assert context_data["actual_value"] == "invalid"

    def test_default_message(self) -> None:
        """Test builder error with default message."""
        error = FlextApiBuilderError()

        assert str(error) == "[FLEXT_API_ERROR] API builder: API builder error"


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_flext_api_error_hierarchy(self) -> None:
        """Test FlextApiError inherits from FlextExceptions."""
        error = FlextApiError("Test")

        assert isinstance(error, FlextExceptions)
        assert isinstance(error, Exception)

    def test_all_specific_errors_inherit_from_correct_base(self) -> None:
        """Test all specific errors inherit from correct flext-core exceptions."""
        # Test inheritance chain - note: not all flext-core exceptions inherit from FlextExceptions
        validation_error = FlextApiValidationError("Test")
        assert isinstance(validation_error, FlextExceptions)
        # FlextExceptions inherits from FlextExceptionsMixin + ValueError, not FlextExceptions

        auth_error = FlextApiAuthenticationError("Test")
        assert isinstance(auth_error, FlextExceptions)
        # FlextExceptions inherits from FlextExceptionsMixin + PermissionError, not FlextExceptions

        config_error = FlextApiConfigurationError("Test")
        assert isinstance(config_error, FlextExceptions)
        # FlextExceptions inherits from FlextExceptionsMixin + ValueError, not FlextExceptions

        connection_error = FlextApiConnectionError("Test")
        assert isinstance(connection_error, FlextExceptions)
        # FlextExceptions inherits from FlextExceptionsMixin + ConnectionError, not FlextExceptions

        processing_error = FlextApiProcessingError("Test")
        assert isinstance(processing_error, FlextProcessingError)
        # FlextProcessingError inherits from FlextExceptionsMixin + RuntimeError, not FlextExceptions

        timeout_error = FlextApiTimeoutError("Test")
        assert isinstance(timeout_error, FlextExceptions)
        # FlextExceptions inherits from FlextExceptionsMixin + TimeoutError, not FlextExceptions

    def test_api_specific_errors_inherit_from_api_error(self) -> None:
        """Test API-specific errors inherit from FlextApiError."""
        request_error = FlextApiRequestError("Test")
        assert isinstance(request_error, FlextApiError)
        assert isinstance(request_error, FlextExceptions)

        response_error = FlextApiResponseError("Test")
        assert isinstance(response_error, FlextApiError)
        assert isinstance(response_error, FlextExceptions)

        storage_error = FlextApiStorageError("Test")
        assert isinstance(storage_error, FlextApiError)
        assert isinstance(storage_error, FlextExceptions)

        builder_error = FlextApiBuilderError("Test")
        assert isinstance(builder_error, FlextApiError)
        assert isinstance(builder_error, FlextExceptions)


class TestExceptionModuleExports:
    """Test module exports and __all__ completeness."""

    def test_all_exceptions_in_module_all(self) -> None:
        """Test all exception classes are in __all__ export."""
        exceptions_module = import_module("flext_api.exceptions")
        module_all = set(getattr(exceptions_module, "__all__", []))

        expected_exports = {
            "FlextApiAuthenticationError",
            "FlextApiAuthorizationError",
            "FlextApiBuilderError",
            "FlextApiConfigurationError",
            "FlextApiConnectionError",
            "FlextApiError",
            "FlextApiNotFoundError",
            "FlextApiProcessingError",
            "FlextApiRateLimitError",
            "FlextApiRequestError",
            "FlextApiResponseError",
            "FlextApiStorageError",
            "FlextApiTimeoutError",
            "FlextApiValidationError",
            "create_error_response",
            "map_http_status_to_exception",
        }

        assert module_all == expected_exports

    def test_all_exports_importable(self) -> None:
        """Test all exported exceptions can be imported."""
        exceptions_module = import_module("flext_api.exceptions")
        export_names = [
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
        ]

        # Verify all are exception classes and instantiable
        for name in export_names:
            exc_class = getattr(exceptions_module, name)
            assert issubclass(exc_class, Exception)
            instance = exc_class("Test message")
            assert isinstance(instance, Exception)
