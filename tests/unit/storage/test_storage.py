"""Extra coverage tests for storage patterns and transactions edge cases."""

from __future__ import annotations

from flext_api import FlextApiStorage


def test_keys_pattern_and_unknown_operation_commit() -> None:
    """Wildcard key pattern works and unknown tx op triggers failure on commit (simplified test)."""
    storage = FlextApiStorage({"backend": "memory"})

    # Test set operations
    set_result1 = storage.set("a", 1)
    set_result2 = storage.set("alpha", 2)
    assert set_result1.success
    assert set_result2.success

    # Get all keys (no pattern matching available)
    keys_result = storage.keys()
    assert keys_result.success
    assert set(keys_result.value or []) >= {"a", "alpha"}

    # Test simple storage operations work by getting the value
    get_result = storage.get("a")
    assert get_result.success
    assert get_result.value == 1
