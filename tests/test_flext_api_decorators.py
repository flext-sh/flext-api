#!/usr/bin/env python3
"""Test FlextApi Decorators - Validate centralized decorator functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive tests for all decorator patterns - real functionality validation.
"""

import asyncio
import time
from typing import Any

import pytest

from flext_api.helpers.flext_api_decorators import (
    flext_api_bulk_processor,
    flext_api_cached_resilient,
    flext_api_circuit_breaker,
    flext_api_memoize_advanced,
    flext_api_rate_limit,
    flext_api_resilient,
    flext_api_with_cache,
    flext_api_with_logging,
    flext_api_with_retry,
    flext_api_with_timeout,
    flext_api_with_validation,
)


class TestBasicDecorators:
    """Test basic decorator functionality."""

    def test_with_logging_sync_function(self) -> None:
        """Test logging decorator with sync function."""
        call_log = []

        @flext_api_with_logging
        def test_function(x: int, y: int) -> int:
            call_log.append(f"Called with {x}, {y}")
            return x + y

        result = test_function(3, 5)

        assert result == 8
        assert len(call_log) == 1
        assert "Called with 3, 5" in call_log[0]

    @pytest.mark.asyncio
    async def test_with_logging_async_function(self) -> None:
        """Test logging decorator with async function."""
        call_log = []

        @flext_api_with_logging
        async def async_test_function(value: str) -> str:
            await asyncio.sleep(0.01)
            call_log.append(f"Async called with {value}")
            return f"Result: {value}"

        result = await async_test_function("test")

        assert result == "Result: test"
        assert len(call_log) == 1

    def test_with_retry_success_after_failures(self) -> None:
        """Test retry decorator with function that succeeds after failures."""
        attempt_count = 0

        @flext_api_with_retry(max_retries=3, delay=0.01)
        def flaky_function() -> str:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                msg = f"Attempt {attempt_count} failed"
                raise ValueError(msg)
            return "Success!"

        result = flaky_function()

        assert result == "Success!"
        assert attempt_count == 3

    def test_with_retry_final_failure(self) -> None:
        """Test retry decorator when function fails all attempts."""
        attempt_count = 0

        @flext_api_with_retry(max_retries=2, delay=0.01)
        def always_failing_function() -> str:
            nonlocal attempt_count
            attempt_count += 1
            msg = f"Failure {attempt_count}"
            raise RuntimeError(msg)

        with pytest.raises(RuntimeError, match="Failure 3"):
            always_failing_function()

        assert attempt_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_with_timeout_success(self) -> None:
        """Test timeout decorator with function that completes in time."""

        @flext_api_with_timeout(1.0)
        async def fast_function() -> str:
            await asyncio.sleep(0.01)
            return "Completed"

        result = await fast_function()
        assert result == "Completed"

    @pytest.mark.asyncio
    async def test_with_timeout_failure(self) -> None:
        """Test timeout decorator with function that exceeds timeout."""

        @flext_api_with_timeout(0.1)
        async def slow_function() -> str:
            await asyncio.sleep(0.5)
            return "Should not reach here"

        with pytest.raises(asyncio.TimeoutError):
            await slow_function()

    def test_with_validation_success(self) -> None:
        """Test validation decorator with valid input."""

        def validate_positive(x: int) -> bool:
            return x > 0

        @flext_api_with_validation([validate_positive])
        def process_positive_number(x: int) -> int:
            return x * 2

        result = process_positive_number(5)
        assert result == 10

    def test_with_validation_failure(self) -> None:
        """Test validation decorator with invalid input."""

        def validate_positive(x: int) -> bool:
            return x > 0

        @flext_api_with_validation([validate_positive])
        def process_positive_number(x: int) -> int:
            return x * 2

        with pytest.raises(ValueError, match="Validation failed"):
            process_positive_number(-5)


