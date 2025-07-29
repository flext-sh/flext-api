#!/usr/bin/env python3
"""Test FlextApi Reducers - Validate real boilerplate reduction functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive tests for all reducer helpers - zero mocks, real validation.
"""

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from flext_api.helpers.flext_api_reducers import (
    FlextApiOperationTracker,
    FlextApiPagination,
    fleft_api_validate_non_empty_string,
    flext_api_build_error,
    flext_api_build_success,
    flext_api_build_validation_error,
    flext_api_create_operation_tracker,
    flext_api_create_standard_request,
    flext_api_ensure_directory,
    flext_api_ensure_types,
    flext_api_extract_fields,
    flext_api_filter_none_values,
    flext_api_gather_results,
    flext_api_read_json_safe,
    flext_api_rename_fields,
    flext_api_timeout_all,
    flext_api_validate_email_simple,
    flext_api_validate_field_types,
    flext_api_validate_required_fields,
    flext_api_write_json_safe,
)


class TestResponseBuilders:
    """Test response builder functions for real boilerplate reduction."""

    def test_build_success(self) -> None:
        """Test success response builder with actual data."""
        data = {"user_id": 123, "name": "test_user"}
        response = flext_api_build_success(data, "User created successfully")

        assert response["success"] is True
        assert response["data"] == data
        assert response["message"] == "User created successfully"
        assert response["status"] == 200
        assert "timestamp" in response
        assert datetime.fromisoformat(response["timestamp"])  # Valid timestamp

    def test_build_error(self) -> None:
        """Test error response builder with actual error cases."""
        response = flext_api_build_error("Validation failed", 422, {"field": "email"})

        assert response["success"] is False
        assert response["data"] == {"field": "email"}
        assert response["message"] == "Validation failed"
        assert response["status"] == 422
        assert "timestamp" in response

    def test_build_validation_error(self) -> None:
        """Test validation error builder with real validation scenario."""
        response = flext_api_build_validation_error(
            "email",
            "invalid-email",
            "Invalid format",
        )

        assert response["success"] is False
        assert response["status"] == 422
        assert "Validation failed for field 'email'" in response["message"]
        assert response["data"]["field"] == "email"
        assert response["data"]["value"] == "invalid-email"
        assert response["data"]["reason"] == "Invalid format"


class TestDataTransformation:
    """Test data transformation helpers for real world scenarios."""

    def test_extract_fields(self) -> None:
        """Test field extraction with real API response data."""
        api_response = {
            "user_id": 123,
            "name": "John Doe",
            "email": "john@example.com",
            "metadata": {"created_at": "2025-01-01"},
            "sensitive_data": "should_not_be_included",
        }

        extracted = flext_api_extract_fields(api_response, "user_id", "name", "email")

        assert len(extracted) == 3
        assert extracted["user_id"] == 123
        assert extracted["name"] == "John Doe"
        assert extracted["email"] == "john@example.com"
        assert "sensitive_data" not in extracted

    def test_rename_fields(self) -> None:
        """Test field renaming for API response transformation."""
        response_data = {
            "id": 123,
            "full_name": "John Doe",
            "email_address": "john@example.com",
        }

        mapping = {"id": "user_id", "full_name": "name", "email_address": "email"}

        renamed = flext_api_rename_fields(response_data, mapping)

        assert renamed["user_id"] == 123
        assert renamed["name"] == "John Doe"
        assert renamed["email"] == "john@example.com"
        assert "id" not in renamed
        assert "full_name" not in renamed

    def test_filter_none_values(self) -> None:
        """Test None value filtering for clean API responses."""
        messy_data = {
            "name": "John",
            "email": None,
            "age": 30,
            "phone": None,
            "address": "123 Main St",
        }

        cleaned = flext_api_filter_none_values(messy_data)

        assert len(cleaned) == 3
        assert cleaned["name"] == "John"
        assert cleaned["age"] == 30
        assert cleaned["address"] == "123 Main St"
        assert "email" not in cleaned
        assert "phone" not in cleaned

    def test_ensure_types(self) -> None:
        """Test type conversion for incoming API data."""
        incoming_data = {
            "user_id": "123",  # String from JSON
            "active": "true",  # String boolean
            "age": "30",  # String number
            "score": "95.5",  # String float
        }

        type_mapping = {"user_id": int, "active": bool, "age": int, "score": float}

        converted = flext_api_ensure_types(incoming_data, type_mapping)

        assert converted["user_id"] == 123
        assert converted["active"] is True
        assert converted["age"] == 30
        assert converted["score"] == 95.5

    def test_ensure_types_with_invalid_data(self) -> None:
        """Test type conversion with invalid data - should not crash."""
        invalid_data = {"age": "not_a_number", "score": "invalid_float"}

        type_mapping = {"age": int, "score": float}

        # Should not raise exception, just log warning
        converted = flext_api_ensure_types(invalid_data, type_mapping)

        # Original values preserved when conversion fails
        assert converted["age"] == "not_a_number"
        assert converted["score"] == "invalid_float"


