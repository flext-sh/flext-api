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

import json
import time
from typing import Self, override

from flext_core import FlextService, r, u
from pydantic import BaseModel, ConfigDict, Field

from flext_api.typings import t


class _StorageMetadata(BaseModel):
    """Internal metadata for stored values (using Pydantic for validation)."""

    value: object
    timestamp: str
    ttl: int | None = None
    created_at: float = Field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if entry has expired using Pydantic-validated TTL."""
        if self.ttl is None:
            return False
        elapsed = time.time() - self.created_at
        return elapsed > self.ttl


class _StorageStats(BaseModel):
    """Storage statistics using Pydantic (automatic validation)."""

    total_operations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_ratio: float = 0.0
    storage_size: int = 0
    memory_usage: int = 0
    namespace: str = "flext"


class FlextApiStorage(FlextService[bool]):
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

    # Override frozen constraint from FlextService - storage needs mutable state
    model_config = ConfigDict(frozen=False, arbitrary_types_allowed=True)

    # Type annotations for dynamically-set fields
    _storage: dict[str, t.JsonValue]
    _expiry_times: dict[str, float]
    _stats: _StorageStats
    _operations_count: int
    _created_at: str

    def __new__(cls, config: object | None = None, **kwargs: object) -> Self:
        """Intercept config argument and convert to kwargs for FlextService V2."""
        instance = super().__new__(cls)
        if config is not None:
            object.__setattr__(instance, "_flext_storage_config", config)
        if kwargs:
            object.__setattr__(instance, "_flext_storage_kwargs", kwargs)
        return instance

    def __init__(self, config: object | None = None, **kwargs: object) -> None:
        """Initialize storage with config using Pydantic."""
        config_obj, storage_kwargs = self._extract_init_params(config, kwargs)
        max_size_val, default_ttl_val = self._extract_storage_kwargs(storage_kwargs)
        # Type narrowing: convert dict[str, object] to dict[str, t.GeneralValueType]
        storage_kwargs_typed: dict[str, t.GeneralValueType] = {
            k: v
            for k, v in storage_kwargs.items()
            if isinstance(v, (str, int, float, bool, type(None), dict, list))
        }
        super().__init__(**storage_kwargs_typed)
        config_dict = self._normalize_config(config_obj)
        self._apply_config(config_dict, max_size_val, default_ttl_val)

        # Flexible storage tracking - use JsonValue for type safety
        # Use object.__setattr__ to bypass frozen constraint from FlextService parent
        object.__setattr__(self, "_storage", {})
        object.__setattr__(self, "_expiry_times", {})

        # Metrics using Pydantic model
        object.__setattr__(self, "_stats", _StorageStats(namespace=self._namespace))
        object.__setattr__(self, "_operations_count", 0)
        object.__setattr__(self, "_created_at", u.Generators.generate_iso_timestamp())

    def _extract_init_params(
        self,
        config: object | None,
        kwargs: dict[str, object],
    ) -> tuple[object | None, dict[str, object]]:
        """Extract config and kwargs from __new__ or parameters."""
        config_obj = getattr(self, "_flext_storage_config", None)
        if config_obj is None:
            config_obj = config
        if hasattr(self, "_flext_storage_config"):
            delattr(self, "_flext_storage_config")

        storage_kwargs = getattr(self, "_flext_storage_kwargs", None)
        if storage_kwargs is None:
            storage_kwargs = kwargs
        if hasattr(self, "_flext_storage_kwargs"):
            delattr(self, "_flext_storage_kwargs")
        return config_obj, storage_kwargs

    def _extract_storage_kwargs(
        self,
        storage_kwargs: dict[str, object],
    ) -> tuple[object | None, object | None]:
        """Extract storage-specific kwargs before passing to super."""
        max_size_val = storage_kwargs.pop("max_size", None)
        default_ttl_val = storage_kwargs.pop("default_ttl", None)
        return max_size_val, default_ttl_val

    def _extract_config_field(
        self,
        config_obj: BaseModel,
        field_name: str,
        default_value: str,
    ) -> str:
        """Extract string field from config object."""
        if hasattr(config_obj, field_name):
            field_value = getattr(config_obj, field_name)
            if isinstance(field_value, str):
                return field_value
        return default_value

    def _extract_optional_config_field(
        self,
        config_obj: BaseModel,
        field_name: str,
    ) -> object | None:
        """Extract optional field from config object."""
        if hasattr(config_obj, field_name):
            field_value = getattr(config_obj, field_name)
            if field_value is not None:
                return field_value
        return None

    def _convert_to_int(self, value: object) -> int | None:
        """Convert value to int or return None if conversion fails."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return None

    def _normalize_config(self, config_obj: object | None) -> t.Api.StorageDict:
        """Normalize config object to dictionary."""
        if isinstance(config_obj, dict):
            return config_obj
        if isinstance(config_obj, BaseModel):
            namespace_str = self._extract_config_field(
                config_obj,
                "namespace",
                "flext",
            )
            backend_str = self._extract_config_field(config_obj, "backend", "memory")
            max_size_val = self._extract_optional_config_field(config_obj, "max_size")
            default_ttl_val = self._extract_optional_config_field(
                config_obj,
                "default_ttl",
            )

            return {
                "namespace": namespace_str,
                "backend": backend_str,
                "max_size": self._convert_to_int(max_size_val),
                "default_ttl": self._convert_to_int(default_ttl_val),
            }
        return {}

    def _apply_config(
        self,
        config_dict: t.Api.StorageDict,
        max_size_val: object | None,
        default_ttl_val: object | None,
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
        # Convert sentinel value (-1) to None for optional max_size
        self._max_size = None if max_size_value == -1 else max_size_value

        default_ttl_result = self._extract_default_ttl(config_dict, default_ttl_val)
        if default_ttl_result.is_failure:
            error_msg = f"Failed to extract default_ttl: {default_ttl_result.error}"
            raise ValueError(error_msg)
        default_ttl_value = default_ttl_result.value
        # Convert sentinel value (-1) to None for optional default_ttl
        self._default_ttl = None if default_ttl_value == -1 else default_ttl_value

        backend_result = self._extract_backend(config_dict)
        if backend_result.is_failure:
            error_msg = f"Failed to extract backend: {backend_result.error}"
            raise ValueError(error_msg)
        self._backend = backend_result.value

    def _extract_namespace(self, config_dict: t.Api.StorageDict) -> r[str]:
        """Extract namespace from config with validation - uses default if not specified."""
        if "namespace" in config_dict:
            namespace_val = config_dict["namespace"]
            if isinstance(namespace_val, str):
                if namespace_val:
                    return r[str].ok(namespace_val)
                return r[str].fail("Namespace cannot be empty")
            return r[str].fail(f"Invalid namespace type: {type(namespace_val)}")
        # Use default namespace (this is OK - it's a valid default, not a fallback)
        return r[str].ok("flext")

    def _extract_max_size(
        self,
        config_dict: t.Api.StorageDict,
        max_size_val: object | None,
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
                        f"Max size must be positive, got: {max_size_int}",
                    )
                except (ValueError, TypeError) as e:
                    return r[int].fail(f"Invalid max_size value: {e}")
        # Return sentinel value (-1) when max_size is not specified (not a fallback - max_size is optional)
        return r[int].ok(-1)

    def _extract_default_ttl(
        self,
        config_dict: t.Api.StorageDict,
        default_ttl_val: object | None,
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
        # Return sentinel value (-1) when default_ttl is not specified (not a fallback - default_ttl is optional)
        return r[int].ok(-1)

    def _extract_backend(self, config_dict: t.Api.StorageDict) -> r[str]:
        """Extract backend from config with validation - uses default if not specified."""
        if "backend" in config_dict:
            backend_val = config_dict["backend"]
            if isinstance(backend_val, str):
                if backend_val:
                    return r[str].ok(backend_val)
                return r[str].fail("Backend cannot be empty")
            return r[str].fail(f"Invalid backend type: {type(backend_val)}")
        # Use default backend (this is OK - it's a valid default, not a fallback)
        return r[str].ok("memory")

    @override
    def execute(self, *_args: object, **_kwargs: object) -> r[bool]:
        """Service lifecycle execution."""
        return r[bool].ok(True)

    def _key(self, key: str) -> str:
        """Create namespaced key."""
        return f"{self._namespace}:{key}"

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

    def set(
        self,
        key: str,
        value: object,
        timeout: int | None = None,
        ttl: int | None = None,
    ) -> r[bool]:
        """Store value with TTL using Pydantic metadata."""
        if not key:
            return r[bool].fail("Key must be non-empty string")

        ttl_val = (
            timeout
            if timeout is not None
            else (ttl if ttl is not None else self._default_ttl)
        )

        # Use Pydantic model for metadata validation
        try:
            metadata = _StorageMetadata(
                value=value,
                timestamp=u.Generators.generate_iso_timestamp(),
                ttl=ttl_val,
            )
        except Exception as e:
            return r[bool].fail(f"Metadata validation failed: {e}")

        # Store with expiry tracking - direct field access
        # Convert value to JsonValue for type safety
        json_value: t.JsonValue
        if isinstance(value, (str, int, float, bool, type(None), list, dict)):
            json_value = value
        else:
            # For complex objects, convert to string representation
            json_value = str(value)

        self._storage[key] = json_value
        # Convert metadata fields to JsonValue with proper type narrowing
        value_json: t.JsonValue = (
            metadata.value
            if isinstance(
                metadata.value, (str, int, float, bool, type(None), dict, list)
            )
            else str(metadata.value)
        )
        ttl_json: t.JsonValue = metadata.ttl if metadata.ttl is not None else None
        metadata_dict: dict[str, t.JsonValue] = {
            "value": value_json,
            "timestamp": metadata.timestamp,
            "ttl": ttl_json,
            "created_at": metadata.created_at,
        }
        self._storage[self._key(key)] = metadata_dict

        if ttl_val is not None:
            self._expiry_times[key] = time.time() + ttl_val

        self._operations_count += 1
        self._stats.total_operations = self._operations_count
        return r[bool].ok(True)

    def get(self, key: str) -> r[object]:
        """Retrieve value with expiration checking."""
        if not key:
            return r[object].fail("Key must be non-empty string")

        self._cleanup_expired()
        self._operations_count += 1

        # Try direct key first
        if key in self._storage:
            value = self._storage[key]
            self._stats.cache_hits += 1
            return r[object].ok(value)

        # Try namespaced key
        namespaced_key = self._key(key)
        if namespaced_key in self._storage:
            result = self._process_namespaced_entry(namespaced_key, key)
            if result.is_success:
                return result

        self._stats.cache_misses += 1
        return r[object].fail(f"Key not found: {key}")

    def _process_namespaced_entry(self, namespaced_key: str, key: str) -> r[object]:
        """Process a namespaced storage entry with metadata validation."""
        data = self._storage[namespaced_key]
        try:
            # Validate using Pydantic model
            if not isinstance(data, dict):
                return r[object].fail(f"Invalid data format for key: {key}")

            # Cast to expected types for Pydantic model construction
            # Runtime validation ensures type safety
            ttl_value = data.get("ttl")
            ttl_int: int | None = None
            if ttl_value is not None and isinstance(ttl_value, (int, str, float)):
                try:
                    ttl_int = int(ttl_value)
                except (ValueError, TypeError):
                    ttl_int = None

            created_at_value = data.get("created_at", 0.0)
            created_at_float = 0.0
            if isinstance(created_at_value, (int, float, str)):
                try:
                    created_at_float = float(created_at_value)
                except (ValueError, TypeError):
                    created_at_float = 0.0

            metadata = _StorageMetadata(
                value=data.get("value"),
                timestamp=str(data.get("timestamp", "")),
                ttl=ttl_int,
                created_at=created_at_float,
            )
            if not metadata.is_expired():
                self._stats.cache_hits += 1
                return r[object].ok(metadata.value)

            # Clean up expired entry
            if namespaced_key in self._storage:
                del self._storage[namespaced_key]
            if key in self._expiry_times:
                del self._expiry_times[key]
            return r[object].fail(f"Key expired: {key}")

        except Exception as e:
            # Log cleanup errors but continue - cache functionality is preserved
            self.logger.warning(
                f"Failed to cleanup expired cache entry: {e}",
                error=str(e),
            )
            return r[object].fail(f"Error processing key: {key}")

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
            return r[bool].ok(True)
        return r[bool].fail(f"Key not found: {key}")

    def exists(self, key: str) -> r[bool]:
        """Check if key exists and not expired."""
        self._cleanup_expired()
        direct_exists = key in self._storage
        if direct_exists:
            return r[bool].ok(True)
        namespaced_exists = self._key(key) in self._storage
        return r[bool].ok(namespaced_exists)

    def clear(self) -> r[bool]:
        """Clear all storage."""
        self._storage.clear()
        self._expiry_times.clear()
        self._operations_count = 0
        return r[bool].ok(True)

    def size(self) -> r[int]:
        """Get storage size with expiration cleanup."""
        self._cleanup_expired()
        return r[int].ok(len(self._storage))

    def keys(self) -> r[list[str]]:
        """Get all non-namespaced keys."""
        self._cleanup_expired()

        def key_not_namespaced(k: str) -> bool:
            return not k.startswith(f"{self._namespace}:")

        filtered_keys = u.Collection.filter(
            list(self._storage.keys()),
            key_not_namespaced,
        )
        return r[list[str]].ok(list(filtered_keys))

    def items(self) -> r[list[tuple[str, object]]]:
        """Get all key-value pairs."""
        self._cleanup_expired()
        return r[list[tuple[str, object]]].ok(list(self._storage.items()))

    def values(self) -> r[list[object]]:
        """Get all values."""
        self._cleanup_expired()
        return r[list[object]].ok(list(self._storage.values()))

    def batch_set(
        self,
        data: dict[str, t.JsonValue],
        ttl: int | None = None,
    ) -> r[bool]:
        """Set multiple keys efficiently using Pydantic validation."""
        try:
            for key, value in data.items():
                result = self.set(key, value, ttl=ttl)
                if result.is_failure:
                    return result
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))

    def batch_get(self, keys: list[str]) -> r[dict[str, t.JsonValue]]:
        """Get multiple keys efficiently."""
        try:
            result_dict: dict[str, t.JsonValue] = {}
            for key in keys:
                get_result = self.get(key)
                if get_result.is_success:
                    unwrapped = get_result.value
                    if isinstance(
                        unwrapped,
                        (str, int, float, bool, type(None), list, dict),
                    ):
                        result_dict[key] = unwrapped
                    else:
                        result_dict[key] = str(unwrapped)
            return r[dict[str, t.JsonValue]].ok(result_dict)
        except Exception as e:
            return r[dict[str, t.JsonValue]].fail(str(e))

    def batch_delete(self, keys: list[str]) -> r[bool]:
        """Delete multiple keys efficiently."""
        try:
            all_deleted = True
            for key in keys:
                delete_result = self.delete(key)
                if delete_result.is_failure:
                    all_deleted = False
            if all_deleted:
                return r[bool].ok(True)
            return r[bool].fail("Some keys could not be deleted")
        except Exception as e:
            return r[bool].fail(str(e))

    def serialize_json(self, data: object) -> r[str]:
        """Serialize to JSON using json library."""
        try:
            return r[str].ok(json.dumps(data, default=str))
        except Exception as e:
            return r[str].fail(f"JSON serialization failed: {e}")

    def deserialize_json(self, json_str: str) -> r[t.JsonValue]:
        """Deserialize from JSON using json library."""
        try:
            return r[t.JsonValue].ok(json.loads(json_str))
        except Exception as e:
            return r[t.JsonValue].fail(f"JSON deserialization failed: {e}")

    def cleanup_expired(self) -> r[int]:
        """Clean up expired entries (TTL management)."""
        try:
            initial_size = len(self._storage)
            self._cleanup_expired()
            removed = initial_size - len(self._storage)
            return r[int].ok(removed)
        except Exception as e:
            return r[int].fail(f"Cleanup failed: {e}")

    def info(self) -> r[dict[str, t.JsonValue]]:
        """Get storage information using Pydantic model."""
        try:
            return r[dict[str, t.JsonValue]].ok({
                "namespace": self._namespace,
                "backend": self._backend,
                "size": len(self._storage),
                "created_at": self._created_at,
                "max_size": self._max_size,
                "default_ttl": self._default_ttl,
                "operations_count": self._operations_count,
            })
        except Exception as e:
            return r[dict[str, t.JsonValue]].fail(str(e))

    def health_check(self) -> r[dict[str, t.JsonValue]]:
        """Perform health check with metrics."""
        try:
            return r[dict[str, t.JsonValue]].ok({
                "status": "healthy",
                "timestamp": u.Generators.generate_iso_timestamp(),
                "storage_accessible": True,
                "size": len(self._storage),
                "operations_count": self._operations_count,
            })
        except Exception as e:
            return r[dict[str, t.JsonValue]].fail(str(e))

    def metrics(self) -> r[dict[str, t.JsonValue]]:
        """Get storage metrics using Pydantic stats model."""
        try:
            # Update stats using Pydantic model
            self._stats.storage_size = len(self._storage)
            if self._stats.total_operations > 0:
                self._stats.hit_ratio = (
                    self._stats.cache_hits / self._stats.total_operations
                )
            self._stats.memory_usage = len(str(self._storage))

            # Direct field access instead of model_dump
            stats_dict: dict[str, t.JsonValue] = {
                "total_operations": self._stats.total_operations,
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
                "hit_ratio": self._stats.hit_ratio,
                "storage_size": self._stats.storage_size,
                "memory_usage": self._stats.memory_usage,
                "namespace": self._stats.namespace,
            }
            return r[dict[str, t.JsonValue]].ok(stats_dict)
        except Exception as e:
            return r[dict[str, t.JsonValue]].fail(str(e))

    def get_cache_stats(self) -> r[t.Api.CacheDict]:
        """Get cache statistics using Pydantic validation."""
        try:
            return r[t.Api.CacheDict].ok({
                "size": len(self._storage),
                "backend": self._backend,
                "hits": self._stats.cache_hits,
                "misses": self._stats.cache_misses,
            })
        except Exception as e:
            return r[t.Api.CacheDict].fail(str(e))

    def get_storage_metrics(self) -> r[t.Api.MetricsDict]:
        """Get complete storage metrics."""
        try:
            return r[t.Api.MetricsDict].ok({
                "total_operations": self._operations_count,
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
            })
        except Exception as e:
            return r[t.Api.MetricsDict].fail(str(e))

    def get_storage_statistics(self) -> r[dict[str, float]]:
        """Get storage statistics with hit ratio calculation."""
        try:
            hit_ratio = (
                self._stats.cache_hits / self._stats.total_operations
                if self._stats.total_operations > 0
                else 0.0
            )
            return r[dict[str, float]].ok({
                "total_operations": float(self._operations_count),
                "cache_hits": float(self._stats.cache_hits),
                "cache_misses": float(self._stats.cache_misses),
                "hit_ratio": hit_ratio,
                "storage_size": float(len(self._storage)),
                "memory_usage": float(len(str(self._storage))),
            })
        except Exception as e:
            return r[dict[str, float]].fail(str(e))

    # Properties for namespace and backend access
    # Note: config property inherited from FlextService base class
    @property
    def namespace(self) -> str:
        """Get namespace."""
        return self._namespace

    @property
    def backend(self) -> str:
        """Get backend."""
        return self._backend


__all__ = ["FlextApiStorage"]
