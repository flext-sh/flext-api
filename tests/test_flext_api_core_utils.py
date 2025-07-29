#!/usr/bin/env python3
"""Tests for FlextApi Core Utils - Comprehensive validation of core utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Testes robustos para utilities core que eliminam 90%+ do boilerplate.
"""

import asyncio
from datetime import datetime
from typing import Any

import pytest
from flext_core import FlextResult

from flext_api.helpers.flext_api_core_utils import (
    FlextApiDataProcessor,
    FlextApiOperation,
    flext_api_auto_operation,
    flext_api_cached_operation,
    flext_api_chain,
    flext_api_create_core_utils,
    flext_api_merge_results,
    flext_api_operation,
    flext_api_operation_context,
    flext_api_retry_operation,
    flext_api_safe_execute,
    flext_api_validate_data,
)


class TestFlextApiOperation:
    """Tests for FlextApiOperation - Operation wrapper with automatic error handling."""

    def test_operation_initialization(self) -> None:
        """Test operation initialization."""
        operation = flext_api_operation("test_op")

        assert operation.name == "test_op"
        assert operation.context == {}
        assert isinstance(operation.start_time, datetime)

    def test_operation_with_context(self) -> None:
        """Test operation with context."""
        context = {"user_id": "123", "request_id": "req-456"}
        operation = flext_api_operation("test_op", context)

        assert operation.context == context

    @pytest.mark.asyncio
    async def test_execute_sync_function_success(self) -> None:
        """Test executing synchronous function successfully."""
        operation = flext_api_operation("test_sync")

        def test_func(x: int, y: int) -> int:
            return x + y

        result = await operation.execute(test_func, 5, 10)

        assert result.is_success
        assert result.data == 15

    @pytest.mark.asyncio
    async def test_execute_async_function_success(self) -> None:
        """Test executing asynchronous function successfully."""
        operation = flext_api_operation("test_async")

        async def test_func(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        result = await operation.execute(test_func, 7)

        assert result.is_success
        assert result.data == 14

    @pytest.mark.asyncio
    async def test_execute_function_failure(self) -> None:
        """Test executing function that raises exception."""
        operation = flext_api_operation("test_failure")

        def failing_func() -> None:
            msg = "Something went wrong"
            raise ValueError(msg)

        result = await operation.execute(failing_func)

        assert not result.is_success
        assert "Something went wrong" in result.error


class TestFlextApiDataProcessor:
    """Tests for FlextApiDataProcessor - High-level data processing."""

    def test_process_dict_with_defaults(self) -> None:
        """Test processing dictionary with defaults."""
        data = {"name": "John"}
        defaults = {"age": 30, "active": True}

        result = FlextApiDataProcessor.flext_api_process_dict(
            data,
            defaults=defaults,
        )

        assert result.is_success
        processed_data = result.data
        assert processed_data["name"] == "John"
        assert processed_data["age"] == 30
        assert processed_data["active"] is True

    def test_process_dict_with_required_fields_success(self) -> None:
        """Test processing with required fields present."""
        data = {"name": "John", "email": "john@example.com", "age": 30}
        required = ["name", "email"]

        result = FlextApiDataProcessor.flext_api_process_dict(
            data,
            required_fields=required,
        )

        assert result.is_success
        assert result.data == data

    def test_process_dict_with_required_fields_missing(self) -> None:
        """Test processing with missing required fields."""
        data = {"name": "John"}
        required = ["name", "email", "age"]

        result = FlextApiDataProcessor.flext_api_process_dict(
            data,
            required_fields=required,
        )

        assert not result.is_success
        assert "Missing required fields" in result.error
        assert "email" in result.error
        assert "age" in result.error

    def test_process_dict_with_transformations(self) -> None:
        """Test processing with transformations."""
        data = {"name": "john", "age": "30"}
        transformations = {
            "name": lambda x: x.upper(),
            "age": int,
        }

        result = FlextApiDataProcessor.flext_api_process_dict(
            data,
            transformations=transformations,
        )

        assert result.is_success
        processed_data = result.data
        assert processed_data["name"] == "JOHN"
        assert processed_data["age"] == 30
        assert isinstance(processed_data["age"], int)

    def test_process_dict_transformation_failure(self) -> None:
        """Test processing with failing transformation."""
        data = {"age": "not_a_number"}
        transformations = {"age": int}

        result = FlextApiDataProcessor.flext_api_process_dict(
            data,
            transformations=transformations,
        )

        assert not result.is_success
        assert "Transformation failed for age" in result.error

    def test_batch_process_success(self) -> None:
        """Test batch processing with successful items."""
        items = [1, 2, 3, 4, 5]

        def processor(x: int) -> FlextResult[int]:
            return FlextResult.ok(x * 2)

        result = FlextApiDataProcessor.flext_api_batch_process(items, processor)

        assert result.is_success
        assert result.data == [2, 4, 6, 8, 10]

    def test_batch_process_with_failures(self) -> None:
        """Test batch processing with some failures."""
        items = [1, 2, 3, 4, 5]

        def processor(x: int) -> FlextResult[int]:
            if x == 3:
                return FlextResult.fail("Failed to process 3")
            return FlextResult.ok(x * 2)

        result = FlextApiDataProcessor.flext_api_batch_process(items, processor)

        assert result.is_success
        # Should contain successful results only
        assert result.data == [2, 4, 8, 10]


class TestFlextApiChain:
    """Tests for FlextApiChain - Chainable operations."""

    def test_chain_initialization(self) -> None:
        """Test chain initialization."""
        chain = flext_api_chain("hello")

        assert chain.value == "hello"
        assert chain.operations == []

    def test_chain_transform(self) -> None:
        """Test chain transformations."""
        result = (
            flext_api_chain("hello")
            .flext_api_transform(lambda x: x.upper())
            .flext_api_transform(lambda x: f"{x} WORLD")
            .flext_api_unwrap()
        )

        assert result == "HELLO WORLD"

    def test_chain_validate_success(self) -> None:
        """Test chain validation success."""
        result = (
            flext_api_chain(10)
            .flext_api_validate(lambda x: x > 5, "Must be greater than 5")
            .flext_api_transform(lambda x: x * 2)
            .flext_api_unwrap()
        )

        assert result == 20

    def test_chain_validate_failure(self) -> None:
        """Test chain validation failure."""
        with pytest.raises(ValueError, match="Must be greater than 10"):
            (
                flext_api_chain(5)
                .flext_api_validate(lambda x: x > 10, "Must be greater than 10")
                .flext_api_unwrap()
            )

    def test_chain_to_result(self) -> None:
        """Test converting chain to FlextResult."""
        result = (
            flext_api_chain("test")
            .flext_api_transform(lambda x: x.upper())
            .flext_api_to_result()
        )

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.data == "TEST"


class TestFlextApiDecorators:
    """Tests for FlextApi decorators."""

    @pytest.mark.asyncio
    async def test_auto_operation_decorator_success(self) -> None:
        """Test auto operation decorator with success."""

        @flext_api_auto_operation("test_operation")
        def test_func(x: int, y: int) -> int:
            return x + y

        result = await test_func(3, 4)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.data == 7

    @pytest.mark.asyncio
    async def test_auto_operation_decorator_failure(self) -> None:
        """Test auto operation decorator with failure."""

        @flext_api_auto_operation("failing_operation")
        def failing_func() -> None:
            msg = "Test error"
            raise RuntimeError(msg)

        result = await failing_func()

        assert isinstance(result, FlextResult)
        assert not result.is_success
        assert "Test error" in result.error

    def test_cached_operation_decorator(self) -> None:
        """Test cached operation decorator."""
        call_count = 0

        @flext_api_cached_operation(ttl_seconds=1)
        def expensive_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same args - should use cache
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count == 1  # No additional call

        # Third call with different args
        result3 = expensive_func(10)
        assert result3 == 20
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_operation_decorator_success(self) -> None:
        """Test retry operation decorator with eventual success."""
        attempt_count = 0

        @flext_api_retry_operation(max_retries=2, delay_seconds=0.01)
        async def flaky_func() -> str:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                msg = "Temporary failure"
                raise RuntimeError(msg)
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert attempt_count == 2

    @pytest.mark.asyncio
    async def test_retry_operation_decorator_max_retries(self) -> None:
        """Test retry operation decorator exceeding max retries."""

        @flext_api_retry_operation(max_retries=1, delay_seconds=0.01)
        async def always_failing_func() -> None:
            msg = "Always fails"
            raise RuntimeError(msg)

        with pytest.raises(RuntimeError, match="Always fails"):
            await always_failing_func()


class TestFlextApiContextManager:
    """Tests for FlextApi context managers."""

    @pytest.mark.asyncio
    async def test_operation_context_success(self) -> None:
        """Test operation context with successful operation."""
        async with flext_api_operation_context("test_context") as operation:
            assert isinstance(operation, FlextApiOperation)
            assert operation.name == "test_context"

    @pytest.mark.asyncio
    async def test_operation_context_failure(self) -> None:
        """Test operation context with failing operation."""
        with pytest.raises(RuntimeError):
            async with flext_api_operation_context("failing_context"):
                msg = "Test failure"
                raise RuntimeError(msg)


class TestFlextApiUtilityFunctions:
    """Tests for FlextApi utility functions."""

    def test_safe_execute_success(self) -> None:
        """Test safe execute with successful function."""

        def test_func(x: int, y: int) -> int:
            return x * y

        result = flext_api_safe_execute(test_func, 6, 7)

        assert result.is_success
        assert result.data == 42

    def test_safe_execute_failure(self) -> None:
        """Test safe execute with failing function."""

        def failing_func() -> None:
            msg = "Test error"
            raise ValueError(msg)

        result = flext_api_safe_execute(failing_func)

        assert not result.is_success
        assert "Test error" in result.error

    def test_merge_results_all_success(self) -> None:
        """Test merging all successful results."""
        result1 = FlextResult.ok("data1")
        result2 = FlextResult.ok("data2")
        result3 = FlextResult.ok("data3")

        merged = flext_api_merge_results(result1, result2, result3)

        assert merged.is_success
        assert merged.data == ["data1", "data2", "data3"]

    def test_merge_results_with_failures(self) -> None:
        """Test merging results with some failures."""
        result1 = FlextResult.ok("data1")
        result2 = FlextResult.fail("error2")
        result3 = FlextResult.ok("data3")

        merged = flext_api_merge_results(result1, result2, result3)

        assert not merged.is_success
        assert "error2" in merged.error

    def test_validate_data_success(self) -> None:
        """Test data validation with valid data."""
        data = {"name": "John", "age": 30, "active": True}
        schema = {"name": str, "age": int, "active": bool}
        required = ["name", "age"]

        result = flext_api_validate_data(data, schema, required)

        assert result.is_success
        assert result.data == data

    def test_validate_data_missing_required(self) -> None:
        """Test data validation with missing required fields."""
        data = {"name": "John"}
        schema = {"name": str, "age": int}
        required = ["name", "age"]

        result = flext_api_validate_data(data, schema, required)

        assert not result.is_success
        assert "Missing required fields" in result.error

    def test_validate_data_type_mismatch(self) -> None:
        """Test data validation with type mismatch."""
        data = {"name": "John", "age": "thirty"}  # age should be int
        schema = {"name": str, "age": int}

        result = flext_api_validate_data(data, schema)

        assert not result.is_success
        assert "should be int" in result.error


class TestFlextApiCoreUtilsFactory:
    """Tests for core utils factory function."""

    def test_create_core_utils(self) -> None:
        """Test creating core utils dictionary."""
        utils = flext_api_create_core_utils()

        assert isinstance(utils, dict)
        assert "operation" in utils
        assert "chain" in utils
        assert "safe_execute" in utils
        assert "merge_results" in utils
        assert "validate_data" in utils
        assert "data_processor" in utils
        assert "operation_context" in utils

        # Test that functions are callable
        assert callable(utils["operation"])
        assert callable(utils["chain"])
        assert callable(utils["safe_execute"])


class TestFlextApiRealWorldScenarios:
    """Tests for real-world usage scenarios."""

    @pytest.mark.asyncio
    async def test_complete_data_processing_workflow(self) -> None:
        """Test complete data processing workflow."""
        # Simulate raw user data
        raw_data = {
            "name": "john doe",
            "email": "JOHN@EXAMPLE.COM",
            "age": "25",
            "status": "active",
        }

        # Process data using chain operations
        result = (
            flext_api_chain(raw_data)
            .flext_api_transform(
                lambda data: {
                    **data,
                    "name": data["name"].title(),
                    "email": data["email"].lower(),
                    "age": int(data["age"]),
                },
            )
            .flext_api_validate(
                lambda data: data["age"] >= 18,
                "User must be 18 or older",
            )
            .flext_api_to_result()
        )

        assert result.is_success
        processed_data = result.data
        assert processed_data["name"] == "John Doe"
        assert processed_data["email"] == "john@example.com"
        assert processed_data["age"] == 25
        assert isinstance(processed_data["age"], int)

    @pytest.mark.asyncio
    async def test_operation_with_context_and_retry(self) -> None:
        """Test operation with context and retry logic."""
        attempt_count = 0

        @flext_api_retry_operation(max_retries=2, delay_seconds=0.01)
        @flext_api_auto_operation("user_creation")
        async def create_user(user_data: dict[str, Any]) -> dict[str, Any]:
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 2:
                msg = "Database temporarily unavailable"
                raise RuntimeError(msg)

            return {"id": 123, **user_data}

        user_data = {"name": "John", "email": "john@example.com"}
        result = await create_user(user_data)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.data["id"] == 123
        assert result.data["name"] == "John"
        assert attempt_count == 2

    def test_data_processor_with_multiple_operations(self) -> None:
        """Test data processor with multiple operations."""
        data = {
            "users": [
                {"name": "john", "status": "active", "score": "85"},
                {"name": "jane", "status": "inactive", "score": "92"},
                {"name": "bob", "status": "active", "score": "78"},
            ],
        }

        # Process users list
        result = FlextApiDataProcessor.flext_api_process_dict(
            data,
            transformations={
                "users": lambda users: [
                    {
                        **user,
                        "name": user["name"].title(),
                        "score": int(user["score"]),
                        "is_active": user["status"] == "active",
                    }
                    for user in users
                ],
            },
        )

        assert result.is_success
        processed_users = result.data["users"]

        assert processed_users[0]["name"] == "John"
        assert processed_users[0]["score"] == 85
        assert processed_users[0]["is_active"] is True

        assert processed_users[1]["name"] == "Jane"
        assert processed_users[1]["is_active"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