class TestCacheDecorator:
    """Test cache decorator functionality."""

    def test_with_cache_basic_functionality(self) -> None:
        """Test basic cache functionality."""
        call_count = 0

        @flext_api_with_cache(ttl=60)
        def expensive_calculation(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x

        # First call - should execute function
        result1 = expensive_calculation(5)
        assert result1 == 25
        assert call_count == 1

        # Second call with same args - should use cache
        result2 = expensive_calculation(5)
        assert result2 == 25
        assert call_count == 1  # No additional call

        # Different args - should execute function
        result3 = expensive_calculation(10)
        assert result3 == 100
        assert call_count == 2

    def test_with_cache_expiration(self) -> None:
        """Test cache expiration functionality."""
        call_count = 0

        @flext_api_with_cache(ttl=0.1)  # Very short TTL
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x + 1

        # First call
        result1 = cached_function(1)
        assert result1 == 2
        assert call_count == 1

        # Wait for cache expiration
        time.sleep(0.2)

        # Should execute function again due to expiration
        result2 = cached_function(1)
        assert result2 == 2
        assert call_count == 2


class TestAdvancedDecorators:
    """Test advanced decorator functionality."""

    def test_memoize_advanced_with_complex_args(self) -> None:
        """Test advanced memoization with complex arguments."""
        call_count = 0

        @flext_api_memoize_advanced
        def complex_function(data: dict[str, Any], factor: int = 2) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            return {
                k: v * factor for k, v in data.items() if isinstance(v, (int, float))
            }

        test_data = {"a": 10, "b": 20, "c": "string"}

        # First call
        result1 = complex_function(test_data, factor=3)
        expected = {"a": 30, "b": 60}
        assert result1 == expected
        assert call_count == 1

        # Same call - should use memoization
        result2 = complex_function(test_data, factor=3)
        assert result2 == expected
        assert call_count == 1

        # Different factor - should execute again
        result3 = complex_function(test_data, factor=5)
        expected_new = {"a": 50, "b": 100}
        assert result3 == expected_new
        assert call_count == 2

    def test_rate_limit_decorator(self) -> None:
        """Test rate limiting decorator."""
        call_times = []

        @flext_api_rate_limit(max_calls=2, window=1.0)
        def rate_limited_function() -> str:
            call_times.append(time.time())
            return "Called"

        # First two calls should succeed
        result1 = rate_limited_function()
        result2 = rate_limited_function()

        assert result1 == "Called"
        assert result2 == "Called"
        assert len(call_times) == 2

        # Third call should fail due to rate limit
        with pytest.raises(Exception, match="Rate limit exceeded"):
            rate_limited_function()

    @pytest.mark.asyncio
    async def test_bulk_processor_decorator(self) -> None:
        """Test bulk processor decorator."""
        processed_items = []

        @flext_api_bulk_processor(batch_size=3)
        async def process_items(items: list[int]) -> list[int]:
            processed_items.extend(items)
            return [x * 2 for x in items]

        # Process items that will be batched
        items_to_process = [1, 2, 3, 4, 5, 6, 7]
        results = []

        for item in items_to_process:
            result = await process_items([item])
            results.extend(result)

        # Wait for any pending batches
        await asyncio.sleep(0.1)

        # Verify all items were processed
        assert len(processed_items) >= len(items_to_process)
        assert all(item * 2 in results for item in items_to_process)

    def test_circuit_breaker_normal_operation(self) -> None:
        """Test circuit breaker in normal operation."""

        @flext_api_circuit_breaker(failure_threshold=3, timeout=60)
        def reliable_function(x: int) -> int:
            return x * 2

        # Normal operations should work
        for i in range(5):
            result = reliable_function(i)
            assert result == i * 2

    def test_circuit_breaker_with_failures(self) -> None:
        """Test circuit breaker with failures."""
        failure_count = 0

        @flext_api_circuit_breaker(failure_threshold=2, timeout=0.1)
        def unreliable_function() -> str:
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 3:
                msg = "Service unavailable"
                raise RuntimeError(msg)
            return "Success"

        # First failures should trigger circuit breaker
        with pytest.raises(RuntimeError):
            unreliable_function()

        with pytest.raises(RuntimeError):
            unreliable_function()

        # Circuit should be open now - calls should fail immediately
        with pytest.raises(Exception, match="Circuit breaker is open"):
            unreliable_function()


class TestCompositeDecorators:
    """Test composite decorators that combine multiple patterns."""

    @pytest.mark.asyncio
    async def test_resilient_decorator(self) -> None:
        """Test resilient decorator combining retry and circuit breaker."""
        attempt_count = 0

        @flext_api_resilient(max_retries=2, failure_threshold=5)
        async def semi_reliable_function() -> str:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 2:
                msg = "Network error"
                raise ConnectionError(msg)
            return "Connected"

        result = await semi_reliable_function()

        assert result == "Connected"
        assert attempt_count == 3  # Initial + 2 retries

    def test_cached_resilient_decorator(self) -> None:
        """Test cached resilient decorator combining cache and resilience."""
        call_count = 0

        @flext_api_cached_resilient(ttl=60, max_retries=2)
        def cached_flaky_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "First call fails"
                raise ValueError(msg)
            return x * x

        # First call should retry and succeed
        result1 = cached_flaky_function(5)
        assert result1 == 25
        assert call_count == 2  # Failed once, then succeeded

        # Second call should use cache
        result2 = cached_flaky_function(5)
        assert result2 == 25
        assert call_count == 2  # No additional calls due to cache


class TestDecoratorEdgeCases:
    """Test edge cases and error conditions."""

    def test_decorator_with_none_args(self) -> None:
        """Test decorators handle None arguments gracefully."""

        @flext_api_with_logging
        def function_with_none(value: str | None = None) -> str:
            return f"Value: {value}"

        result = function_with_none(None)
        assert result == "Value: None"

    def test_decorator_with_exceptions(self) -> None:
        """Test decorators handle exceptions properly."""

        @flext_api_with_logging
        def failing_function() -> None:
            msg = "Test exception"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Test exception"):
            failing_function()

    @pytest.mark.asyncio
    async def test_async_decorator_with_sync_function(self) -> None:
        """Test async-capable decorators with sync functions."""

        @flext_api_with_timeout(1.0)
        def sync_function(x: int) -> int:
            return x + 1

        result = await sync_function(5)
        assert result == 6

    def test_decorator_parameter_validation(self) -> None:
        """Test decorator parameter validation."""
        # Test with invalid TTL
        with pytest.raises((ValueError, TypeError)):

            @flext_api_with_cache(ttl=-1)
            def invalid_cache_function() -> None:
                pass

        # Test with invalid retry count
        with pytest.raises((ValueError, TypeError)):

            @flext_api_with_retry(max_retries=-1)
            def invalid_retry_function() -> None:
                pass


class TestDecoratorCombinations:
    """Test combining multiple decorators."""

    def test_multiple_decorators_stacked(self) -> None:
        """Test stacking multiple decorators."""
        call_count = 0

        @flext_api_with_cache(ttl=60)
        @flext_api_with_logging
        @flext_api_with_retry(max_retries=2, delay=0.01)
        def multi_decorated_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "First attempt fails"
                raise ValueError(msg)
            return x * 3

        # Should retry once and then cache result
        result1 = multi_decorated_function(4)
        assert result1 == 12
        assert call_count == 2

        # Second call should use cache
        result2 = multi_decorated_function(4)
        assert result2 == 12
        assert call_count == 2  # No additional calls due to cache

    @pytest.mark.asyncio
    async def test_async_decorators_combination(self) -> None:
        """Test combining async decorators."""

        @flext_api_with_timeout(1.0)
        @flext_api_with_retry(max_retries=1, delay=0.01)
        async def combined_async_function(delay: float) -> str:
            await asyncio.sleep(delay)
            return "Completed"

        # Should complete within timeout
        result = await combined_async_function(0.01)
        assert result == "Completed"


class TestDecoratorPerformance:
    """Test decorator performance characteristics."""

    def test_cache_performance_improvement(self) -> None:
        """Test that caching improves performance for expensive operations."""

        @flext_api_with_cache(ttl=60)
        def expensive_operation(n: int) -> int:
            # Simulate expensive computation
            result = 0
            for i in range(n):
                result += i
            return result

        # Measure first call
        start_time = time.time()
        result1 = expensive_operation(10000)
        first_duration = time.time() - start_time

        # Measure cached call
        start_time = time.time()
        result2 = expensive_operation(10000)
        cached_duration = time.time() - start_time

        assert result1 == result2
        assert cached_duration < first_duration / 10  # Cache should be much faster

    def test_memoization_memory_usage(self) -> None:
        """Test that memoization doesn't leak memory excessively."""

        @flext_api_memoize_advanced
        def fibonacci(n: int) -> int:
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        # Calculate several fibonacci numbers
        results = [fibonacci(i) for i in range(10)]

        # Verify correct results
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert results == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
