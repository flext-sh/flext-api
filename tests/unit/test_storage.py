"""Public-contract tests for the API storage component.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_api import FlextApiStorage, m


class TestStorageContract:
    """Validate storage behavior only through its public API."""

    def test_storage_uses_canonical_settings_model(self) -> None:
        """Storage exposes configured namespace and runtime info."""
        storage = FlextApiStorage(
            settings=m.Api.Storage.Settings(
                namespace="api-cache",
                backend="memory",
                max_size=2,
                default_ttl=30,
            ),
        )

        info_result = storage.info()

        tm.that(storage.namespace, eq="api-cache")
        tm.that(storage.backend, eq="memory")
        tm.that(info_result.success, eq=True)
        tm.that(info_result.value["max_size"], eq=2)
        tm.that(info_result.value["default_ttl"], eq=30)

    def test_storage_set_get_exists_and_delete(self) -> None:
        """Storage keeps and removes values through public methods."""
        storage = FlextApiStorage()

        set_result = storage.set("user:1", {"name": "Ada", "active": True})
        exists_result = storage.exists("user:1")
        get_result = storage.get("user:1")
        delete_result = storage.delete("user:1")
        missing_result = storage.get("user:1")

        tm.that(set_result.success, eq=True)
        tm.that(exists_result.value, eq=True)
        tm.that(get_result.success, eq=True)
        tm.that(get_result.value, eq={"name": "Ada", "active": True})
        tm.that(delete_result.success, eq=True)
        tm.that(missing_result.failure, eq=True)

    def test_storage_rejects_new_entries_after_capacity_limit(self) -> None:
        """Storage refuses inserts past configured capacity."""
        storage = FlextApiStorage(
            settings=m.Api.Storage.Settings(namespace="bounded", max_size=1),
        )

        first_result = storage.set("first", {"ok": True})
        second_result = storage.set("second", {"ok": False})

        tm.that(first_result.success, eq=True)
        tm.that(second_result.failure, eq=True)
        tm.that(second_result.error, eq="Storage is full")

    def test_storage_metrics_report_hits_and_misses(self) -> None:
        """Storage metrics reflect observable get behavior."""
        storage = FlextApiStorage()

        storage.set("cached", {"status": "ready"})
        storage.get("cached")
        storage.get("missing")
        metrics_result = storage.metrics()
        statistics_result = storage.storage_statistics()

        tm.that(metrics_result.success, eq=True)
        tm.that(metrics_result.value["cache_hits"], eq=1)
        tm.that(metrics_result.value["cache_misses"], eq=1)
        tm.that(statistics_result.success, eq=True)
        tm.that(statistics_result.value["hit_ratio"], eq=1 / 3)
