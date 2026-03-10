"""Generic HTTP storage with features using external libraries.

Delegates to:
- pydantic: data validation and serialization
- json: JSON handling
- flext-core: patterns and utilities

Flexible features:
- Batch operations
- TTL/expiration management
- Metrics and statistics
- Health monitoring
- Event emission
- JSON serialization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import json
import time
from collections.abc import Mapping
from typing import Self

from flext_core import FlextLogger, FlextRuntime, r, u
from pydantic import BaseModel, ConfigDict, ValidationError

from flext_api import m, t


class FlextApiStorage:
    """Generic HTTP storage with features via library delegation.

    Delegates to:
    - pydantic for data models and validation
    - json for serialization
    - flext-core utilities for timestamps
    - Python built-ins for core storage

    Flexible features:
    - TTL-based expiration
    - Batch operations
    - Metrics collection
    - Health monitoring
    - Event tracking
    """

    model_config = ConfigDict(frozen=False, arbitrary_types_allowed=True)
    _storage: dict[str, t.ApiJsonValue]
    _expiry_times: dict[str, float]
    _stats: m.Api.Storage.Stats
    _operations_count: int
    _created_at: str
    _namespace: str
    _max_size: int | None
    _default_ttl: float | None
    _backend: str

    def __new__(
        cls, config: t.ApiJsonValue | None = None, **kwargs: t.ApiJsonValue
    ) -> Self:
        """Intercept config argument and convert to kwargs for FlextService V2."""
        instance = super().__new__(cls)
        if config is not None:
            object.__setattr__(instance, "_flext_storage_config", config)
        if kwargs:
            object.__setattr__(instance, "_flext_storage_kwargs", kwargs)
        return instance

    def __init__(
        self, config: t.ApiJsonValue | None = None, **kwargs: t.ApiJsonValue
    ) -> None:
        """Initialize storage with config using Pydantic."""
        self.logger = FlextLogger(__name__)
        config_obj, storage_kwargs = self._extract_init_params(config, kwargs)
        max_size_val, default_ttl_val = self._extract_storage_kwargs(storage_kwargs)
        storage_kwargs_typed: dict[str, t.ApiJsonValue] = {
            k: FlextRuntime.normalize_to_general_value(v)
            for k, v in storage_kwargs.items()
        }
        super().__init__(**storage_kwargs_typed)
        config_dict = self._normalize_config(config_obj)
        self._apply_config(config_dict, max_size_val, default_ttl_val)
        object.__setattr__(self, "_storage", {})
        object.__setattr__(self, "_expiry_times", {})
        object.__setattr__(self, "_stats", m.Storage.Stats(namespace=self._namespace))
        object.__setattr__(self, "_operations_count", 0)
        object.__setattr__(self, "_created_at", u.Generators.generate_iso_timestamp())

    @property
    def backend(self) -> str:
        """Get backend."""
        return self._backend

    @property
    def namespace(self) -> str:
        """Get namespace."""
        return self._namespace

    @staticmethod
    def _to_json_value(value: t.ContainerValue) -> t.ApiJsonValue:
        """Convert arbitrary value to JsonValue recursively."""
        normalized = FlextRuntime.normalize_to_general_value(value)
        if normalized is None or isinstance(normalized, (str, int, float, bool)):
            return normalized
        if isinstance(normalized, dict):
            converted: t.JsonObject = {}
            for key, item in normalized.items():
                converted[str(key)] = FlextApiStorage._to_json_value(item)
            return converted
        if isinstance(normalized, (list, tuple)):
            return [FlextApiStorage._to_json_value(item) for item in normalized]
        return str(normalized)

    def batch_delete(self, keys: list[str]) -> r[bool]:
        """Delete multiple keys efficiently."""
        try:
            all_deleted = True
            for key in keys:
                delete_result = self.delete(key)
                if delete_result.is_failure:
                    all_deleted = False
            if all_deleted:
                return r[bool].ok(value=True)
            return r[bool].fail("Some keys could not be deleted")
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[bool].fail(str(e))

    def batch_get(self, keys: list[str]) -> r[Mapping[str, t.ApiJsonValue]]:
        """Get multiple keys efficiently."""
        try:
            result_dict: dict[str, t.ApiJsonValue] = {}
            for key in keys:
                get_result = self.get(key)
                if get_result.is_success:
                    unwrapped = get_result.value
                    result_dict[key] = self._to_json_value(unwrapped)
            return r[Mapping[str, t.ApiJsonValue]].ok(result_dict)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[Mapping[str, t.ApiJsonValue]].fail(str(e))

    def batch_set(
        self, data: Mapping[str, t.ApiJsonValue], ttl: int | None = None
    ) -> r[bool]:
        """Set multiple keys efficiently using Pydantic validation."""
        try:
            for key, value in data.items():
                result = self.set(key, value, ttl=ttl)
                if result.is_failure:
                    return result
            return r[bool].ok(value=True)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[bool].fail(str(e))

    def cleanup_expired(self) -> r[int]:
        """Clean up expired entries (TTL management)."""
        try:
            initial_size = len(self._storage)
            self._cleanup_expired()
            removed = initial_size - len(self._storage)
            return r[int].ok(removed)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[int].fail(f"Cleanup failed: {e}")

    def clear(self) -> r[bool]:
        """Clear all storage."""
        self._storage.clear()
        self._expiry_times.clear()
        self._operations_count = 0
        return r[bool].ok(value=True)

    def delete(self, key: str) -> r[bool]:
        """Delete key from storage."""
        key_deleted = key in self._storage
        namespaced_key = self._key(key)
        namespaced_deleted = namespaced_key in self._storage
        if key in self._storage:
            del self._storage[key]
        if namespaced_key in self._storage:
            del self._storage[namespaced_key]
        if key in self._expiry_times:
            del self._expiry_times[key]
        self._operations_count += 1
        if key_deleted or namespaced_deleted:
            return r[bool].ok(value=True)
        return r[bool].fail(f"Key not found: {key}")

    def deserialize_json(self, json_str: str) -> r[t.ApiJsonValue]:
        """Deserialize from JSON using json library."""
        try:
            return r[t.ApiJsonValue].ok(json.loads(json_str))
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[t.ApiJsonValue].fail(f"JSON deserialization failed: {e}")

    def execute(self, *_args: t.ApiJsonValue, **_kwargs: t.ApiJsonValue) -> r[bool]:
        """Service lifecycle execution."""
        return r[bool].ok(value=True)

    def exists(self, key: str) -> r[bool]:
        """Check if key exists and not expired."""
        self._cleanup_expired()
        direct_exists = key in self._storage
        if direct_exists:
            return r[bool].ok(value=True)
        namespaced_exists = self._key(key) in self._storage
        return r[bool].ok(namespaced_exists)

    def get(self, key: str) -> r[t.ApiJsonValue]:
        """Retrieve value with expiration checking."""
        if not key:
            return r[t.ApiJsonValue].fail("Key must be non-empty string")
        self._cleanup_expired()
        self._operations_count += 1
        if key in self._storage:
            value = self._storage[key]
            self._stats = m.Storage.Stats(
                total_operations=self._stats.total_operations,
                cache_hits=self._stats.cache_hits + 1,
                cache_misses=self._stats.cache_misses,
                hit_ratio=self._stats.hit_ratio,
                storage_size=self._stats.storage_size,
                memory_usage=self._stats.memory_usage,
                namespace=self._stats.namespace,
            )
            return r[t.ApiJsonValue].ok(value)
        namespaced_key = self._key(key)
        if namespaced_key in self._storage:
            result = self._process_namespaced_entry(namespaced_key, key)
            if result.is_success:
                return result
        self._stats = m.Storage.Stats(
            total_operations=self._stats.total_operations,
            cache_hits=self._stats.cache_hits,
            cache_misses=self._stats.cache_misses + 1,
            hit_ratio=self._stats.hit_ratio,
            storage_size=self._stats.storage_size,
            memory_usage=self._stats.memory_usage,
            namespace=self._stats.namespace,
        )
        return r[t.ApiJsonValue].fail(f"Key not found: {key}")

    def get_cache_stats(self) -> r[t.Api.CacheDict]:
        """Get cache statistics using Pydantic validation."""
        try:
            return r[t.Api.CacheDict].ok({
                "size": len(self._storage),
                "backend": self._backend,
                "hits": self._stats.cache_hits,
                "misses": self._stats.cache_misses,
            })
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[t.Api.CacheDict].fail(str(e))

    def get_storage_metrics(self) -> r[t.Api.MetricsDict]:
        """Get complete storage metrics."""
        try:
            return r[t.Api.MetricsDict].ok({
                "total_operations": self._operations_count,
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
            })
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[t.Api.MetricsDict].fail(str(e))

    def get_storage_statistics(self) -> r[Mapping[str, float]]:
        """Get storage statistics with hit ratio calculation."""
        try:
            hit_ratio = (
                self._stats.cache_hits / self._stats.total_operations
                if self._stats.total_operations > 0
                else 0.0
            )
            return r[Mapping[str, float]].ok({
                "total_operations": float(self._operations_count),
                "cache_hits": float(self._stats.cache_hits),
                "cache_misses": float(self._stats.cache_misses),
                "hit_ratio": hit_ratio,
                "storage_size": float(len(self._storage)),
                "memory_usage": float(len(str(self._storage))),
            })
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[Mapping[str, float]].fail(str(e))

    def health_check(self) -> r[Mapping[str, t.ApiJsonValue]]:
        """Perform health check with metrics."""
        try:
            return r[Mapping[str, t.ApiJsonValue]].ok({
                "status": "healthy",
                "timestamp": u.Generators.generate_iso_timestamp(),
                "storage_accessible": True,
                "size": len(self._storage),
                "operations_count": self._operations_count,
            })
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[Mapping[str, t.ApiJsonValue]].fail(str(e))

    def info(self) -> r[Mapping[str, t.ApiJsonValue]]:
        """Get storage information using Pydantic model."""
        try:
            return r[Mapping[str, t.ApiJsonValue]].ok({
                "namespace": self._namespace,
                "backend": self._backend,
                "size": len(self._storage),
                "created_at": self._created_at,
                "max_size": self._max_size,
                "default_ttl": self._default_ttl,
                "operations_count": self._operations_count,
            })
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[Mapping[str, t.ApiJsonValue]].fail(str(e))

    def items(self) -> r[list[tuple[str, t.ApiJsonValue]]]:
        """Get all key-value pairs."""
        self._cleanup_expired()
        return r[list[tuple[str, t.ApiJsonValue]]].ok(list(self._storage.items()))

    def keys(self) -> r[list[str]]:
        """Get all non-namespaced keys."""
        self._cleanup_expired()

        def key_not_namespaced(k: str) -> bool:
            return not k.startswith(f"{self._namespace}:")

        filtered_keys = u.Collection.filter(
            list(self._storage.keys()), key_not_namespaced
        )
        return r[list[str]].ok(list(filtered_keys))

    def metrics(self) -> r[Mapping[str, t.ApiJsonValue]]:
        """Get storage metrics using Pydantic stats model."""
        try:
            hit_ratio = 0.0
            if self._stats.total_operations > 0:
                hit_ratio = self._stats.cache_hits / self._stats.total_operations
            self._stats = m.Storage.Stats(
                total_operations=self._stats.total_operations,
                cache_hits=self._stats.cache_hits,
                cache_misses=self._stats.cache_misses,
                hit_ratio=hit_ratio,
                storage_size=len(self._storage),
                memory_usage=len(str(self._storage)),
                namespace=self._stats.namespace,
            )
            stats_dict: dict[str, t.ApiJsonValue] = {
                "total_operations": self._stats.total_operations,
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
                "hit_ratio": self._stats.hit_ratio,
                "storage_size": self._stats.storage_size,
                "memory_usage": self._stats.memory_usage,
                "namespace": self._stats.namespace,
            }
            return r[Mapping[str, t.ApiJsonValue]].ok(stats_dict)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[Mapping[str, t.ApiJsonValue]].fail(str(e))

    def serialize_json(self, data: t.ApiJsonValue) -> r[str]:
        """Serialize to JSON using json library."""
        try:
            return r[str].ok(json.dumps(data, default=str))
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[str].fail(f"JSON serialization failed: {e}")

    def set(
        self,
        key: str,
        value: t.ApiJsonValue,
        timeout: int | None = None,
        ttl: int | None = None,
    ) -> r[bool]:
        """Store value with TTL using Pydantic metadata."""
        if not key:
            return r[bool].fail("Key must be non-empty string")
        ttl_val = (
            timeout
            if timeout is not None
            else ttl
            if ttl is not None
            else self._default_ttl
        )
        try:
            metadata = m.Storage.Metadata(
                value=value,
                timestamp=u.Generators.generate_iso_timestamp(),
                ttl=ttl_val,
            )
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            return r[bool].fail(f"Metadata validation failed: {e}")
        json_value = self._to_json_value(value)
        self._storage[key] = json_value
        value_json = self._to_json_value(metadata.value)
        ttl_json: t.ApiJsonValue = metadata.ttl if metadata.ttl is not None else None
        metadata_dict: dict[str, t.ApiJsonValue] = {
            "value": value_json,
            "timestamp": metadata.timestamp,
            "ttl": ttl_json,
            "created_at": metadata.created_at,
        }
        self._storage[self._key(key)] = metadata_dict
        if ttl_val is not None:
            self._expiry_times[key] = time.time() + ttl_val
        self._operations_count += 1
        self._stats = m.Storage.Stats(
            total_operations=self._operations_count,
            cache_hits=self._stats.cache_hits,
            cache_misses=self._stats.cache_misses,
            hit_ratio=self._stats.hit_ratio,
            storage_size=self._stats.storage_size,
            memory_usage=self._stats.memory_usage,
            namespace=self._stats.namespace,
        )
        return r[bool].ok(value=True)

    def size(self) -> r[int]:
        """Get storage size with expiration cleanup."""
        self._cleanup_expired()
        return r[int].ok(len(self._storage))

    def values(self) -> r[list[t.ApiJsonValue]]:
        """Get all values."""
        self._cleanup_expired()
        return r[list[t.ApiJsonValue]].ok(list(self._storage.values()))

    def _apply_config(
        self,
        config_dict: t.Api.StorageDict,
        max_size_val: t.ApiJsonValue | None,
        default_ttl_val: t.ApiJsonValue | None,
    ) -> None:
        """Apply normalized config to instance attributes - no fallbacks."""
        namespace_result = self._extract_namespace(config_dict)
        if namespace_result.is_failure:
            error_msg = f"Failed to extract namespace: {namespace_result.error}"
            raise ValueError(error_msg)
        self._namespace = namespace_result.value
        max_size_result = self._extract_max_size(config_dict, max_size_val)
        if max_size_result.is_failure:
            error_msg = f"Failed to extract max_size: {max_size_result.error}"
            raise ValueError(error_msg)
        max_size_value = max_size_result.value
        self._max_size = None if max_size_value == -1 else max_size_value
        default_ttl_result = self._extract_default_ttl(config_dict, default_ttl_val)
        if default_ttl_result.is_failure:
            error_msg = f"Failed to extract default_ttl: {default_ttl_result.error}"
            raise ValueError(error_msg)
        default_ttl_value = default_ttl_result.value
        self._default_ttl = None if default_ttl_value == -1 else default_ttl_value
        backend_result = self._extract_backend(config_dict)
        if backend_result.is_failure:
            error_msg = f"Failed to extract backend: {backend_result.error}"
            raise ValueError(error_msg)
        self._backend = backend_result.value

    def _cleanup_expired(self) -> None:
        """Remove expired entries (TTL management)."""
        current_time = time.time()
        expired_keys = [
            k for k, expiry in self._expiry_times.items() if expiry < current_time
        ]
        for k in expired_keys:
            if k in self._storage:
                del self._storage[k]
            if k in self._expiry_times:
                del self._expiry_times[k]

    def _convert_to_int(self, value: t.ApiJsonValue) -> int | None:
        """Convert value to int or return None if conversion fails."""
        if value is None:
            return None
        try:
            return int(str(value))
        except (ValueError, TypeError):
            return None

    def _extract_backend(self, config_dict: t.Api.StorageDict) -> r[str]:
        """Extract backend from config with validation - uses default if not specified."""
        if "backend" in config_dict:
            backend_val = config_dict["backend"]
            match backend_val:
                case str() as s:
                    if s:
                        return r[str].ok(s)
                    return r[str].fail("Backend cannot be empty")
                case _:
                    return r[str].fail(f"Invalid backend type: {type(backend_val)}")
        return r[str].ok("memory")

    def _extract_config_field(
        self, config_obj: BaseModel, field_name: str, default_value: str
    ) -> str:
        """Extract string field from config object."""
        field_value = config_obj.model_dump().get(field_name)
        if isinstance(field_value, str):
            return field_value
        return default_value

    def _extract_default_ttl(
        self, config_dict: t.Api.StorageDict, default_ttl_val: t.ApiJsonValue | None
    ) -> r[int]:
        """Extract default_ttl preferring parameter over config - no fallbacks.

        Returns r[int] with a sentinel value (-1) when default_ttl is not specified.
        The caller should check for -1 to determine if default_ttl was not set.
        """
        if default_ttl_val is not None:
            try:
                ttl_int = int(str(default_ttl_val))
                if ttl_int > 0:
                    return r[int].ok(ttl_int)
                return r[int].fail(f"Default TTL must be positive, got: {ttl_int}")
            except (ValueError, TypeError) as e:
                return r[int].fail(f"Invalid default_ttl value: {e}")
        if "default_ttl" in config_dict:
            default_ttl_config = config_dict["default_ttl"]
            if default_ttl_config is not None:
                try:
                    ttl_int = int(str(default_ttl_config))
                    if ttl_int > 0:
                        return r[int].ok(ttl_int)
                    return r[int].fail(f"Default TTL must be positive, got: {ttl_int}")
                except (ValueError, TypeError) as e:
                    return r[int].fail(f"Invalid default_ttl value: {e}")
        return r[int].ok(-1)

    def _extract_init_params(
        self, config: t.ApiJsonValue | None, kwargs: Mapping[str, t.ApiJsonValue]
    ) -> tuple[t.ApiJsonValue | None, Mapping[str, t.ApiJsonValue]]:
        """Extract config and kwargs from __new__ or parameters."""
        config_obj = getattr(self, "_flext_storage_config", None)
        if config_obj is None:
            config_obj = config
        with contextlib.suppress(AttributeError):
            delattr(self, "_flext_storage_config")
        storage_kwargs = getattr(self, "_flext_storage_kwargs", None)
        if storage_kwargs is None:
            storage_kwargs = kwargs
        with contextlib.suppress(AttributeError):
            delattr(self, "_flext_storage_kwargs")
        return (config_obj, storage_kwargs)

    def _extract_max_size(
        self, config_dict: t.Api.StorageDict, max_size_val: t.ApiJsonValue | None
    ) -> r[int]:
        """Extract max_size preferring parameter over config - no fallbacks.

        Returns r[int] with a sentinel value (-1) when max_size is not specified.
        The caller should check for -1 to determine if max_size was not set.
        """
        if max_size_val is not None:
            try:
                max_size_int = int(str(max_size_val))
                if max_size_int > 0:
                    return r[int].ok(max_size_int)
                return r[int].fail(f"Max size must be positive, got: {max_size_int}")
            except (ValueError, TypeError) as e:
                return r[int].fail(f"Invalid max_size value: {e}")
        if "max_size" in config_dict:
            max_size_config = config_dict["max_size"]
            if max_size_config is not None:
                try:
                    max_size_int = int(str(max_size_config))
                    if max_size_int > 0:
                        return r[int].ok(max_size_int)
                    return r[int].fail(
                        f"Max size must be positive, got: {max_size_int}"
                    )
                except (ValueError, TypeError) as e:
                    return r[int].fail(f"Invalid max_size value: {e}")
        return r[int].ok(-1)

    def _extract_namespace(self, config_dict: t.Api.StorageDict) -> r[str]:
        """Extract namespace from config with validation - uses default if not specified."""
        if "namespace" in config_dict:
            namespace_val = config_dict["namespace"]
            match namespace_val:
                case str() as s:
                    if s:
                        return r[str].ok(s)
                    return r[str].fail("Namespace cannot be empty")
                case _:
                    return r[str].fail(f"Invalid namespace type: {type(namespace_val)}")
        return r[str].ok("flext_api")

    def _extract_optional_config_field(
        self, config_obj: BaseModel, field_name: str
    ) -> t.ContainerValue | None:
        """Extract optional field from config object."""
        field_value = config_obj.model_dump().get(field_name)
        if field_value is not None:
            return FlextRuntime.normalize_to_general_value(field_value)
        return None

    def _extract_storage_kwargs(
        self, storage_kwargs: Mapping[str, t.ApiJsonValue]
    ) -> tuple[t.ApiJsonValue | None, t.ApiJsonValue | None]:
        """Extract storage-specific kwargs before passing to super."""
        storage_kwargs_dict = dict(storage_kwargs)
        max_size_val = storage_kwargs_dict.pop("max_size", None)
        default_ttl_val = storage_kwargs_dict.pop("default_ttl", None)
        self._flext_storage_kwargs = storage_kwargs_dict
        return (max_size_val, default_ttl_val)

    def _key(self, key: str) -> str:
        """Create namespaced key."""
        return f"{self._namespace}:{key}"

    def _normalize_config(self, config_obj: t.ApiJsonValue | None) -> t.Api.StorageDict:
        """Normalize config object to dictionary."""
        if config_obj is None:
            return {}
        if isinstance(config_obj, dict):
            normalized: t.Api.StorageDict = {}
            for key, value in config_obj.items():
                key_str = str(key)
                if value is None or isinstance(value, (str, int, bool)):
                    normalized[key_str] = value
                elif isinstance(value, float):
                    normalized[key_str] = int(value)
                else:
                    normalized[key_str] = str(value)
            return normalized
        if isinstance(config_obj, BaseModel):
            namespace_str = self._extract_config_field(config_obj, "namespace", "flext")
            backend_str = self._extract_config_field(config_obj, "backend", "memory")
            max_size_val = self._extract_optional_config_field(config_obj, "max_size")
            default_ttl_val = self._extract_optional_config_field(
                config_obj, "default_ttl"
            )
            return {
                "namespace": namespace_str,
                "backend": backend_str,
                "max_size": self._convert_to_int(max_size_val),
                "default_ttl": self._convert_to_int(default_ttl_val),
            }
        return {}

    def _process_namespaced_entry(
        self, namespaced_key: str, key: str
    ) -> r[t.ApiJsonValue]:
        """Process a namespaced storage entry with metadata validation."""
        data = self._storage[namespaced_key]
        try:
            if not isinstance(data, dict):
                return r[t.ApiJsonValue].fail(f"Invalid data format for key: {key}")
            ttl_value = data.get("ttl")
            ttl_int: int | None = None
            if ttl_value is not None:
                try:
                    ttl_int = int(str(ttl_value))
                except (ValueError, TypeError):
                    ttl_int = None
            created_at_value = data.get("created_at", 0.0)
            created_at_float = 0.0
            try:
                created_at_float = float(str(created_at_value))
            except (ValueError, TypeError):
                created_at_float = 0.0
            metadata = m.Storage.Metadata(
                value=data.get("value"),
                timestamp=str(data.get("timestamp", "")),
                ttl=ttl_int,
                created_at=created_at_float,
            )
            if not metadata.is_expired():
                self._stats = m.Storage.Stats(
                    total_operations=self._stats.total_operations,
                    cache_hits=self._stats.cache_hits + 1,
                    cache_misses=self._stats.cache_misses,
                    hit_ratio=self._stats.hit_ratio,
                    storage_size=self._stats.storage_size,
                    memory_usage=self._stats.memory_usage,
                    namespace=self._stats.namespace,
                )
                return r[t.ApiJsonValue].ok(metadata.value)
            if namespaced_key in self._storage:
                del self._storage[namespaced_key]
            if key in self._expiry_times:
                del self._expiry_times[key]
            return r[t.ApiJsonValue].fail(f"Key expired: {key}")
        except ValidationError as e:
            FlextLogger(__name__).error(
                "Metadata validation failed for storage entry",
                error=str(e),
                exception_type="ValidationError",
                key=key,
            )
            return r[t.ApiJsonValue].fail(
                f"ValidationError processing key '{key}': {e}"
            )
        except (KeyError, TypeError, AttributeError) as e:
            FlextLogger(__name__).error(
                "Failed to process namespaced storage entry",
                error=str(e),
                exception_type=type(e).__name__,
                key=key,
            )
            return r[t.ApiJsonValue].fail(
                f"{type(e).__name__} processing key '{key}': {e}"
            )


__all__ = ["FlextApiStorage"]
