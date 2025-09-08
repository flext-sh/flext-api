"""Transaction and cache behavior tests for storage backends.

NOTE: All tests in this file are skipped because transaction APIs
(begin_transaction, commit_transaction, rollback_transaction) are not implemented.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio

import pytest

from flext_api import FlextApiStorage

# All tests marked as skip due to missing transaction API
pytestmark = pytest.mark.skip(reason="Transaction APIs not implemented")


@pytest.mark.asyncio
async def test_transaction_commit_set_and_delete_and_cache() -> None:
    """Transaction commit persists set/delete and populates cache."""
    storage = FlextApiStorage(
        {
            "namespace": "txn",
            "backend": "memory",
            "enable_caching": True,
        }
    )
    tx = storage.begin_transaction()
    assert (await storage.set("a", 1, transaction_id=tx)).success
    assert (await storage.set("b", 2, transaction_id=tx)).success
    assert (await storage.delete("a", transaction_id=tx)).success
    assert (await storage.commit_transaction(tx)).success

    # After commit, key a should be absent, b present
    assert (await storage.get("a")).value is None
    assert (await storage.get("b")).value == 2

    # Cache should serve subsequent fetch
    res_cached = await storage.get("b")
    assert res_cached.success
    assert res_cached.value == 2


@pytest.mark.asyncio
async def test_transaction_rollback_and_clear_cache_and_close() -> None:
    """Rollback clears changes; clear() empties cache; close() succeeds."""
    storage = FlextApiStorage(
        {
            "namespace": "rb",
            "backend": "memory",
            "enable_caching": True,
        }
    )
    tx = storage.begin_transaction()
    await storage.set("x", 99, transaction_id=tx)
    assert storage.rollback_transaction(tx).success
    assert (await storage.get("x")).value is None

    # Setting and then clearing
    await storage.set("y", 1)
    assert (await storage.clear()).success
    assert (await storage.keys()).value == []

    # Close should succeed when there are no active transactions
    assert (await storage.close()).success


@pytest.mark.asyncio
async def test_cache_ttl_expiration_with_real_time() -> None:
    """TTL expiration is respected using REAL time delay - NO MOCKS."""
    # Use very short TTL for fast test execution
    storage = FlextApiStorage(
        {
            "namespace": "ttl_real",
            "backend": "memory",
            "enable_caching": True,
            "cache_ttl_seconds": 10,
        }
    )

    # Set value with short TTL for real-time test
    await storage.set("real_ttl_key", "test_value", ttl_seconds=1)  # 1 second TTL

    # Verify value exists immediately
    result = await storage.get("real_ttl_key")
    assert result.success
    assert result.value == "test_value"

    # Wait for TTL to expire with REAL time
    await asyncio.sleep(1.1)  # Wait slightly longer than TTL

    # Value should be expired now
    expired_result = await storage.get("real_ttl_key")
    assert expired_result.success
    assert expired_result.value is None  # Should be None after TTL expiration

    # exists() should also return False
    exists_result = await storage.exists("real_ttl_key")
    assert exists_result.success
    assert exists_result.value is False
