"""Storage component backed by centralized Pydantic models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence

from flext_api import m, p, r, t, u


class FlextApiStorage:
    """In-memory storage with centralized settings/state models."""

    _settings: m.Api.Storage.Settings
    _state: m.Api.Storage.State

    def __init__(
        self,
        settings: m.Api.Storage.Settings | Mapping[str, t.ValueOrModel] | None = None,
        **overrides: t.ValueOrModel,
    ) -> None:
        """Create one storage instance from the canonical settings model."""
        self._settings = self._resolve_settings(settings, overrides)
        self._state = m.Api.Storage.State()
        self._logger = u.fetch_logger(__name__)

    @property
    def backend(self) -> str:
        """Return configured backend name."""
        return self._settings.backend

    @property
    def namespace(self) -> str:
        """Return configured namespace."""
        return self._settings.namespace

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

    def batch_get(self, keys: t.StrSequence) -> p.Result[Mapping[str, t.ApiJsonValue]]:
        """Get multiple keys."""
        collected: dict[str, t.ApiJsonValue] = {}
        for key in keys:
            get_result = self.get(key)
            if get_result.success:
                collected[key] = get_result.value
        return r[Mapping[str, t.ApiJsonValue]].ok(collected)

    def batch_set(
        self,
        data: Mapping[str, t.ApiJsonValue],
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
        created_at = self._state.created_at
        self._state = m.Api.Storage.State(created_at=created_at)
        return r[bool].ok(True)

    def delete(self, key: str) -> p.Result[bool]:
        """Delete one key."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[bool].fail(key_result.error)
        self._cleanup_expired_entries()
        self._record_operation()
        normalized_key = key_result.value
        if normalized_key not in self._state.entries:
            return r[bool].fail(f"Key not found: {normalized_key}")
        del self._state.entries[normalized_key]
        return r[bool].ok(True)

    def deserialize_json(self, json_str: str) -> p.Result[t.ContainerValue]:
        """Deserialize JSON into the canonical container contract."""
        return u.try_(
            lambda: t.Api.CONTAINER_VALUE_ADAPTER.validate_json(json_str),
            catch=(ValueError, TypeError),
        ).map_error(lambda error: f"JSON deserialization failed: {error}")

    def execute(
        self, *_args: t.ApiJsonValue, **_kwargs: t.ApiJsonValue
    ) -> p.Result[bool]:
        """Lifecycle entrypoint for parity with service-shaped components."""
        return r[bool].ok(True)

    def exists(self, key: str) -> p.Result[bool]:
        """Return whether the key exists after expiration cleanup."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[bool].fail(key_result.error)
        self._cleanup_expired_entries()
        return r[bool].ok(key_result.value in self._state.entries)

    def get(self, key: str) -> p.Result[t.ApiJsonValue]:
        """Get one value from storage."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[t.ApiJsonValue].fail(key_result.error)
        self._cleanup_expired_entries()
        self._record_operation()
        normalized_key = key_result.value
        entry = self._state.entries.get(normalized_key)
        if entry is None:
            self._state.cache_misses += 1
            return r[t.ApiJsonValue].fail(f"Key not found: {normalized_key}")
        self._state.cache_hits += 1
        return r[t.ApiJsonValue].ok(entry.value)

    def cache_stats(self) -> p.Result[t.Api.CacheDict]:
        """Return cache counters."""
        stats = self._stats_model()
        return r[t.Api.CacheDict].ok({
            "size": stats.storage_size,
            "backend": self.backend,
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

    def health_check(self) -> p.Result[Mapping[str, t.ApiJsonValue]]:
        """Return health information."""
        return r[Mapping[str, t.ApiJsonValue]].ok({
            "status": "healthy",
            "timestamp": u.generate_iso_timestamp(),
            "storage_accessible": True,
            "size": len(self._state.entries),
            "operations_count": self._state.operations_count,
        })

    def info(self) -> p.Result[Mapping[str, t.ApiJsonValue]]:
        """Return storage configuration and runtime info."""
        return r[Mapping[str, t.ApiJsonValue]].ok({
            "namespace": self.namespace,
            "backend": self.backend,
            "size": len(self._state.entries),
            "created_at": self._state.created_at,
            "max_size": self._settings.max_size,
            "default_ttl": self._settings.default_ttl,
            "operations_count": self._state.operations_count,
        })

    def items(self) -> p.Result[Sequence[t.Pair[str, t.ApiJsonValue]]]:
        """Return stored key-value pairs."""
        self._cleanup_expired_entries()
        return r[Sequence[t.Pair[str, t.ApiJsonValue]]].ok(
            [(key, entry.value) for key, entry in self._state.entries.items()],
        )

    def keys(self) -> p.Result[t.StrSequence]:
        """Return stored keys."""
        self._cleanup_expired_entries()
        return r[t.StrSequence].ok(list(self._state.entries.keys()))

    def metrics(self) -> p.Result[Mapping[str, t.ApiJsonValue]]:
        """Return canonical storage metrics payload."""
        stats = self._stats_model()
        return r[Mapping[str, t.ApiJsonValue]].ok({
            "total_operations": stats.total_operations,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
            "hit_ratio": stats.hit_ratio,
            "storage_size": stats.storage_size,
            "memory_usage": stats.memory_usage,
            "namespace": stats.namespace,
        })

    def serialize_json(self, data: t.ApiJsonValue) -> p.Result[str]:
        """Serialize one JSON-compatible value."""
        if data is None:
            return r[str].ok("null")
        return u.try_(
            lambda: t.Api.API_JSON_VALUE_ADAPTER.dump_json(data).decode("utf-8"),
            catch=(ValueError, TypeError),
        ).map_error(lambda error: f"JSON serialization failed: {error}")

    def set(
        self,
        key: str,
        value: t.ApiJsonValue,
        timeout: int | None = None,
        ttl: int | None = None,
    ) -> p.Result[bool]:
        """Store one value with optional TTL."""
        key_result = self._validate_key(key)
        if key_result.failure:
            return r[bool].fail(key_result.error)
        ttl_result = self._resolve_ttl(timeout=timeout, ttl=ttl)
        if ttl_result.failure:
            return r[bool].fail(ttl_result.error)
        normalized_key = key_result.value
        self._cleanup_expired_entries()
        if (
            self._settings.max_size is not None
            and normalized_key not in self._state.entries
            and len(self._state.entries) >= self._settings.max_size
        ):
            return r[bool].fail("Storage is full")
        metadata_result = u.load(
            m.Api.Storage.Metadata,
            {
                "value": value,
                "timestamp": u.generate_iso_timestamp(),
                "ttl": ttl_result.value,
                "created_at": time.time(),
            },
        )
        if metadata_result.failure:
            return r[bool].fail(metadata_result.error or "Metadata validation failed")
        self._state.entries[normalized_key] = metadata_result.value
        self._record_operation()
        return r[bool].ok(True)

    def size(self) -> p.Result[int]:
        """Return current storage size."""
        self._cleanup_expired_entries()
        return r[int].ok(len(self._state.entries))

    def values(self) -> p.Result[Sequence[t.ApiJsonValue]]:
        """Return stored values."""
        self._cleanup_expired_entries()
        return r[Sequence[t.ApiJsonValue]].ok(
            [entry.value for entry in self._state.entries.values()],
        )

    @staticmethod
    def _validate_key(key: str) -> p.Result[str]:
        """Validate a public storage key."""
        key_result = u.validate_value(t.Api.STRING_ADAPTER, key)
        if key_result.failure:
            return r[str].fail(key_result.error or "Invalid storage key")
        normalized_key = key_result.value.strip()
        if not normalized_key:
            return r[str].fail("Key must be non-empty string")
        return r[str].ok(normalized_key)

    def _cleanup_expired_entries(self) -> int:
        """Remove expired entries and return the number removed."""
        expired_keys = [
            key for key, entry in self._state.entries.items() if entry.expired
        ]
        for key in expired_keys:
            del self._state.entries[key]
        return len(expired_keys)

    def _estimate_memory_usage(self) -> int:
        """Estimate in-memory payload size through canonical JSON serialization."""
        return sum(
            len(t.Api.STRING_ADAPTER.dump_json(key))
            + len(t.Api.API_JSON_VALUE_ADAPTER.dump_json(entry.value))
            for key, entry in self._state.entries.items()
        )

    def _record_operation(self) -> None:
        """Increment storage operation count."""
        self._state.operations_count += 1

    def _resolve_settings(
        self,
        settings: m.Api.Storage.Settings | Mapping[str, t.ValueOrModel] | None,
        overrides: Mapping[str, t.ValueOrModel],
    ) -> m.Api.Storage.Settings:
        """Resolve one canonical storage settings model."""
        if isinstance(settings, m.Api.Storage.Settings):
            return settings.model_copy(update=dict(overrides) or None)
        payload: dict[str, t.ValueOrModel] = {}
        if isinstance(settings, Mapping):
            payload.update(settings)
        elif settings is not None:
            msg = "Storage settings must be a mapping or Storage.Settings model"
            raise TypeError(msg)
        payload.update(overrides)
        if not payload:
            return m.Api.Storage.Settings()
        settings_result = u.load(
            m.Api.Storage.Settings,
            t.ConfigMap(root=payload),
        )
        if settings_result.failure:
            msg = settings_result.error or "Storage settings validation failed"
            raise ValueError(msg)
        return settings_result.value

    def _resolve_ttl(
        self,
        *,
        timeout: int | None = None,
        ttl: int | None = None,
    ) -> p.Result[int | None]:
        """Resolve one TTL value from public inputs and settings."""
        resolved = timeout if timeout is not None else ttl
        if resolved is None:
            resolved = self._settings.default_ttl
        if resolved is None:
            return r[int | None].ok(None)
        if resolved <= 0:
            return r[int | None].fail("TTL must be positive")
        return r[int | None].ok(resolved)

    def _stats_model(self) -> m.Api.Storage.Stats:
        """Materialize one stats model from centralized runtime state."""
        return m.Api.Storage.Stats(
            total_operations=self._state.operations_count,
            cache_hits=self._state.cache_hits,
            cache_misses=self._state.cache_misses,
            storage_size=len(self._state.entries),
            memory_usage=self._estimate_memory_usage(),
            namespace=self.namespace,
        )


__all__: list[str] = ["FlextApiStorage"]
