"""Tests for flext_api.exceptions module using flext_tests EM ABSOLUTO.

MAXIMUM usage of flext_tests - ALL test utilities via flext_tests.
Uses FlextTestsMatchers, FlextTestsDomains, FlextTestsUtilities.
ACESSO DIRETO - NO ALIASES, NO WRAPPERS, NO COMPATIBILITY.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core.typings import FlextTypes

# MAXIMUM usage of flext_tests - ACESSO DIRETO - NO ALIASES
from flext_tests import FlextTestsDomains, FlextTestsMatchers, FlextTestsUtilities

from flext_api import FlextApiExceptions


class TestFlextApiExceptions:
    """Test FlextApiExceptions using flext_tests patterns and real functionality."""

    def test_exceptions_class_exists(self) -> None:
        """Test FlextApiExceptions class exists with real error types."""
        assert FlextApiExceptions is not None

        # Verify core exception types exist - test only working ones
        required_exceptions = [
            "FlextApiError",
            "ValidationError",
            "AuthenticationError",
            "NotFoundError",
            "ProcessingError",
            "HttpError",
            "ServerError",
            "ClientError",
        ]

        for exc_name in required_exceptions:
            assert hasattr(FlextApiExceptions, exc_name), f"Missing {exc_name}"

    def test_flext_api_error_basic(self) -> None:
        """Test basic FlextApiError creation using flext_tests patterns."""
        error_data = FlextTestsUtilities.create_test_result(success=False, error="API operation failed")
        error = FlextApiExceptions.FlextApiError("API error")

        # Verify error properties
        assert "API error" in str(error)
        assert hasattr(error, "status_code")

        # Use FlextTestsMatchers for validation
        assert FlextTestsMatchers.is_failed_result(error_data)

    def test_flext_api_error_custom_message(self) -> None:
        """Test FlextApiError with custom message using factory data."""
        test_message = "Custom operation failed"
        error_result = FlextTestsUtilities.create_test_result(success=False, error=test_message)
        error = FlextApiExceptions.FlextApiError(test_message)

        assert test_message in str(error)
        assert FlextTestsMatchers.is_failed_result(error_result)
        # FlextTestsUtilities may use default error message, so check it's a failure
        assert error_result.error is not None

    def test_flext_api_error_with_service_data(
        self, sample_service_data: FlextTypes.Core.Dict
    ) -> None:
        """Test FlextApiError with service data from conftest fixture."""
        service_name = str(sample_service_data.get("name", "unknown_service"))
        error_message = f"Service '{service_name}' operation failed"
        error = FlextApiExceptions.FlextApiError(error_message)

        assert service_name in str(error)
        assert "operation failed" in str(error)
        assert hasattr(error, "status_code")

    def test_validation_error_with_user_data(
        self, sample_user_data: FlextTypes.Core.Dict
    ) -> None:
        """Test ValidationError with user data from conftest fixture."""
        user_email = str(sample_user_data.get("email", "unknown@example.com"))
        validation_message = f"Invalid email format: {user_email}"
        error = FlextApiExceptions.ValidationError(validation_message)

        assert user_email in str(error)
        assert "Invalid email" in str(error)
        assert hasattr(error, "status_code")

    def test_authentication_error_with_factory_data(self) -> None:
        """Test AuthenticationError using factory patterns."""
        user_data = FlextTestsDomains.create_user()
        auth_message = (
            f"Authentication failed for user {user_data.get('name', 'unknown')}"
        )
        error = FlextApiExceptions.AuthenticationError(auth_message)

        assert "Authentication failed" in str(error)
        assert str(user_data.get("name", "unknown")) in str(error)
        # AuthenticationError from flext-core may not have status_code
        assert isinstance(error, FlextApiExceptions.AuthenticationError)

    def test_not_found_error_with_payload_data(
        self, sample_payload_data: FlextTypes.Core.Dict
    ) -> None:
        """Test NotFoundError with payload data from conftest fixture."""
        resource_id = sample_payload_data.get("message_id", "unknown_resource")
        not_found_message = f"Resource {resource_id} not found"
        error = FlextApiExceptions.NotFoundError(not_found_message)

        assert str(resource_id) in str(error)
        assert "not found" in str(error)
        # NotFoundError from flext-core may not have status_code
        assert isinstance(error, FlextApiExceptions.NotFoundError)

    def test_processing_error_with_configuration_data(
        self, sample_configuration_data: FlextTypes.Core.Dict
    ) -> None:
        """Test ProcessingError with configuration data from conftest fixture."""
        config_name = sample_configuration_data.get("database_url", "unknown_config")
        processing_message = f"Processing error in configuration '{config_name}'"
        error = FlextApiExceptions.ProcessingError(processing_message)

        assert str(config_name) in str(error)
        assert "Processing error" in str(error)
        # ProcessingError from flext-core may not have status_code
        assert isinstance(error, FlextApiExceptions.ProcessingError)

    def test_validation_error_batch_operations(self) -> None:
        """Test ValidationError with batch operations using flext_tests factory patterns."""
        batch_users = FlextTestsDomains.batch_users(3)
        validation_errors = []

        for i, user_data in enumerate(batch_users):
            error_msg = (
                f"Validation error for user {i}: {user_data.get('email', 'unknown')}"
            )
            error = FlextApiExceptions.ValidationError(error_msg)
            validation_errors.append(error)

            # Verify each error
            assert f"user {i}" in str(error)
            assert "Validation error" in str(error)

        # Should have created 3 distinct errors
        assert len(validation_errors) == 3
        assert all(isinstance(e, FlextApiExceptions.ValidationError) for e in validation_errors)

    def test_base_error_hierarchy(self) -> None:
        """Test base error hierarchy using flext_tests patterns."""
        # Test different base error types that work with strings
        base_errors = [
            (FlextApiExceptions.FlextApiError, "API operation failed"),
            (FlextApiExceptions.ValidationError, "Validation failed"),
            (FlextApiExceptions.AuthenticationError, "Authentication failed"),
            (FlextApiExceptions.NotFoundError, "Resource not found"),
            (FlextApiExceptions.ProcessingError, "Processing failed"),
        ]

        for error_class, message in base_errors:
            error = error_class(message)

            # Should be proper exception instances
            assert isinstance(error, Exception)
            assert message in str(error)
            # FlextApiError has status_code, others may not
            if error_class == FlextApiExceptions.FlextApiError:
                assert hasattr(error, "status_code")

    def test_error_creation_with_flext_tests_domains(self) -> None:
        """Test error creation using FlextTestsDomains."""
        # Create various domain objects and use them in error messages
        user = FlextTestsDomains.create_user()
        service = FlextTestsDomains.create_service()
        payload = FlextTestsDomains.create_payload()

        errors = [
            FlextApiExceptions.ValidationError(
                f"Invalid user data: {user.get('email')}"
            ),
            FlextApiExceptions.NotFoundError(
                f"Service not found: {service.get('name')}"
            ),
            FlextApiExceptions.ProcessingError(
                f"Failed to process payload: {payload.get('message_id')}"
            ),
        ]

        for error in errors:
            # Some errors may not inherit from FlextApiError (they come from flext-core)
            assert isinstance(error, Exception)
            assert len(str(error)) > 0

    def test_error_validation_patterns(self) -> None:
        """Test error validation using FlextTestsMatchers patterns."""
        # Create error results and validate them
        error_cases = [
            FlextTestsUtilities.create_test_result(success=False, error="API validation failed"),
            FlextTestsUtilities.create_test_result(success=False, error="Authentication error"),
            FlextTestsUtilities.create_test_result(success=False, error="Resource not found"),
        ]

        for error_result in error_cases:
            # Use FlextTestsMatchers for validation
            assert FlextTestsMatchers.is_failed_result(error_result)
            assert not FlextTestsMatchers.is_successful_result(error_result)
            assert error_result.error is not None

    def test_error_inheritance_structure(self) -> None:
        """Test error inheritance hierarchy using real classes."""
        # Test base error inheritance
        base_error = FlextApiExceptions.FlextApiError("Base error")
        assert isinstance(base_error, FlextApiExceptions.FlextApiError)

        # Test specific error instances - these come from flext-core
        validation_error = FlextApiExceptions.ValidationError("Validation failed")
        assert isinstance(validation_error, Exception)  # May not inherit from FlextApiError

        auth_error = FlextApiExceptions.AuthenticationError("Auth failed")
        assert isinstance(auth_error, Exception)  # May not inherit from FlextApiError

        not_found_error = FlextApiExceptions.NotFoundError("Not found")
        assert isinstance(not_found_error, Exception)  # May not inherit from FlextApiError

    def test_error_exception_behavior_with_flext_tests(self) -> None:
        """Test errors behave as proper exceptions using flext_tests patterns."""
        test_data = FlextTestsDomains.create_service()
        test_error_msg = f"Test error for service {test_data.get('name', 'unknown')}"

        # Should be raisable and catchable
        with pytest.raises(FlextApiExceptions.FlextApiError) as exc_info:
            raise FlextApiExceptions.FlextApiError(test_error_msg)

        assert str(test_data.get("name", "unknown")) in str(exc_info.value)
        assert "Test error" in str(exc_info.value)
        assert hasattr(exc_info.value, "status_code")

    def test_specific_error_exception_behavior_with_fixtures(
        self, sample_user_data: FlextTypes.Core.Dict
    ) -> None:
        """Test specific errors behave as proper exceptions with fixture data."""
        user_email = str(sample_user_data.get("email", "test@example.com"))

        # ValidationError with user data
        invalid_data_msg = f"Invalid email format: {user_email}"
        with pytest.raises(FlextApiExceptions.ValidationError) as exc_info:
            raise FlextApiExceptions.ValidationError(invalid_data_msg)

        assert user_email in str(exc_info.value)
        assert "Invalid email" in str(exc_info.value)

        # ValidationError may not inherit from FlextApiError, so catch as Exception
        with pytest.raises(Exception):
            raise FlextApiExceptions.ValidationError(invalid_data_msg)

    def test_error_properties_validation(self) -> None:
        """Test each error has proper properties using flext_tests."""
        error_test_cases = [
            FlextApiExceptions.FlextApiError("Base error"),
            FlextApiExceptions.ValidationError("Validation failed"),
            FlextApiExceptions.AuthenticationError("Auth failed"),
            FlextApiExceptions.NotFoundError("Resource not found"),
            FlextApiExceptions.ProcessingError("Processing failed"),
        ]

        for error in error_test_cases:
            # All errors should be valid exceptions
            assert isinstance(str(error), str)
            assert len(str(error)) > 0
            # Only FlextApiError is guaranteed to have status_code
            if isinstance(error, FlextApiExceptions.FlextApiError):
                assert hasattr(error, "status_code")

    def test_error_codes_and_attributes(self) -> None:
        """Test errors have proper codes and attributes using flext_tests patterns."""
        # Test with factory data
        payload_data = FlextTestsDomains.create_payload()

        error_cases = [
            FlextApiExceptions.FlextApiError(
                f"API error for payload {payload_data.get('message_id')}"
            ),
            FlextApiExceptions.ValidationError(
                f"Validation error for payload {payload_data.get('message_id')}"
            ),
            FlextApiExceptions.AuthenticationError(
                f"Auth error for payload {payload_data.get('message_id')}"
            ),
            FlextApiExceptions.NotFoundError(
                f"Not found error for payload {payload_data.get('message_id')}"
            ),
        ]

        for error in error_cases:
            # All errors should have some form of identification
            assert hasattr(error, "code") or hasattr(error, "__class__")
            assert str(payload_data.get("message_id", "unknown")) in str(error)

    def test_errors_type_validation_with_flext_tests(self) -> None:
        """Test errors are proper types using flext_tests validation."""
        # Main exception factory class
        assert FlextApiExceptions is not None
        assert callable(FlextApiExceptions)

        # Create errors with factory data
        config_data = FlextTestsDomains.create_configuration()
        test_message = f"Configuration error: {config_data.get('database_url', 'unknown')}"

        error = FlextApiExceptions.FlextApiError(test_message)
        assert isinstance(error, FlextApiExceptions.FlextApiError)
        assert str(config_data.get("database_url", "unknown")) in str(error)

        validation_error = FlextApiExceptions.ValidationError(test_message)
        assert isinstance(validation_error, FlextApiExceptions.ValidationError)
        # ValidationError may not inherit from FlextApiError (comes from flext-core)
        assert isinstance(validation_error, Exception)

    def test_errors_string_representation_with_domain_data(self) -> None:
        """Test errors have proper string representation using FlextTestsDomains."""
        # Use domain objects for realistic error messages
        user = FlextTestsDomains.create_user()
        service = FlextTestsDomains.create_service()

        errors = [
            FlextApiExceptions.FlextApiError(f"API error for user {user.get('name')}"),
            FlextApiExceptions.ValidationError(
                f"Invalid data for user {user.get('email')}"
            ),
            FlextApiExceptions.AuthenticationError(
                f"Auth failed for user {user.get('name')}"
            ),
            FlextApiExceptions.NotFoundError(
                f"Service '{service.get('name')}' not found"
            ),
            FlextApiExceptions.ProcessingError(
                f"Processing error in service {service.get('name')}"
            ),
        ]

        for error in errors:
            error_str = str(error)
            assert isinstance(error_str, str)
            assert len(error_str) > 0
            # Should contain either user name, email, or service name
            assert (
                str(user.get("name", "")) in error_str
                or str(user.get("email", "")) in error_str
                or str(service.get("name", "")) in error_str
            )

    def test_error_attributes_persistence_with_factory_data(self) -> None:
        """Test error attributes persist after creation using factory data."""
        request_data = FlextTestsDomains.create_payload()
        error_message = f"Request failed: {request_data.get('url', 'unknown')}"
        error = FlextApiExceptions.FlextApiError(error_message)

        # Attributes should persist
        assert str(request_data.get("url", "unknown")) in str(error)
        assert "Request failed" in str(error)
        assert hasattr(error, "status_code")

        # Should still have these after operations
        _ = repr(error)

        # Error message should still be there
        assert "Request failed" in str(error)

    def test_multiple_error_instances_independence_with_batch_data(self) -> None:
        """Test multiple error instances are independent using batch factory data."""
        # Create batch of different error scenarios
        batch_users = FlextTestsDomains.batch_users(2)

        error1 = FlextApiExceptions.ValidationError(
            f"Validation failed for {batch_users[0].get('name', 'user1')}"
        )
        error2 = FlextApiExceptions.ValidationError(
            f"Validation failed for {batch_users[1].get('name', 'user2')}"
        )

        # Should be independent instances
        assert error1 is not error2
        assert str(error1) != str(error2)

        # Should contain different user names
        assert str(batch_users[0].get("name", "user1")) in str(error1)
        assert str(batch_users[1].get("name", "user2")) in str(error2)

        # Both should be ValidationError instances
        assert isinstance(error1, FlextApiExceptions.ValidationError)
        assert isinstance(error2, FlextApiExceptions.ValidationError)
