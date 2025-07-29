#!/usr/bin/env python3
"""Teste standalone dos core utils para validar funcionalidade."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import operator

from flext_core import FlextResult

from flext_api.helpers.flext_api_core_utils import (
    FlextApiDataProcessor,
    flext_api_chain,
    flext_api_merge_results,
    flext_api_operation,
    flext_api_safe_execute,
)


async def test_core_utils() -> bool:
    """Test all core utils functionality."""
    # Test 1: Operation
    op = flext_api_operation("test_operation")
    assert op.name == "test_operation"
    assert op.context == {}

    # Test async execution
    async def test_func(x: int) -> int:
        await asyncio.sleep(0.001)
        return x * 2

    result = await op.execute(test_func, 5)
    assert result.is_success()
    assert result.data == 10

    # Test 2: Chain
    chain_result = (flext_api_chain("hello")
                   .flext_api_transform(lambda x: x.upper())
                   .flext_api_transform(lambda x: f"{x} WORLD")
                   .flext_api_unwrap())
    assert chain_result == "HELLO WORLD"

    # Test validation
    try:
        (flext_api_chain(5)
         .flext_api_validate(lambda x: x > 10, "Must be > 10")
         .flext_api_unwrap())
        msg = "Should have raised exception"
        raise AssertionError(msg)
    except ValueError:
        pass

    # Test 3: Safe Execute
    safe_result = flext_api_safe_execute(operator.add, 3, 4)
    assert safe_result.is_success
    assert safe_result.data == 7

    error_result = flext_api_safe_execute(lambda: 1 / 0)
    assert not error_result.is_success
    assert error_result.error is not None

    # Test 4: Merge Results
    result1 = FlextResult.ok("data1")
    result2 = FlextResult.ok("data2")
    merged = flext_api_merge_results(result1, result2)
    assert merged.is_success
    assert merged.data == ["data1", "data2"]

    fail_result = FlextResult.fail("error")
    merged_fail = flext_api_merge_results(result1, fail_result)
    assert not merged_fail.is_success

    # Test 5: Data Processor
    data = {"name": "john", "age": "25"}
    result = FlextApiDataProcessor.flext_api_process_dict(
        data,
        transformations={"name": lambda x: x.title(), "age": int},
    )
    assert result.is_success
    assert result.data["name"] == "John"
    assert result.data["age"] == 25

    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_core_utils())
        sys.exit(0 if result else 1)
    except Exception:
        sys.exit(1)