class TestAsyncUtilities:
    """Test async utilities for real concurrent scenarios."""

    @pytest.mark.asyncio
    async def test_gather_results_with_mixed_operations(self) -> None:
        """Test gathering mixed sync/async operations with real functions."""

        async def async_operation(value: int) -> int:
            await asyncio.sleep(0.01)  # Simulate async work
            return value * 2

        def sync_operation(value: int) -> int:
            return value + 10

        def failing_operation() -> int:
            msg = "Operation failed"
            raise ValueError(msg)

        operations = [
            ("double_5", async_operation, (5,), {}),
            ("add_10_to_3", sync_operation, (3,), {}),
            ("will_fail", failing_operation, (), {}),
            ("double_10", async_operation, (10,), {}),
        ]

        results = await flext_api_gather_results(operations)

        assert len(results) == 4
        assert results["double_5"].is_success
        assert results["double_5"].data == 10
        assert results["add_10_to_3"].is_success
        assert results["add_10_to_3"].data == 13
        assert results["will_fail"].is_failure
        assert "Operation failed" in results["will_fail"].error
        assert results["double_10"].is_success
        assert results["double_10"].data == 20

    @pytest.mark.asyncio
    async def test_timeout_all_operations(self) -> None:
        """Test timeout functionality with real operations."""

        async def fast_operation() -> str:
            await asyncio.sleep(0.01)
            return "fast_result"

        async def slow_operation() -> str:
            await asyncio.sleep(1.0)  # Will timeout
            return "slow_result"

        def sync_operation() -> str:
            return "sync_result"

        operations = [fast_operation, slow_operation, sync_operation]
        results = await flext_api_timeout_all(operations, timeout=0.1)

        assert len(results) == 3
        assert results[0].is_success
        assert results[0].data == "fast_result"
        assert results[1].is_failure
        assert "timed out" in results[1].error
        assert results[2].is_success
        assert results[2].data == "sync_result"


class TestFileOperations:
    """Test file operation helpers for real file handling scenarios."""

    def test_read_json_safe_existing_file(self) -> None:
        """Test JSON reading with real file."""
        test_data = {"name": "test", "value": 42}

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            result = flext_api_read_json_safe(temp_path)

            assert result.is_success
            assert result.data == test_data
        finally:
            Path(temp_path).unlink()

    def test_read_json_safe_nonexistent_file_with_default(self) -> None:
        """Test JSON reading with nonexistent file and default value."""
        default_data = {"default": True}
        result = flext_api_read_json_safe("/nonexistent/file.json", default_data)

        assert result.is_success
        assert result.data == default_data

    def test_read_json_safe_invalid_json(self) -> None:
        """Test JSON reading with invalid JSON content."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json content")
            temp_path = f.name

        try:
            result = flext_api_read_json_safe(temp_path)

            assert result.is_failure
            assert "Invalid JSON" in result.error
        finally:
            Path(temp_path).unlink()

    def test_write_json_safe(self) -> None:
        """Test JSON writing with real data."""
        test_data = {"users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]}

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            result = flext_api_write_json_safe(temp_path, test_data)

            assert result.is_success
            assert result.data is True

            # Verify file was written correctly
            with open(temp_path, encoding="utf-8") as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data
        finally:
            Path(temp_path).unlink()

    def test_ensure_directory(self) -> None:
        """Test directory creation with nested paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "level1" / "level2" / "level3"

            result = flext_api_ensure_directory(nested_path)

            assert result.is_success
            assert result.data == nested_path
            assert nested_path.exists()
            assert nested_path.is_dir()


