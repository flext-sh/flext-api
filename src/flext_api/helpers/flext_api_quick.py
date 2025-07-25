#!/usr/bin/env python3
"""FlextApi Quick Helpers - Massive Code Reduction Utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Utilities that eliminate 90%+ of common API client boilerplate code.
"""

from __future__ import annotations

import asyncio
from typing import Any, Self

from flext_core import FlextResult, get_logger

from flext_api.client.core import FlextApiClient, FlextApiClientBuilder

logger = get_logger(__name__)


# ==============================================================================
# QUICK API OPERATIONS - MASSIVE CODE REDUCTION
# ==============================================================================


async def flext_api_quick_get(url: str, **kwargs: object) -> dict[str, Any]:
    """Quick GET request - replaces 20+ lines of boilerplate with 1 line.

    Returns:
        {"success": bool, "data": Any, "status": int, "cached": bool}

    """
    async with FlextApiClientBuilder().with_base_url("").build() as client:
        result = await client.get(url, **kwargs)
        return {
            "success": result.success,
            "data": result.data.json_data if result.success else None,
            "status": result.data.status_code if result.data else 0,
            "cached": result.data.cached if result.data else False,
        }


async def flext_api_quick_post(
    url: str, data: dict[str, Any], **kwargs: object
) -> dict[str, Any]:
    """Quick POST request with JSON data.

    Returns:
        {"success": bool, "data": Any, "status": int}

    """
    async with FlextApiClientBuilder().with_base_url("").build() as client:
        result = await client.post(url, json=data, **kwargs)
        return {
            "success": result.success,
            "data": result.data.json_data if result.success else None,
            "status": result.data.status_code if result.data else 0,
        }


