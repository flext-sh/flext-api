#!/usr/bin/env python3
"""FlextApi Universal API Client - Plugin System.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive plugin system for FlextApi client with logging, retry,
caching, metrics, circuit breaker and custom plugins.
"""

from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from flext_core import get_logger

if TYPE_CHECKING:
    from flext_api.client.core import FlextApiClientRequest, FlextApiClientResponse

logger = get_logger(__name__)


# ==============================================================================
# PLUGIN BASE CLASS
# ==============================================================================

class FlextApiPlugin(ABC):
    """Abstract base class for FlextApi client plugins."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__
        self.enabled = True
        self._metrics: dict[str, Any] = {}

    @abstractmethod
    async def before_request(self, request: FlextApiClientRequest) -> None:
        """Called before request execution."""

    @abstractmethod
    async def after_request(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Called after successful request."""

    @abstractmethod
    async def on_error(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Called when request fails."""

    def get_metrics(self) -> dict[str, Any]:
        """Get plugin metrics."""
        return self._metrics.copy()

    def reset_metrics(self) -> None:
        """Reset plugin metrics."""
        self._metrics.clear()


# ==============================================================================
# LOGGING PLUGIN
# ==============================================================================

@dataclass
class FlextApiLoggingConfig:
    """Configuration for logging plugin."""

    log_requests: bool = True
    log_responses: bool = True
    log_headers: bool = True
    log_body: bool = True
    log_performance: bool = True
    max_body_length: int = 1000
    sensitive_headers: list[str] = field(default_factory=lambda: ["authorization", "x-api-key", "cookie"])


class FlextApiLoggingPlugin(FlextApiPlugin):
    """Plugin for comprehensive request/response logging."""

    def __init__(self, config: FlextApiLoggingConfig | None = None) -> None:
        super().__init__("LoggingPlugin")
        self.config = config or FlextApiLoggingConfig()
        self._request_counter = 0

    def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Sanitize sensitive headers for logging."""
        if not self.config.log_headers:
            return {}

        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.config.sensitive_headers:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_body(self, body: Any) -> str:
        """Sanitize request/response body for logging."""
        if not self.config.log_body:
            return "***BODY_LOGGING_DISABLED***"

        if body is None:
            return "None"

        try:
            if isinstance(body, dict):
                body_str = json.dumps(body, indent=2)
            elif isinstance(body, str):
                body_str = body
            else:
                body_str = str(body)

            if len(body_str) > self.config.max_body_length:
                return body_str[:self.config.max_body_length] + "...[TRUNCATED]"

            return body_str
        except Exception:
            return "***BODY_SERIALIZATION_ERROR***"

    async def before_request(self, request: FlextApiClientRequest) -> None:
        """Log request details."""
        if not self.config.log_requests:
            return

        self._request_counter += 1
        request_id = f"req_{self._request_counter}_{int(time.time())}"

        # Store request ID for correlation
        request.plugin_data["request_id"] = request_id

        log_parts = [
            f"🚀 REQUEST [{request_id}]",
            f"Method: {request.method}",
            f"URL: {request.url}",
        ]

        if self.config.log_headers and request.headers:
            sanitized_headers = self._sanitize_headers(request.headers)
            log_parts.append(f"Headers: {json.dumps(sanitized_headers, indent=2)}")

        if request.params:
            log_parts.append(f"Params: {json.dumps(request.params, indent=2)}")

        if request.json or request.data:
            body = request.json or request.data
            sanitized_body = self._sanitize_body(body)
            log_parts.append(f"Body: {sanitized_body}")

        logger.info("\n".join(log_parts))

        # Update metrics
        self._metrics["requests_logged"] = self._metrics.get("requests_logged", 0) + 1

    async def after_request(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Log successful response details."""
        if not self.config.log_responses:
            return

        request_id = request.plugin_data.get("request_id", "unknown")

        log_parts = [
            f"✅ RESPONSE [{request_id}]",
            f"Status: {response.status_code}",
        ]

        if self.config.log_performance:
            log_parts.extend([
                f"Duration: {response.execution_time_ms:.2f}ms",
                f"Cached: {response.cached}",
                f"Retries: {response.retry_count}",
                f"Circuit Breaker: {response.circuit_breaker_state}",
            ])

        if self.config.log_headers and response.headers:
            sanitized_headers = self._sanitize_headers(response.headers)
            log_parts.append(f"Headers: {json.dumps(sanitized_headers, indent=2)}")

        if response.data:
            sanitized_body = self._sanitize_body(response.data)
            log_parts.append(f"Body: {sanitized_body}")

        logger.info("\n".join(log_parts))

        # Update metrics
        self._metrics["responses_logged"] = self._metrics.get("responses_logged", 0) + 1
        self._metrics["successful_responses"] = self._metrics.get("successful_responses", 0) + 1

    async def on_error(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Log error response details."""
        request_id = request.plugin_data.get("request_id", "unknown")

        log_parts = [
            f"❌ ERROR [{request_id}]",
            f"Status: {response.status_code}",
            f"Duration: {response.execution_time_ms:.2f}ms",
            f"Retries: {response.retry_count}",
            f"Circuit Breaker: {response.circuit_breaker_state}",
        ]

        if response.text:
            sanitized_body = self._sanitize_body(response.text)
            log_parts.append(f"Error: {sanitized_body}")

        logger.error("\n".join(log_parts))

        # Update metrics
        self._metrics["error_responses"] = self._metrics.get("error_responses", 0) + 1


# ==============================================================================
# RETRY PLUGIN
# ==============================================================================

@dataclass
class FlextApiRetryConfig:
    """Configuration for retry plugin."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retry_on_status_codes: list[int] = field(default_factory=lambda: [408, 429, 500, 502, 503, 504])
    retry_on_exceptions: list[type] = field(default_factory=lambda: [asyncio.TimeoutError, ConnectionError])


class FlextApiRetryPlugin(FlextApiPlugin):
    """Plugin for intelligent retry logic with exponential backoff."""

    def __init__(self, config: FlextApiRetryConfig | None = None) -> None:
        super().__init__("RetryPlugin")
        self.config = config or FlextApiRetryConfig()

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        if not self.config.exponential_backoff:
            return self.config.base_delay

        delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            import secrets
            # Use cryptographically secure random for jitter
            delay *= (0.5 + secrets.randbelow(500) / 1000.0)  # Add 0-50% jitter

        return delay

    def _should_retry(self, response: FlextApiClientResponse) -> bool:
        """Determine if request should be retried."""
        return response.status_code in self.config.retry_on_status_codes

    async def before_request(self, request: FlextApiClientRequest) -> None:
        """Update request retry configuration."""
        # Override request retry settings with plugin config
        request.retry_count = max(request.retry_count, self.config.max_retries)

        self._metrics["retry_requests"] = self._metrics.get("retry_requests", 0) + 1

    async def after_request(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Record successful request (no retry needed)."""
        if response.retry_count > 0:
            self._metrics["successful_retries"] = self._metrics.get("successful_retries", 0) + 1
            logger.info(f"Request succeeded after {response.retry_count} retries")

    async def on_error(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Handle retry logic for failed requests."""
        if self._should_retry(response) and response.retry_count < self.config.max_retries:
            delay = self._calculate_delay(response.retry_count)
            logger.warning(f"Request failed, retrying in {delay:.2f}s (attempt {response.retry_count + 1}/{self.config.max_retries})")

            self._metrics["retry_attempts"] = self._metrics.get("retry_attempts", 0) + 1
            await asyncio.sleep(delay)
        else:
            self._metrics["failed_retries"] = self._metrics.get("failed_retries", 0) + 1
            logger.error(f"Request failed after {response.retry_count} retries")


# ==============================================================================
# CACHING PLUGIN
# ==============================================================================

@dataclass
class FlextApiCachingConfig:
    """Configuration for caching plugin."""

    enabled: bool = True
    default_ttl: int = 300  # 5 minutes
    max_cache_size: int = 1000
    cache_get_requests: bool = True
    cache_post_requests: bool = False
    respect_cache_headers: bool = True
    cache_key_prefix: str = "flext_api_cache"


class FlextApiCacheEntry:
    """Cache entry with TTL and metadata."""

    def __init__(self, response: FlextApiClientResponse, ttl: int) -> None:
        self.response = response
        self.timestamp = time.time()
        self.ttl = ttl
        self.hit_count = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.timestamp > self.ttl

    def get_response(self) -> FlextApiClientResponse:
        """Get cached response and increment hit count."""
        self.hit_count += 1
        # Mark response as cached
        response_copy = self.response.model_copy()
        response_copy.cached = True
        return response_copy


class FlextApiCachingPlugin(FlextApiPlugin):
    """Plugin for response caching with TTL support."""

    def __init__(self, config: FlextApiCachingConfig | None = None) -> None:
        super().__init__("CachingPlugin")
        self.config = config or FlextApiCachingConfig()
        self._cache: dict[str, FlextApiCacheEntry] = {}

    def _generate_cache_key(self, request: FlextApiClientRequest) -> str:
        """Generate cache key for request."""
        key_parts = [
            self.config.cache_key_prefix,
            request.method,
            request.url,
            json.dumps(request.params, sort_keys=True) if request.params else "",
            json.dumps(request.headers, sort_keys=True) if request.headers else "",
        ]
        return "|".join(key_parts)

    def _should_cache_request(self, request: FlextApiClientRequest) -> bool:
        """Determine if request should be cached."""
        if not self.config.enabled:
            return False

        if request.method == "GET" and self.config.cache_get_requests:
            return True

        return bool(request.method == "POST" and self.config.cache_post_requests)

    def _should_cache_response(self, response: FlextApiClientResponse) -> bool:
        """Determine if response should be cached."""
        # Only cache successful responses
        if not (200 <= response.status_code < 300):
            return False

        # Respect cache-control headers if configured
        if self.config.respect_cache_headers:
            cache_control = response.headers.get("cache-control", "").lower()
            if "no-cache" in cache_control or "no-store" in cache_control:
                return False

        return True

    def _cleanup_cache(self) -> None:
        """Remove expired entries and enforce size limit."""
        # Remove expired entries
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]

        # Enforce size limit (simple LRU: remove oldest entries)
        if len(self._cache) > self.config.max_cache_size:
            # Sort by timestamp and remove oldest
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].timestamp
            )

            excess_count = len(self._cache) - self.config.max_cache_size
            for key, _ in sorted_entries[:excess_count]:
                del self._cache[key]

    async def before_request(self, request: FlextApiClientRequest) -> None:
        """Check cache for existing response."""
        if not self._should_cache_request(request):
            return

        cache_key = self._generate_cache_key(request)
        cache_entry = self._cache.get(cache_key)

        if cache_entry and not cache_entry.is_expired():
            # Cache hit - store cached response in request for later use
            request.plugin_data["cached_response"] = cache_entry.get_response()

            self._metrics["cache_hits"] = self._metrics.get("cache_hits", 0) + 1
            logger.debug(f"Cache HIT for {request.method} {request.url}")
        else:
            self._metrics["cache_misses"] = self._metrics.get("cache_misses", 0) + 1
            logger.debug(f"Cache MISS for {request.method} {request.url}")

        # Clean up cache periodically
        if len(self._cache) % 100 == 0:  # Every 100 requests
            self._cleanup_cache()

    async def after_request(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Cache successful response."""
        if not self._should_cache_request(request) or not self._should_cache_response(response):
            return

        cache_key = self._generate_cache_key(request)

        # Determine TTL
        ttl = self.config.default_ttl
        if request.cache_ttl:
            ttl = request.cache_ttl
        elif self.config.respect_cache_headers:
            cache_control = response.headers.get("cache-control", "")
            if "max-age=" in cache_control:
                try:
                    max_age = int(cache_control.split("max-age=")[1].split(",")[0])
                    ttl = max_age
                except (ValueError, IndexError):
                    pass

        # Store in cache
        self._cache[cache_key] = FlextApiCacheEntry(response, ttl)
        self._metrics["cache_stores"] = self._metrics.get("cache_stores", 0) + 1

        logger.debug(f"Cached response for {request.method} {request.url} (TTL: {ttl}s)")

    async def on_error(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Don't cache error responses."""

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())

        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "cache_size_bytes": sum(len(str(entry.response)) for entry in self._cache.values()),
            "hit_rate": (
                self._metrics.get("cache_hits", 0) /
                max(self._metrics.get("cache_hits", 0) + self._metrics.get("cache_misses", 0), 1)
            ) * 100,
        }


# ==============================================================================
# METRICS PLUGIN
# ==============================================================================

@dataclass
class FlextApiMetricsConfig:
    """Configuration for metrics plugin."""

    track_performance: bool = True
    track_status_codes: bool = True
    track_endpoints: bool = True
    track_user_agents: bool = False
    percentiles: list[float] = field(default_factory=lambda: [50.0, 90.0, 95.0, 99.0])


class FlextApiMetricsPlugin(FlextApiPlugin):
    """Plugin for comprehensive metrics collection."""

    def __init__(self, config: FlextApiMetricsConfig | None = None) -> None:
        super().__init__("MetricsPlugin")
        self.config = config or FlextApiMetricsConfig()
        self._response_times: list[float] = []
        self._status_codes: dict[int, int] = {}
        self._endpoints: dict[str, dict[str, Any]] = {}
        self._start_time = time.time()

    def _track_response_time(self, response_time: float) -> None:
        """Track response time for percentile calculations."""
        if not self.config.track_performance:
            return

        self._response_times.append(response_time)

        # Keep only last 10000 measurements to prevent memory growth
        if len(self._response_times) > 10000:
            self._response_times = self._response_times[-5000:]  # Keep last 5000

    def _track_status_code(self, status_code: int) -> None:
        """Track status code distribution."""
        if not self.config.track_status_codes:
            return

        self._status_codes[status_code] = self._status_codes.get(status_code, 0) + 1

    def _track_endpoint(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Track endpoint-specific metrics."""
        if not self.config.track_endpoints:
            return

        endpoint_key = f"{request.method} {request.url}"

        if endpoint_key not in self._endpoints:
            self._endpoints[endpoint_key] = {
                "request_count": 0,
                "total_response_time": 0.0,
                "status_codes": {},
                "first_seen": time.time(),
                "last_seen": time.time(),
            }

        endpoint_data = self._endpoints[endpoint_key]
        endpoint_data["request_count"] += 1
        endpoint_data["total_response_time"] += response.execution_time_ms
        endpoint_data["last_seen"] = time.time()

        status_code = response.status_code
        endpoint_data["status_codes"][status_code] = endpoint_data["status_codes"].get(status_code, 0) + 1

    def _calculate_percentiles(self) -> dict[str, float]:
        """Calculate response time percentiles."""
        if not self._response_times:
            return {}

        sorted_times = sorted(self._response_times)
        percentiles = {}

        for p in self.config.percentiles:
            index = int((p / 100) * len(sorted_times))
            index = min(index, len(sorted_times) - 1)
            percentiles[f"p{p}"] = sorted_times[index]

        return percentiles

    async def before_request(self, request: FlextApiClientRequest) -> None:
        """Initialize request tracking."""
        self._metrics["total_requests"] = self._metrics.get("total_requests", 0) + 1

    async def after_request(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Track successful request metrics."""
        self._track_response_time(response.execution_time_ms)
        self._track_status_code(response.status_code)
        self._track_endpoint(request, response)

        self._metrics["successful_requests"] = self._metrics.get("successful_requests", 0) + 1

        if response.cached:
            self._metrics["cached_responses"] = self._metrics.get("cached_responses", 0) + 1

    async def on_error(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Track error request metrics."""
        self._track_response_time(response.execution_time_ms)
        self._track_status_code(response.status_code)
        self._track_endpoint(request, response)

        self._metrics["failed_requests"] = self._metrics.get("failed_requests", 0) + 1

    def get_detailed_metrics(self) -> dict[str, Any]:
        """Get comprehensive metrics report."""
        uptime = time.time() - self._start_time
        total_requests = self._metrics.get("total_requests", 0)
        successful_requests = self._metrics.get("successful_requests", 0)

        return {
            "uptime_seconds": uptime,
            "requests_per_second": total_requests / max(uptime, 1),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": self._metrics.get("failed_requests", 0),
            "success_rate": (successful_requests / max(total_requests, 1)) * 100,
            "cached_responses": self._metrics.get("cached_responses", 0),
            "cache_hit_rate": (self._metrics.get("cached_responses", 0) / max(total_requests, 1)) * 100,
            "response_time_percentiles": self._calculate_percentiles(),
            "status_code_distribution": self._status_codes.copy(),
            "endpoint_metrics": self._endpoints.copy(),
            "average_response_time": (
                sum(self._response_times) / max(len(self._response_times), 1)
                if self._response_times else 0
            ),
        }


# ==============================================================================
# CIRCUIT BREAKER PLUGIN
# ==============================================================================

@dataclass
class FlextApiCircuitBreakerConfig:
    """Configuration for circuit breaker plugin."""

    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60
    monitor_window_seconds: int = 300  # 5 minutes
    excluded_status_codes: list[int] = field(default_factory=lambda: [400, 401, 403, 404])


class FlextApiCircuitBreakerPlugin(FlextApiPlugin):
    """Plugin for circuit breaker pattern implementation."""

    def __init__(self, config: FlextApiCircuitBreakerConfig | None = None) -> None:
        super().__init__("CircuitBreakerPlugin")
        self.config = config or FlextApiCircuitBreakerConfig()
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._state = "closed"  # closed, open, half-open
        self._failure_times: list[float] = []

    def _should_count_as_failure(self, response: FlextApiClientResponse) -> bool:
        """Determine if response should count as failure."""
        if response.status_code in self.config.excluded_status_codes:
            return False  # Client errors don't count as failures

        return response.status_code >= 500  # Server errors count as failures

    def _cleanup_old_failures(self) -> None:
        """Remove failures outside monitoring window."""
        cutoff_time = time.time() - self.config.monitor_window_seconds
        self._failure_times = [t for t in self._failure_times if t > cutoff_time]

    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened."""
        self._cleanup_old_failures()
        return len(self._failure_times) >= self.config.failure_threshold

    def _can_attempt_request(self) -> bool:
        """Check if request can be attempted."""
        if self._state == "closed":
            return True

        if self._state == "open":
            # Check if timeout has elapsed
            if time.time() - self._last_failure_time > self.config.timeout_seconds:
                self._state = "half-open"
                self._success_count = 0
                return True
            return False

        # half-open state
        return True

    async def before_request(self, request: FlextApiClientRequest) -> None:
        """Check circuit breaker state before request."""
        if not self._can_attempt_request():
            # Circuit is open - fail fast
            request.plugin_data["circuit_breaker_blocked"] = True

            self._metrics["blocked_requests"] = self._metrics.get("blocked_requests", 0) + 1
            logger.warning(f"Circuit breaker OPEN - blocking request to {request.url}")

    async def after_request(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Handle successful response."""
        if self._should_count_as_failure(response):
            # This is actually a failure
            await self.on_error(request, response)
            return

        # Success
        if self._state == "half-open":
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._state = "closed"
                self._failure_count = 0
                self._failure_times.clear()
                logger.info("Circuit breaker CLOSED - service recovered")

        elif self._state == "closed":
            # Reset failure count on success
            self._failure_count = max(0, self._failure_count - 1)

        self._metrics["successful_requests"] = self._metrics.get("successful_requests", 0) + 1

    async def on_error(self, request: FlextApiClientRequest, response: FlextApiClientResponse) -> None:
        """Handle failed response."""
        if not self._should_count_as_failure(response):
            return  # Don't count client errors

        current_time = time.time()
        self._failure_count += 1
        self._last_failure_time = current_time
        self._failure_times.append(current_time)

        if self._state == "half-open":
            # Failure in half-open state immediately opens circuit
            self._state = "open"
            logger.warning("Circuit breaker OPENED - service still failing")

        elif self._state == "closed" and self._should_open_circuit():
            self._state = "open"
            logger.warning(f"Circuit breaker OPENED - {self.config.failure_threshold} failures in {self.config.monitor_window_seconds}s")

        self._metrics["failed_requests"] = self._metrics.get("failed_requests", 0) + 1
        self._metrics["circuit_state"] = self._state

    def get_circuit_status(self) -> dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "state": self._state,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "recent_failures": len(self._failure_times),
            "last_failure_time": self._last_failure_time,
            "seconds_until_half_open": max(0, self.config.timeout_seconds - (time.time() - self._last_failure_time)) if self._state == "open" else 0,
        }