class TestValidationHelpers:
    """Test validation helpers for real input validation scenarios."""

    def test_validate_required_fields_success(self) -> None:
        """Test required field validation with complete data."""
        user_data = {"name": "John Doe", "email": "john@example.com", "age": 30}

        result = flext_api_validate_required_fields(user_data, "name", "email", "age")

        assert result.is_success
        assert result.data is True

    def test_validate_required_fields_missing(self) -> None:
        """Test required field validation with missing fields."""
        incomplete_data = {
            "name": "John Doe",
            "age": 30,
            # Missing email
        }

        result = flext_api_validate_required_fields(
            incomplete_data,
            "name",
            "email",
            "age",
        )

        assert result.is_failure
        assert "Missing required fields: email" in result.error

    def test_validate_required_fields_none_values(self) -> None:
        """Test required field validation with None values."""
        data_with_none = {"name": "John Doe", "email": None, "age": 30}

        result = flext_api_validate_required_fields(
            data_with_none,
            "name",
            "email",
            "age",
        )

        assert result.is_failure
        assert "Missing required fields: email" in result.error

    def test_validate_field_types_success(self) -> None:
        """Test field type validation with correct types."""
        typed_data = {"name": "John Doe", "age": 30, "active": True, "score": 95.5}

        type_mapping = {"name": str, "age": int, "active": bool, "score": float}

        result = flext_api_validate_field_types(typed_data, type_mapping)

        assert result.is_success
        assert result.data is True

    def test_validate_field_types_failure(self) -> None:
        """Test field type validation with incorrect types."""
        wrong_typed_data = {
            "name": 123,  # Should be str
            "age": "thirty",  # Should be int
            "active": "yes",  # Should be bool
        }

        type_mapping = {"name": str, "age": int, "active": bool}

        result = flext_api_validate_field_types(wrong_typed_data, type_mapping)

        assert result.is_failure
        assert "Field 'name' must be str" in result.error
        assert "Field 'age' must be int" in result.error
        assert "Field 'active' must be bool" in result.error

    def test_validate_email_simple(self) -> None:
        """Test simple email validation with real email formats."""
        # Valid emails
        assert flext_api_validate_email_simple("user@example.com") is True
        assert flext_api_validate_email_simple("test.email+tag@domain.co.uk") is True
        assert flext_api_validate_email_simple("user123@test-domain.org") is True

        # Invalid emails
        assert flext_api_validate_email_simple("invalid-email") is False
        assert flext_api_validate_email_simple("@domain.com") is False
        assert flext_api_validate_email_simple("user@") is False
        assert flext_api_validate_email_simple("user@domain") is False
        assert flext_api_validate_email_simple("") is False

    def test_validate_non_empty_string(self) -> None:
        """Test non-empty string validation with real string cases."""
        # Valid strings
        assert fleft_api_validate_non_empty_string("hello") is True
        assert fleft_api_validate_non_empty_string("  valid with spaces  ") is True

        # Invalid strings
        assert fleft_api_validate_non_empty_string("") is False
        assert fleft_api_validate_non_empty_string("   ") is False  # Only whitespace
        assert fleft_api_validate_non_empty_string(None) is False
        assert fleft_api_validate_non_empty_string(123) is False  # Not a string