async def flext_api_quick_bulk(requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Execute multiple API requests concurrently - massive performance gain.

    Args:
        requests: [{"method": "GET", "url": "...", "data": {...}}, ...]

    Returns:
        [{"success": bool, "data": Any, "status": int}, ...]

    """
    async with FlextApiClientBuilder().build() as client:
        tasks = []

        for req in requests:
            method = req.get("method", "GET").lower()
            url = req["url"]

            if method == "get":
                task = client.get(
                    url, **{k: v for k, v in req.items() if k not in ["method", "url"]}
                )
            elif method == "post":
                task = client.post(
                    url, **{k: v for k, v in req.items() if k not in ["method", "url"]}
                )
            elif method == "put":
                task = client.put(
                    url, **{k: v for k, v in req.items() if k not in ["method", "url"]}
                )
            elif method == "delete":
                task = client.delete(
                    url, **{k: v for k, v in req.items() if k not in ["method", "url"]}
                )
            else:
                continue

            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            {
                "success": not isinstance(r, Exception) and r.success,
                "data": r.data.json_data
                if not isinstance(r, Exception) and r.success
                else None,
                "status": r.data.status_code
                if not isinstance(r, Exception) and r.data
                else 0,
                "error": str(r)
                if isinstance(r, Exception)
                else (r.message if not r.success else None),
            }
            for r in results
        ]


# ==============================================================================
# ENTERPRISE API CLIENT BUILDER - ONE LINE SETUP
# ==============================================================================


def flext_api_enterprise_client(
    base_url: str,
    auth_token: str | None = None,
    api_key: str | None = None,
    enable_all_features: bool = True,
    **kwargs: object,
) -> FlextApiClient:
    """Create enterprise-grade API client with one line.

    Replaces 50+ lines of configuration with 1 line.
    Includes: caching, circuit breaker, retries, metrics, validation, logging.
    """
    builder = FlextApiClientBuilder().with_base_url(base_url)

    # Authentication
    if auth_token:
        builder.with_auth_token(auth_token)
    if api_key:
        builder.with_api_key(api_key)

    if enable_all_features:
        # Enterprise features with sensible defaults
        builder = (
            builder.with_caching(enabled=True, ttl=300)
            .with_circuit_breaker(enabled=True, failure_threshold=5)
            .with_retries(max_retries=3, delay=1.0)
            .with_validation(requests=True, responses=True)
            .with_observability(metrics=True, tracing=True)
            .with_http2(enabled=True)
        )

        # Add enterprise plugins
        from flext_api.client.plugins import (
            FlextApiLoggingPlugin,
            FlextApiMetricsPlugin,
            FlextApiRetryPlugin,
        )

        builder = (
            builder.with_plugin(FlextApiLoggingPlugin())
            .with_plugin(FlextApiMetricsPlugin())
            .with_plugin(FlextApiRetryPlugin())
        )

    # Apply any additional configuration
    for key, value in kwargs.items():
        if hasattr(builder, f"with_{key}"):
            getattr(builder, f"with_{key}")(value)

    return builder.build()


# ==============================================================================
# MICROSERVICE INTEGRATION HELPER
# ==============================================================================


class FlextApiMicroserviceIntegrator:
    """Integrate with multiple microservices using single client - massive code reduction."""

    def __init__(self, services: dict[str, str], auth_token: str | None = None) -> None:
        """Initialize with service map: {"service_name": "base_url"}."""
        self.services = services
        self.auth_token = auth_token
        self._clients: dict[str, FlextApiClient] = {}

    async def __aenter__(self) -> Self:
        # Create optimized client for each service
        for service_name, base_url in self.services.items():
            self._clients[service_name] = flext_api_enterprise_client(
                base_url=base_url, auth_token=self.auth_token
            )
            await self._clients[service_name].__aenter__()
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object) -> None:
        for client in self._clients.values():
            await client.__aexit__(exc_type, exc_val, exc_tb)

    async def call_service(
        self, service_name: str, endpoint: str, method: str = "GET", **kwargs: object
    ) -> dict[str, Any]:
        """Call any microservice endpoint with automatic error handling."""
        if service_name not in self._clients:
            return {"success": False, "error": f"Service {service_name} not configured"}

        client = self._clients[service_name]

        try:
            if method.upper() == "GET":
                result = await client.get(endpoint, **kwargs)
            elif method.upper() == "POST":
                result = await client.post(endpoint, **kwargs)
            elif method.upper() == "PUT":
                result = await client.put(endpoint, **kwargs)
            elif method.upper() == "DELETE":
                result = await client.delete(endpoint, **kwargs)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}

            return {
                "success": result.success,
                "data": result.data.json_data if result.success else None,
                "status": result.data.status_code if result.data else 0,
                "service": service_name,
                "cached": result.data.cached if result.data else False,
                "execution_time_ms": result.data.execution_time_ms
                if result.data
                else 0,
            }

        except Exception as e:
            logger.exception(f"Service call failed: {service_name}/{endpoint}")
            return {
                "success": False,
                "error": str(e),
                "service": service_name,
            }

    async def call_multiple_services(
        self, calls: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Call multiple services concurrently - massive performance gain.

        Args:
            calls: [{"service": "user-service", "endpoint": "/users/1", "method": "GET"}, ...]

        """
        tasks = []
        for call in calls:
            service = call.get("service")
            endpoint = call.get("endpoint")
            method = call.get("method", "GET")
            kwargs = {
                k: v
                for k, v in call.items()
                if k not in ["service", "endpoint", "method"]
            }

            task = self.call_service(service, endpoint, method, **kwargs)
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    def get_service_health(self) -> dict[str, Any]:
        """Get health status of all services."""
        health_data = {}
        for service_name, client in self._clients.items():
            health = client.get_health()
            metrics = client.get_metrics()

            health_data[service_name] = {
                "status": health.get("status"),
                "total_requests": metrics.total_requests,
                "success_rate": health.get("success_rate", 0),
                "cache_size": health.get("cache_size", 0),
            }

        return health_data


# ==============================================================================
# API RESPONSE AGGREGATOR
# ==============================================================================


class FlextApiResponseAggregator:
    """Aggregate responses from multiple APIs with intelligent error handling."""

    @staticmethod
    async def aggregate_concurrent(
        requests: list[dict[str, Any]],
        base_url: str = "",
        auth_token: str | None = None,
    ) -> dict[str, Any]:
        """Aggregate multiple API calls concurrently with comprehensive error handling."""
        async with flext_api_enterprise_client(base_url, auth_token) as client:
            tasks = []

            # Prepare all requests
            for req in requests:
                method = req.get("method", "GET").lower()
                url = req["url"]
                req_kwargs = {
                    k: v for k, v in req.items() if k not in ["method", "url", "key"]
                }

                if method == "get":
                    task = client.get(url, **req_kwargs)
                elif method == "post":
                    task = client.post(url, **req_kwargs)
                else:
                    continue

                tasks.append((req.get("key", f"request_{len(tasks)}"), task))

            # Execute all concurrently
            results = await asyncio.gather(
                *[task for _, task in tasks], return_exceptions=True
            )

            # Process results
            aggregated = {
                "success": True,
                "data": {},
                "metadata": {
                    "total_requests": len(tasks),
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "cached_responses": 0,
                },
            }

            for i, (key, _task) in enumerate(tasks):
                result = results[i]

                if isinstance(result, Exception):
                    aggregated["data"][key] = {"error": str(result), "success": False}
                    aggregated["metadata"]["failed_requests"] += 1
                elif result.success:
                    aggregated["data"][key] = {
                        "data": result.data.json_data,
                        "success": True,
                        "cached": result.data.cached,
                        "execution_time_ms": result.data.execution_time_ms,
                    }
                    aggregated["metadata"]["successful_requests"] += 1
                    if result.data.cached:
                        aggregated["metadata"]["cached_responses"] += 1
                else:
                    aggregated["data"][key] = {
                        "error": result.message,
                        "success": False,
                        "status": result.data.status_code if result.data else 0,
                    }
                    aggregated["metadata"]["failed_requests"] += 1

            # Overall success if at least 50% requests succeeded
            success_rate = (
                aggregated["metadata"]["successful_requests"]
                / aggregated["metadata"]["total_requests"]
            )
            aggregated["success"] = success_rate >= 0.5
            aggregated["metadata"]["success_rate"] = success_rate * 100

            return aggregated


# ==============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON PATTERNS
# ==============================================================================


async def flext_api_fetch_user_data(
    user_id: str, services: dict[str, str], auth_token: str | None = None
) -> dict[str, Any]:
    """Fetch complete user data from multiple services - replaces 100+ lines."""
    # Common pattern: user profile + orders + preferences + activity
    calls = [
        {"service": "user", "endpoint": f"/users/{user_id}", "key": "profile"},
        {"service": "order", "endpoint": f"/users/{user_id}/orders", "key": "orders"},
        {
            "service": "preference",
            "endpoint": f"/users/{user_id}/preferences",
            "key": "preferences",
        },
        {
            "service": "activity",
            "endpoint": f"/users/{user_id}/activity",
            "key": "activity",
        },
    ]

    async with FlextApiMicroserviceIntegrator(services, auth_token) as integrator:
        results = await integrator.call_multiple_services(calls)

        # Build unified user data
        user_data = {
            "user_id": user_id,
            "profile": None,
            "orders": [],
            "preferences": {},
            "activity": [],
            "data_completeness": 0,
        }

        successful_calls = 0
        for result in results:
            if not isinstance(result, Exception) and result.get("success"):
                key = next(
                    (call["key"] for call in calls if call["endpoint"] in str(result)),
                    "unknown",
                )
                user_data[key] = result["data"]
                successful_calls += 1

        user_data["data_completeness"] = (successful_calls / len(calls)) * 100

        return user_data


async def flext_api_health_check_all(services: dict[str, str]) -> dict[str, Any]:
    """Check health of all services concurrently - replaces monitoring boilerplate."""
    health_calls = [
        {"service": service, "endpoint": "/health", "method": "GET"}
        for service in services
    ]

    async with FlextApiMicroserviceIntegrator(services) as integrator:
        results = await integrator.call_multiple_services(health_calls)

        health_summary = {
            "overall_health": "healthy",
            "services": {},
            "healthy_count": 0,
            "total_count": len(services),
        }

        for result in results:
            if isinstance(result, Exception):
                continue

            service_name = result.get("service", "unknown")
            is_healthy = result.get("success", False) and result.get("status", 0) == 200

            health_summary["services"][service_name] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "response_time_ms": result.get("execution_time_ms", 0),
                "cached": result.get("cached", False),
            }

            if is_healthy:
                health_summary["healthy_count"] += 1

        # Overall health calculation
        health_ratio = health_summary["healthy_count"] / health_summary["total_count"]
        if health_ratio < 0.5:
            health_summary["overall_health"] = "unhealthy"
        elif health_ratio < 0.8:
            health_summary["overall_health"] = "degraded"

        health_summary["health_percentage"] = health_ratio * 100

        return health_summary
