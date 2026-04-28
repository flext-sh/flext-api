"""Storage component backed by centralized Pydantic models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import (
    Mapping,
    MutableMapping,
    Sequence,
)

from flext_api import c, m, p, r, t
from flext_web import u


class FlextApiStorage:
    """In-memory storage with centralized settings/state models."""

    settings: m.Api.Storage.Settings
    state: m.Api.Storage.State

    def __init__(
        self,
        settings: m.Api.Storage.Settings | Mapping[str, t.JsonPayload] | None = None,
        **overrides: t.JsonPayload,
    ) -> None:
        """Create one storage instance from the canonical settings model."""
        existing_payload: dict[str, t.JsonPayload] = (
            dict(settings.model_dump())
            if isinstance(settings, m.Api.Storage.Settings)
            else dict(settings or {})
        )
        self.settings = m.Api.Storage.Settings.model_validate({
            **existing_payload,
            **overrides,
        })
        self.state = m.Api.Storage.State()
        self.logger = u.fetch_logger(__name__)

    def batch_delete(self, keys: t.StrSequence) -> p.Result[bool]:
        """Delete multiple keys."""
        all_deleted = True
        for key in keys:
            delete_result = self.delete(key)
            if delete_result.failure:
                all_deleted = False
        if all_deleted:
            return r[bool].ok(True)
        return r[bool].fail("Some keys could not be deleted")

    def batch_get(self, keys: t.StrSequence) -> p.Result[t.JsonMapping]:
        """Get multiple keys."""
        collected: t.MutableJsonMapping = {}
        for key in keys:
            get_result = self.get(key)
            if get_result.success:
                collected[key] = get_result.value
        return r[t.JsonMapping].ok(collected)

    def batch_set(
        self,
        data: t.JsonMapping,
        ttl: int | None = None,
    ) -> p.Result[bool]:
        """Set multiple keys."""
        for key, value in data.items():
            set_result = self.set(key, value, ttl=ttl)
            if set_result.failure:
                return set_result
        return r[bool].ok(True)

    def cleanup_expired(self) -> p.Result[int]:
        """Remove expired entries and return the count."""
        return r[int].ok(self._cleanup_expired_entries())

    def clear(self) -> p.Result[bool]:
        """Clear storage state."""
        created_at = self.state.created_at
        self.state = m.Api.Storage.State(created_at=created_at)
        return r[bool].ok(True)

    def delete(self, key: str) -> p.Result[bool]:
        """Delete one key."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[bool].fail(key_result.error)
        self._cleanup_expired_entries()
        self._record_operation()
        normalized_key = key_result.value
        if normalized_key not in self.state.entries:
            return r[bool].fail(f"Key not found: {normalized_key}")
        del self.state.entries[normalized_key]
        return r[bool].ok(True)

    def deserialize_json(self, json_str: str) -> p.Result[t.JsonValue]:
        """Deserialize JSON into the canonical container contract."""
        return u.try_(
            lambda: t.Api.API_JSON_VALUE_ADAPTER.validate_json(json_str),
            catch=(ValueError, TypeError),
        ).map_error(lambda error: f"JSON deserialization failed: {error}")

    def execute(self) -> p.Result[bool]:
        """Lifecycle entrypoint for parity with service-shaped components."""
        return r[bool].ok(True)

    def exists(self, key: str) -> p.Result[bool]:
        """Return whether the key exists after expiration cleanup."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[bool].fail(key_result.error)
        self._cleanup_expired_entries()
        return r[bool].ok(key_result.value in self.state.entries)

    def get(self, key: str) -> p.Result[t.JsonValue]:
        """Get one value from storage."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[t.JsonValue].fail(key_result.error)
        self._cleanup_expired_entries()
        self._record_operation()
        normalized_key = key_result.value
        entry = self.state.entries.get(normalized_key)
        if entry is None:
            self.state.cache_misses += 1
            return r[t.JsonValue].fail(f"Key not found: {normalized_key}")
        self.state.cache_hits += 1
        return r[t.JsonValue].ok(entry.value)

    def cache_stats(self) -> p.Result[t.Api.CacheDict]:
        """Return cache counters."""
        stats = self._stats_model()
        return r[t.Api.CacheDict].ok({
            "size": stats.storage_size,
            "backend": self.settings.backend,
            "hits": stats.cache_hits,
            "misses": stats.cache_misses,
        })

    def storage_metrics(self) -> p.Result[t.IntMapping]:
        """Return integer storage counters."""
        stats = self._stats_model()
        return r[t.IntMapping].ok({
            "total_operations": stats.total_operations,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
        })

    def storage_statistics(self) -> p.Result[Mapping[str, float]]:
        """Return float-based storage statistics."""
        stats = self._stats_model()
        return r[Mapping[str, float]].ok({
            "total_operations": float(stats.total_operations),
            "cache_hits": float(stats.cache_hits),
            "cache_misses": float(stats.cache_misses),
            "hit_ratio": stats.hit_ratio,
            "storage_size": float(stats.storage_size),
            "memory_usage": float(stats.memory_usage),
        })

    def health_check(self) -> p.Result[t.JsonMapping]:
        """Return health information."""
        return r[t.JsonMapping].ok({
            "status": c.HealthStatus.HEALTHY.value,
            "timestamp": u.generate_iso_timestamp(),
            "storage_accessible": True,
            "size": len(self.state.entries),
            "operations_count": self.state.operations_count,
        })

    def info(self) -> p.Result[t.JsonMapping]:
        """Return storage configuration and runtime info."""
        return r[t.JsonMapping].ok({
            "namespace": self.settings.namespace,
            "backend": self.settings.backend,
            "size": len(self.state.entries),
            "created_at": self.state.created_at,
            "max_size": self.settings.max_size,
            "default_ttl": self.settings.default_ttl,
            "operations_count": self.state.operations_count,
        })

    def items(self) -> p.Result[Sequence[t.Pair[str, t.JsonValue]]]:
        """Return stored key-value pairs."""
        self._cleanup_expired_entries()
        return r[Sequence[t.Pair[str, t.JsonValue]]].ok(
            [(key, entry.value) for key, entry in self.state.entries.items()],
        )

    def keys(self) -> p.Result[t.StrSequence]:
        """Return stored keys."""
        self._cleanup_expired_entries()
        return r[t.StrSequence].ok(list(self.state.entries.keys()))

    def metrics(self) -> p.Result[t.JsonMapping]:
        """Return canonical storage metrics payload."""
        stats = self._stats_model()
        return r[t.JsonMapping].ok({
            "total_operations": stats.total_operations,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
            "hit_ratio": stats.hit_ratio,
            "storage_size": stats.storage_size,
            "memory_usage": stats.memory_usage,
            "namespace": stats.namespace,
        })

    def serialize_json(self, data: t.JsonValue) -> p.Result[str]:
        """Serialize one JSON-compatible value."""
        if data is None:
            return r[str].ok("null")
        return u.try_(
            lambda: t.Api.API_JSON_VALUE_ADAPTER.dump_json(data).decode(
                c.DEFAULT_ENCODING
            ),
            catch=(ValueError, TypeError),
        ).map_error(lambda error: f"JSON serialization failed: {error}")

    def set(
        self,
        key: str,
        value: t.JsonValue,
        timeout: int | None = None,
        ttl: int | None = None,
    ) -> p.Result[bool]:
        """Store one value with optional TTL."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[bool].fail(key_result.error)
        resolved_ttl = timeout if timeout is not None else ttl
        if resolved_ttl is None:
            resolved_ttl = self.settings.default_ttl
        if resolved_ttl is not None and resolved_ttl <= 0:
            return r[bool].fail("TTL must be positive")
        normalized_key = key_result.value
        self._cleanup_expired_entries()
        if (
            self.settings.max_size is not None
            and normalized_key not in self.state.entries
            and len(self.state.entries) >= self.settings.max_size
        ):
            return r[bool].fail("Storage is full")
        metadata_value = t.Api.API_JSON_VALUE_ADAPTER.validate_python(value)
        metadata_payload: MutableMapping[str, t.JsonValue | str | t.Numeric] = {
            "value": metadata_value,
            "timestamp": u.generate_iso_timestamp(),
            "created_at": time.time(),
        }
        if resolved_ttl is not None:
            metadata_payload["ttl"] = resolved_ttl
        metadata_result = u.try_(
            lambda: m.Api.Storage.Metadata.model_validate(metadata_payload),
            catch=(c.ValidationError, TypeError, ValueError),
        ).map_error(lambda error: f"Metadata validation failed: {error}")
        if metadata_result.failure:
            return r[bool].fail(metadata_result.error or "Metadata validation failed")
        self.state.entries[normalized_key] = metadata_result.value
        self._record_operation()
        return r[bool].ok(True)

    def size(self) -> p.Result[int]:
        """Return current storage size."""
        self._cleanup_expired_entries()
        return r[int].ok(len(self.state.entries))

    def values(self) -> p.Result[t.JsonList]:
        """Return stored values."""
        self._cleanup_expired_entries()
        return r[t.JsonList].ok(
            [entry.value for entry in self.state.entries.values()],
        )

    @staticmethod
    def _validate_key(key: str) -> p.Result[str]:
        """Validate a public storage key."""
        key_result: p.Result[str] = u.validate_value(t.Api.STRING_ADAPTER, key)
        if key_result.failure:
            return r[str].fail(key_result.error or "Invalid storage key")
        normalized_key = key_result.value.strip()
        if not normalized_key:
            return r[str].fail("Key must be non-empty string")
        return r[str].ok(normalized_key)

    def _cleanup_expired_entries(self) -> int:
        """Remove expired entries and return the number removed."""
        expired_keys = [
            key for key, entry in self.state.entries.items() if entry.expired
        ]
        for key in expired_keys:
            del self.state.entries[key]
        return len(expired_keys)

    def _estimate_memory_usage(self) -> int:
        """Estimate in-memory payload size through canonical JSON serialization."""
        return sum(
            len(t.Api.STRING_ADAPTER.dump_json(key))
            + len(t.Api.API_JSON_VALUE_ADAPTER.dump_json(entry.value))
            for key, entry in self.state.entries.items()
        )

    def _record_operation(self) -> None:
        """Increment storage operation count."""
        self.state.operations_count += 1

    def _stats_model(self) -> m.Api.Storage.Stats:
        """Materialize one stats model from centralized runtime state."""
        return m.Api.Storage.Stats(
            total_operations=self.state.operations_count,
            cache_hits=self.state.cache_hits,
            cache_misses=self.state.cache_misses,
            storage_size=len(self.state.entries),
            memory_usage=self._estimate_memory_usage(),
            namespace=self.settings.namespace,
        )


__all__: t.MutableSequenceOf[str] = ["FlextApiStorage"]