class TestOperationTracker:
    """Test operation tracking for real workflow monitoring."""

    def test_operation_lifecycle(self) -> None:
        """Test complete operation lifecycle."""
        tracker = flext_api_create_operation_tracker()

        # Start operation
        operation_id = "user_creation_001"
        tracker.flext_api_start_operation(operation_id, "create_user")

        # Check started operation
        operation = tracker.flext_api_get_operation(operation_id)
        assert operation is not None
        assert operation["operation_id"] == operation_id
        assert operation["operation_type"] == "create_user"
        assert operation["status"] == "running"
        assert operation["completed_at"] is None
        assert operation["result"] is None
        assert operation["error"] is None

        # Complete operation
        result_data = {"user_id": 123, "name": "John Doe"}
        tracker.flext_api_complete_operation(operation_id, result_data)

        # Check completed operation
        completed_operation = tracker.flext_api_get_operation(operation_id)
        assert completed_operation["status"] == "completed"
        assert completed_operation["completed_at"] is not None
        assert completed_operation["result"] == result_data
        assert completed_operation["error"] is None

    def test_operation_failure(self) -> None:
        """Test operation failure tracking."""
        tracker = FlextApiOperationTracker()

        operation_id = "failing_operation_001"
        tracker.flext_api_start_operation(operation_id, "risky_operation")

        # Fail operation
        error_message = "Database connection failed"
        tracker.flext_api_fail_operation(operation_id, error_message)

        # Check failed operation
        failed_operation = tracker.flext_api_get_operation(operation_id)
        assert failed_operation["status"] == "failed"
        assert failed_operation["completed_at"] is not None
        assert failed_operation["result"] is None
        assert failed_operation["error"] == error_message

    def test_multiple_operations_tracking(self) -> None:
        """Test tracking multiple operations simultaneously."""
        tracker = FlextApiOperationTracker()

        # Start multiple operations
        operations = [
            ("op1", "create_user"),
            ("op2", "update_profile"),
            ("op3", "delete_account"),
        ]

        for op_id, op_type in operations:
            tracker.flext_api_start_operation(op_id, op_type)

        # Check all operations are running
        all_operations = tracker.flext_api_get_all_operations()
        assert len(all_operations) == 3

        running_operations = tracker.flext_api_get_operations_by_status("running")
        assert len(running_operations) == 3

        # Complete some, fail others
        tracker.flext_api_complete_operation("op1", {"success": True})
        tracker.flext_api_fail_operation("op2", "Validation error")
        # Leave op3 running

        # Check status distribution
        completed = tracker.flext_api_get_operations_by_status("completed")
        failed = tracker.flext_api_get_operations_by_status("failed")
        running = tracker.flext_api_get_operations_by_status("running")

        assert len(completed) == 1
        assert len(failed) == 1
        assert len(running) == 1


