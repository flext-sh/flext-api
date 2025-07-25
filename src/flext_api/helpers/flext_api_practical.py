#!/usr/bin/env python3
"""FlextApi Practical Helpers - Real-world utility functions for common development tasks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Practical helpers that solve actual development pain points with minimal code.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from flext_core import FlextResult, get_logger

from flext_api.helpers.flext_api_quick import flext_api_quick_get, flext_api_quick_post

logger = get_logger(__name__)


# ==============================================================================
# CONFIGURATION MANAGEMENT
# ==============================================================================

class FlextApiConfigManager:
    """Centralized configuration management with environment support."""

    def __init__(self, config_dir: str | Path = "config") -> None:
        """Initialize with configuration directory."""
        self.config_dir = Path(config_dir)
        self._cache: dict[str, dict[str, Any]] = {}

    def load_config(self, env: str = "development") -> dict[str, Any]:
        """Load configuration for specific environment."""
        cache_key = f"config_{env}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        config_file = self.config_dir / f"{env}.json"

        if not config_file.exists():
            # Create default config if it doesn't exist
            default_config = self._create_default_config(env)
            self._save_config(config_file, default_config)
            return default_config

        try:
            with config_file.open() as f:
                config = json.load(f)
                self._cache[cache_key] = config
                return config
        except Exception:
            logger.exception(f"Failed to load config for {env}")
            return self._create_default_config(env)

    def _create_default_config(self, env: str) -> dict[str, Any]:
        """Create default configuration for environment."""
        return {
            "environment": env,
            "api": {
                "base_url": f"https://api-{env}.example.com" if env != "development" else "http://localhost:8000",
                "timeout": 30,
                "retries": 3
            },
            "cache": {
                "enabled": True,
                "ttl": 300
            },
            "logging": {
                "level": "DEBUG" if env == "development" else "INFO"
            }
        }

    def _save_config(self, config_file: Path, config: dict[str, Any]) -> None:
        """Save configuration to file."""
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with config_file.open("w") as f:
            json.dump(config, f, indent=2)


# ==============================================================================
# API DEBUGGING AND TESTING
# ==============================================================================

class FlextApiDebugger:
    """Debug helper for API development and testing."""

    @staticmethod
    async def test_endpoint(
        url: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Test API endpoint with detailed response analysis."""
        start_time = datetime.now()

        try:
            if method.upper() == "GET":
                result = await flext_api_quick_get(url, headers=headers or {})
            elif method.upper() == "POST":
                result = await flext_api_quick_post(url, data or {}, headers=headers or {})
            else:
                return {"error": f"Unsupported method: {method}", "success": False}

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            return {
                "success": result["success"],
                "status_code": result["status"],
                "response_time_ms": response_time,
                "data": result["data"],
                "analysis": {
                    "is_json": isinstance(result["data"], dict),
                    "data_size_bytes": len(str(result["data"])) if result["data"] else 0,
                    "cached": result.get("cached", False),
                    "performance": "fast" if response_time < 1000 else "slow",
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": {"exception_type": type(e).__name__}
            }

    @staticmethod
    async def load_test_endpoint(
        url: str,
        concurrent_requests: int = 10,
        method: str = "GET",
        data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Perform load testing on endpoint."""
        start_time = datetime.now()

        tasks = []
        for _ in range(concurrent_requests):
            if method.upper() == "GET":
                task = flext_api_quick_get(url)
            elif method.upper() == "POST":
                task = flext_api_quick_post(url, data or {})
            else:
                continue
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now()

        total_time = (end_time - start_time).total_seconds()
        successful = sum(1 for r in results if not isinstance(r, Exception) and r.get("success"))
        failed = len(results) - successful

        return {
            "load_test_results": {
                "total_requests": len(results),
                "successful_requests": successful,
                "failed_requests": failed,
                "success_rate": (successful / len(results)) * 100,
                "total_time_seconds": total_time,
                "requests_per_second": len(results) / total_time,
                "average_response_time": total_time / len(results) * 1000
            }
        }


# ==============================================================================
# DATA TRANSFORMATION UTILITIES
# ==============================================================================

class FlextApiDataTransformer:
    """Common data transformation utilities for API responses."""

    @staticmethod
    def flatten_nested_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """Flatten nested dictionary structure."""
        def _flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
            result = {}
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    if isinstance(value, dict):
                        result.update(_flatten(value, new_key))
                    elif isinstance(value, list) and value and isinstance(value[0], dict):
                        for i, item in enumerate(value):
                            result.update(_flatten(item, f"{new_key}[{i}]"))
                    else:
                        result[new_key] = value
            return result

        return _flatten(data)

    @staticmethod
    def extract_fields(data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
        """Extract specific fields from nested data structure."""
        result = {}
        flattened = FlextApiDataTransformer.flatten_nested_dict(data)

        for field in fields:
            if field in flattened:
                result[field] = flattened[field]
            else:
                # Try partial matching
                matching_keys = [k for k in flattened if field in k]
                if matching_keys:
                    result[field] = {k.split(".")[-1]: flattened[k] for k in matching_keys}

        return result

    @staticmethod
    def normalize_response_format(data: Any) -> dict[str, Any]:
        """Normalize different API response formats to standard structure."""
        if isinstance(data, dict):
            # Check for common response patterns
            if "data" in data and "status" in data:
                return data  # Already normalized
            if "result" in data:
                return {"data": data["result"], "status": "success"}
            if "error" in data:
                return {"data": None, "status": "error", "error": data["error"]}
            return {"data": data, "status": "success"}
        return {"data": data, "status": "success"}


# ==============================================================================
# API WORKFLOW AUTOMATION
# ==============================================================================

class FlextApiWorkflow:
    """Automate common API workflow patterns."""

    def __init__(self, base_url: str, auth_headers: dict[str, str] | None = None) -> None:
        """Initialize workflow with base configuration."""
        self.base_url = base_url.rstrip("/")
        self.auth_headers = auth_headers or {}
        self.workflow_results: list[dict[str, Any]] = []

    async def execute_sequence(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute sequence of API calls with dependency handling."""
        workflow_start = datetime.now()
        results = {}

        for i, step in enumerate(steps):
            step_name = step.get("name", f"step_{i}")
            method = step.get("method", "GET")
            endpoint = step["endpoint"]

            # Build URL
            url = f"{self.base_url}{endpoint}" if not endpoint.startswith("http") else endpoint

            # Prepare data with variable substitution
            data = step.get("data", {})
            if isinstance(data, dict):
                data = self._substitute_variables(data, results)

            # Prepare headers
            headers = {**self.auth_headers, **step.get("headers", {})}

            # Execute step
            try:
                if method.upper() == "GET":
                    result = await flext_api_quick_get(url, headers=headers)
                elif method.upper() == "POST":
                    result = await flext_api_quick_post(url, data, headers=headers)
                else:
                    result = {"success": False, "error": f"Unsupported method: {method}"}

                # Store result for next steps
                results[step_name] = result["data"] if result["success"] else None

                # Extract specific fields if specified
                if "extract" in step and result["success"]:
                    extracted = FlextApiDataTransformer.extract_fields(result["data"], step["extract"])
                    results[f"{step_name}_extracted"] = extracted

                self.workflow_results.append({
                    "step": step_name,
                    "success": result["success"],
                    "status": result.get("status"),
                    "data": result["data"]
                })

                # Stop on failure if specified
                if not result["success"] and step.get("stop_on_failure", False):
                    break

            except Exception as e:
                self.workflow_results.append({
                    "step": step_name,
                    "success": False,
                    "error": str(e)
                })
                if step.get("stop_on_failure", False):
                    break

        workflow_end = datetime.now()

        return {
            "workflow_success": all(r["success"] for r in self.workflow_results),
            "total_steps": len(steps),
            "successful_steps": sum(1 for r in self.workflow_results if r["success"]),
            "execution_time_seconds": (workflow_end - workflow_start).total_seconds(),
            "results": results,
            "step_details": self.workflow_results
        }

    def _substitute_variables(self, data: dict[str, Any], variables: dict[str, Any]) -> dict[str, Any]:
        """Substitute variables in data using previous step results."""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    var_name = value[2:-1]
                    result[key] = variables.get(var_name, value)
                elif isinstance(value, dict):
                    result[key] = self._substitute_variables(value, variables)
                else:
                    result[key] = value
            return result
        return data


# ==============================================================================
# PERFORMANCE MONITORING
# ==============================================================================

class FlextApiPerformanceMonitor:
    """Monitor API performance and generate reports."""

    def __init__(self) -> None:
        """Initialize performance monitor."""
        self.metrics: list[dict[str, Any]] = []

    async def benchmark_endpoint(
        self,
        url: str,
        duration_seconds: int = 60,
        requests_per_second: int = 10
    ) -> dict[str, Any]:
        """Benchmark endpoint over specified duration."""
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=duration_seconds)

        request_times = []
        success_count = 0
        error_count = 0

        while datetime.now() < end_time:
            batch_start = datetime.now()

            # Create batch of concurrent requests
            tasks = [flext_api_quick_get(url) for _ in range(requests_per_second)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    error_count += 1
                elif result.get("success"):
                    success_count += 1
                    request_times.append(result.get("response_time_ms", 0))
                else:
                    error_count += 1

            # Wait for next second
            batch_duration = (datetime.now() - batch_start).total_seconds()
            if batch_duration < 1.0:
                await asyncio.sleep(1.0 - batch_duration)

        total_requests = success_count + error_count

        return {
            "benchmark_results": {
                "duration_seconds": duration_seconds,
                "total_requests": total_requests,
                "successful_requests": success_count,
                "failed_requests": error_count,
                "requests_per_second_actual": total_requests / duration_seconds,
                "success_rate": (success_count / total_requests * 100) if total_requests > 0 else 0,
                "response_times": {
                    "min_ms": min(request_times) if request_times else 0,
                    "max_ms": max(request_times) if request_times else 0,
                    "avg_ms": sum(request_times) / len(request_times) if request_times else 0,
                    "p95_ms": sorted(request_times)[int(len(request_times) * 0.95)] if request_times else 0
                }
            }
        }


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

def flext_api_create_config_manager(config_dir: str = "config") -> FlextApiConfigManager:
    """Create configuration manager."""
    return FlextApiConfigManager(config_dir)


def flext_api_create_debugger() -> FlextApiDebugger:
    """Create API debugger."""
    return FlextApiDebugger()


def flext_api_create_workflow(base_url: str, auth_token: str | None = None) -> FlextApiWorkflow:
    """Create API workflow automation."""
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else None
    return FlextApiWorkflow(base_url, headers)


def flext_api_create_performance_monitor() -> FlextApiPerformanceMonitor:
    """Create performance monitor."""
    return FlextApiPerformanceMonitor()


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

async def flext_api_quick_health_check(endpoints: list[str]) -> dict[str, Any]:
    """Quick health check for multiple endpoints."""
    start_time = datetime.now()

    tasks = [flext_api_quick_get(endpoint) for endpoint in endpoints]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    healthy_count = 0
    unhealthy_endpoints = []

    for i, result in enumerate(results):
        endpoint = endpoints[i]
        if isinstance(result, Exception):
            unhealthy_endpoints.append({"endpoint": endpoint, "error": str(result)})
        elif result.get("success") and result.get("status") == 200:
            healthy_count += 1
        else:
            unhealthy_endpoints.append({
                "endpoint": endpoint,
                "status": result.get("status", 0),
                "error": "Non-200 response"
            })

    end_time = datetime.now()

    return {
        "overall_health": "healthy" if healthy_count == len(endpoints) else "degraded",
        "healthy_endpoints": healthy_count,
        "total_endpoints": len(endpoints),
        "health_percentage": (healthy_count / len(endpoints)) * 100,
        "unhealthy_endpoints": unhealthy_endpoints,
        "check_duration_ms": (end_time - start_time).total_seconds() * 1000
    }


async def flext_api_compare_responses(url1: str, url2: str, compare_fields: list[str] | None = None) -> dict[str, Any]:
    """Compare responses from two API endpoints."""
    result1, result2 = await asyncio.gather(
        flext_api_quick_get(url1),
        flext_api_quick_get(url2),
        return_exceptions=True
    )

    comparison = {
        "url1": url1,
        "url2": url2,
        "both_successful": False,
        "responses_identical": False,
        "differences": []
    }

    if not isinstance(result1, Exception) and not isinstance(result2, Exception):
        comparison["both_successful"] = result1.get("success") and result2.get("success")

        if comparison["both_successful"]:
            data1 = result1["data"]
            data2 = result2["data"]

            if compare_fields:
                # Compare specific fields
                for field in compare_fields:
                    flat1 = FlextApiDataTransformer.flatten_nested_dict(data1)
                    flat2 = FlextApiDataTransformer.flatten_nested_dict(data2)

                    val1 = flat1.get(field)
                    val2 = flat2.get(field)

                    if val1 != val2:
                        comparison["differences"].append({
                            "field": field,
                            "url1_value": val1,
                            "url2_value": val2
                        })
            else:
                # Compare entire responses
                comparison["responses_identical"] = data1 == data2
                if not comparison["responses_identical"]:
                    comparison["differences"].append("Full response content differs")

    return comparison