class TestPagination:
    """Test pagination helpers for real data pagination scenarios."""

    def test_paginate_list_first_page(self) -> None:
        """Test pagination with real dataset - first page."""
        # Simulate user list from database
        users = [{"id": i, "name": f"User {i}"} for i in range(1, 101)]  # 100 users

        result = FlextApiPagination.flext_api_paginate_list(users, page=1, page_size=20)

        assert len(result["items"]) == 20
        assert result["items"][0]["id"] == 1
        assert result["items"][-1]["id"] == 20

        pagination = result["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 20
        assert pagination["total_items"] == 100
        assert pagination["total_pages"] == 5
        assert pagination["has_previous"] is False
        assert pagination["has_next"] is True
        assert pagination["previous_page"] is None
        assert pagination["next_page"] == 2

    def test_paginate_list_middle_page(self) -> None:
        """Test pagination - middle page."""
        items = list(range(1, 51))  # 50 items

        result = FlextApiPagination.flext_api_paginate_list(items, page=3, page_size=10)

        assert len(result["items"]) == 10
        assert result["items"][0] == 21  # (3-1) * 10 + 1
        assert result["items"][-1] == 30

        pagination = result["pagination"]
        assert pagination["current_page"] == 3
        assert pagination["total_pages"] == 5
        assert pagination["has_previous"] is True
        assert pagination["has_next"] is True
        assert pagination["previous_page"] == 2
        assert pagination["next_page"] == 4

    def test_paginate_list_last_page(self) -> None:
        """Test pagination - last page with partial results."""
        items = list(range(1, 48))  # 47 items

        result = FlextApiPagination.flext_api_paginate_list(items, page=5, page_size=10)

        assert len(result["items"]) == 7  # Remaining items on last page
        assert result["items"][0] == 41
        assert result["items"][-1] == 47

        pagination = result["pagination"]
        assert pagination["current_page"] == 5
        assert pagination["total_pages"] == 5
        assert pagination["has_previous"] is True
        assert pagination["has_next"] is False
        assert pagination["previous_page"] == 4
        assert pagination["next_page"] is None

    def test_extract_pagination_params(self) -> None:
        """Test pagination parameter extraction from request."""
        # Valid parameters
        request_params = {"page": "3", "page_size": "25"}
        page, page_size = FlextApiPagination.flext_api_extract_pagination_params(
            request_params,
        )

        assert page == 3
        assert page_size == 25

        # Invalid parameters - should use defaults
        invalid_params = {"page": "invalid", "page_size": "-5"}
        page, page_size = FlextApiPagination.flext_api_extract_pagination_params(
            invalid_params,
        )

        assert page == 1
        assert page_size == 20

        # Parameters with limits
        large_params = {"page": "0", "page_size": "500"}
        page, page_size = FlextApiPagination.flext_api_extract_pagination_params(
            large_params,
        )

        assert page == 1  # Minimum 1
        assert page_size == 100  # Maximum 100


class TestFactoryFunctions:
    """Test factory functions for simplified creation."""

    def test_create_operation_tracker(self) -> None:
        """Test operation tracker factory."""
        tracker = flext_api_create_operation_tracker()

        assert isinstance(tracker, FlextApiOperationTracker)
        assert len(tracker.flext_api_get_all_operations()) == 0

    def test_create_standard_request(self) -> None:
        """Test standard request factory with real request data."""
        request = flext_api_create_standard_request(
            url="https://api.example.com/users",
            method="POST",
            data={"name": "John", "email": "john@example.com"},
            headers={"Authorization": "Bearer token123"},
            timeout=60,
        )

        assert request["method"] == "POST"
        assert request["url"] == "https://api.example.com/users"
        assert request["data"]["name"] == "John"
        assert request["headers"]["Authorization"] == "Bearer token123"
        assert request["timeout"] == 60

    def test_create_standard_request_defaults(self) -> None:
        """Test standard request factory with default values."""
        request = flext_api_create_standard_request("https://api.example.com/health")

        assert request["method"] == "GET"
        assert request["url"] == "https://api.example.com/health"
        assert request["data"] == {}
        assert request["headers"] == {}
        assert request["timeout"] == 30


class TestTypedDictStructures:
    """Test TypedDict structures for type safety and validation."""

    def test_standard_response_structure(self) -> None:
        """Test standard response TypedDict structure."""
        response = flext_api_build_success({"user_id": 123}, "User found")

        # Verify all required fields are present
        required_fields = ["success", "data", "status", "message", "timestamp"]
        for field in required_fields:
            assert field in response

        # Verify types match TypedDict definition
        assert isinstance(response["success"], bool)
        assert isinstance(response["status"], int)
        assert isinstance(response["message"], str)
        assert isinstance(response["timestamp"], str)

    def test_standard_request_structure(self) -> None:
        """Test standard request TypedDict structure."""
        request = flext_api_create_standard_request(
            "https://api.test.com/endpoint",
            "PUT",
            {"field": "value"},
            {"Content-Type": "application/json"},
        )

        # Verify all required fields are present
        required_fields = ["method", "url", "headers", "data", "timeout"]
        for field in required_fields:
            assert field in request

        # Verify types
        assert isinstance(request["method"], str)
        assert isinstance(request["url"], str)
        assert isinstance(request["headers"], dict)
        assert isinstance(request["data"], dict)
        assert isinstance(request["timeout"], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
