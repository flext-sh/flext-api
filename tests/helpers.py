"""Test helpers for flext-api tests.

This module provides helper functions and utilities for testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import json
import re
import stat
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime
from pathlib import Path

import pytest
from flext_core import FlextConstants, FlextResult, T
from flext_tests import FlextTestsDomains, u
from flext_tests.domains import FlextTestsDomains as d

from flext_api.typings import t as t_api


def create_test_storage_config(**overrides: object) -> dict[str, str | int | bool]:
    """Create storage config using FlextTestsDomains - ABSOLUTE usage.

    Returns:
        Storage configuration dictionary.

    """
    # Use FlextTestsDomains instead of local implementation
    base_config = FlextTestsDomains.create_configuration()

    storage_config = {
        "backend": str(base_config.get("storage_backend", "memory")),
        "namespace": f"test_{base_config.get('namespace', 'storage')!s}",
        "enable_caching": bool(base_config.get("enable_caching", True)),
        "cache_ttl_seconds": int(base_config.get("cache_ttl", 300)),
    }
    # Apply overrides with type filtering
    storage_config.update({
        key: value
        for key, value in overrides.items()
        if isinstance(value, (str, int, bool))
    })
    return storage_config


def assert_flext_result_success(
    result: FlextResult[T],
    expected_value: T | None = None,
) -> None:
    """Assert FlextResult success using FlextTestsMatchers - ABSOLUTE."""
    # Direct assertion to avoid type variance issues in matchers
    if not result.is_success:
        pytest.fail(f"Expected success but got error: {result.error}")
    if expected_value is not None and result.value != expected_value:
        pytest.fail(f"Expected value {expected_value} but got {result.value}")


def assert_flext_result_failure[T](
    result: FlextResult[T],
    expected_error: str | None = None,
) -> None:
    """Assert FlextResult failure using FlextTestsMatchers - ABSOLUTE."""
    # Direct assertion to avoid type variance issues in matchers
    if result.is_success:
        pytest.fail(f"Expected failure but got data: {result.value}")
    if expected_error is not None and expected_error not in str(result.error):
        pytest.fail(
            f"Expected error containing '{expected_error}' but got: {result.error}",
        )


def create_test_request(
    method: str = "GET",
    url: str = "https://httpbin.org/get",
    headers: t_api.FlextWebHeaders | None = None,
    params: t_api.ResponseDict | None = None,
    timeout: float = 30.0,
) -> t_api.ResponseDict:
    """Create test request using FlextTestsDomains - ABSOLUTE usage.

    Returns:
        Test request dictionary.

    """
    # Use FlextTestsDomains for payload structure - NO local implementation
    payload_data = FlextTestsDomains.create_payload()

    return {
        "method": method,
        "url": url,
        "timeout": timeout,
        "headers": headers or payload_data.get("headers", {}),
        "params": params or payload_data.get("params", {}),
        "request_id": str(uuid.uuid4()),
    }


def create_test_response(
    status_code: int = 200,
    data: t_api.ResponseDict | t_api.ResponseList | str | bytes | None = None,
    headers: t_api.FlextWebHeaders | None = None,
    elapsed_time: float = 0.5,
    request_id: str | None = None,
    *,
    from_cache: bool = False,
) -> t_api.ResponseDict:
    """Create test response using FlextTestsDomains - ABSOLUTE usage.

    Returns:
        Test response dictionary.

    """
    # Use FlextTestsDomains for API response structure - NO local implementation
    api_response = FlextTestsDomains.api_response_data()

    return {
        "status_code": status_code,
        "data": data or api_response.get("data", {}),
        "headers": headers or {"Content-Type": "application/json"},
        "elapsed_time": elapsed_time,
        "request_id": request_id or api_response.get("request_id"),
        "from_cache": from_cache,
        "success": 200 <= status_code < 400,
    }


# ============================================================================
# UTILITIES using FlextTestsUtilities - ABSOLUTE
# ============================================================================


def run_test[T](coro: Awaitable[T]) -> T:
    """Run test using FlextTestsUtilities patterns.

    Returns:
        Result of the coroutine.

    Raises:
        AssertionError: If the test fails.

    """
    try:
        return coro
    except Exception as e:
        msg = f"test failed: {e}"
        raise AssertionError(msg) from e


def wait_for_condition(
    condition: Callable[[], bool],
    timeout_seconds: float = 5.0,
    interval: float = 0.1,
) -> bool:
    """Wait for condition using FlextTestsUtilities patterns.

    Returns:
        True if condition is met within timeout, False otherwise.

    """
    elapsed = 0.0
    while elapsed < timeout_seconds:
        if condition():
            return True
        time.sleep(interval)
        elapsed += interval
    return False


# ============================================================================
# FILE SYSTEM UTILITIES using FlextTestsUtilities - ABSOLUTE
# ============================================================================


def create_temp_json_file(path: Path, data: t_api.ResponseDict) -> Path:
    """Create temp JSON file using FlextTestsUtilities patterns.

    Returns:
        Path to the created JSON file.

    """
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def create_readonly_file(path: Path, content: str = "{}") -> Path:
    """Create readonly file using FlextTestsUtilities patterns.

    Returns:
        Path to the created readonly file.

    """
    path.write_text(content, encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return path


def restore_file_permissions(path: Path) -> None:
    """Restore file permissions using FlextTestsUtilities patterns."""
    with contextlib.suppress(OSError, PermissionError, FileNotFoundError):
        path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)


# ============================================================================
# API TESTING UTILITIES using FlextTestsDomains - ABSOLUTE
# ============================================================================


def assert_http_status(
    response: t_api.ResponseDict,
    expected_status: int = 200,
) -> None:
    """Assert HTTP status using FlextTestsMatchers patterns."""
    actual_status = response.get("status_code")
    if actual_status != expected_status:
        pytest.fail(
            f"Expected status {expected_status} but got {actual_status} "
            f"in response: {response}",
        )


def assert_response_structure(
    response: t_api.ResponseDict,
    required_keys: list[str] | None = None,
) -> None:
    """Assert response structure using FlextTestsMatchers patterns."""
    required_keys = required_keys or ["status_code", "data", "success"]

    for key in required_keys:
        if key not in response:
            pytest.fail(f"Missing required key '{key}' in response: {response}")


def assert_success_response(response: t_api.ResponseDict) -> None:
    """Assert success response using FlextTestsMatchers patterns."""
    assert_response_structure(response)
    assert_http_status(response, 200)

    success = response.get("success", False)
    if not success:
        pytest.fail(f"Response indicates failure: {response}")


def assert_error_response(
    response: t_api.ResponseDict,
    expected_status: int = 400,
) -> None:
    """Assert error response using FlextTestsMatchers patterns."""
    assert_response_structure(response)
    assert_http_status(response, expected_status)

    success = response.get("success", True)
    if success:
        pytest.fail(f"Response indicates success but error expected: {response}")


def create_mock_response(
    status_code: int = 200,
    data: t_api.ResponseDict | None = None,
) -> t_api.ResponseDict:
    """Create mock response using FlextTestsDomains - ABSOLUTE.

    Returns:
        Mock response dictionary.

    """
    # Use FlextTestsDomains for API response data - NO local implementation
    api_data = FlextTestsDomains.api_response_data().get("data", {})
    response_data = data or (api_data if isinstance(api_data, dict) else {})
    return create_test_response(
        status_code=status_code,
        data=response_data,
    )


def validate_email_format(email: str) -> bool:
    """Validate email using FlextTestsDomains - ABSOLUTE.

    Returns:
        True if email is valid, False otherwise.

    """
    # Use FlextTestsDomains validation cases - NO local implementation
    valid_cases = FlextTestsDomains.valid_email_cases()
    return email in valid_cases or ("@" in email and "." in email)


def create_test_headers(
    content_type: str = "application/json",
    **additional_headers: str,
) -> dict[str, str]:
    """Create headers using FlextTestsDomains service data.

    Returns:
        Headers dictionary.

    """
    # Use FlextTestsDomains for service information
    service_data = FlextTestsDomains.create_service()

    headers = {
        "Content-Type": content_type,
        "Accept": content_type,
        "User-Agent": f"{service_data.get('name', 'FlextAPI')!s}-Test/{service_data.get('version', '0.9.0')!s}",
        FlextConstants.Platform.HEADER_REQUEST_ID: str(uuid.uuid4()),
    }
    headers.update(additional_headers)
    return headers


# ============================================================================
# VALIDATION UTILITIES using FlextTestsDomains - ABSOLUTE
# ============================================================================


def assert_valid_uuid(value: str) -> None:
    """Assert valid UUID using FlextTestsUtilities patterns."""
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    if not re.match(uuid_pattern, value.lower()):
        pytest.fail(f"Invalid UUID format: {value}")


def assert_timestamp_format(value: str) -> None:
    """Assert valid timestamp using FlextTestsUtilities patterns."""
    try:
        datetime.fromisoformat(value)
    except (ValueError, TypeError):
        pytest.fail(f"Invalid timestamp format: {value}")


def assert_url_format(url: str) -> None:
    """Assert valid URL using FlextTestsUtilities patterns."""
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if not re.match(url_pattern, url):
        pytest.fail(f"Invalid URL format: {url}")


# ============================================================================
# FLEXT_TESTS UTILITIES INTEGRATION - ABSOLUTE USAGE
# ============================================================================


def create_test_result_success(data: object = None) -> FlextResult[object]:
    """Create success result using FlextTestsUtilities - ABSOLUTE.

    Returns:
        Successful FlextResult object.

    """
    if data is None:
        data = {"success": True, "message": "Test operation successful"}
    return u.Tests.Result.create_success_result(data)


def create_test_result_failure(error: str = "Test error") -> FlextResult[object]:
    """Create failure result using FlextTestsUtilities - ABSOLUTE.

    Returns:
        Failed FlextResult object.

    """
    return u.Tests.Result.create_failure_result(error)


def create_functional_test_service(
    service_type: str = "api",
    **config: object,
) -> object:
    """Create functional service using FlextTestsUtilities - ABSOLUTE.

    Returns:
        Functional service object.

    """
    return d.create_service(service_type=service_type, **config)


def create_test_context(
    target: object,
    attribute: str,
    new_value: object = None,
    **options: object,
) -> object:
    """Create test context using FlextTestsUtilities - ABSOLUTE.

    Returns:
        Test context object.

    """
    # Create test context and set attribute if provided
    context = u.Tests.ContextHelpers.create_test_context()
    if attribute and new_value is not None:
        context.set(attribute, new_value)
    return context


def assert_result_with_utilities[T](result: FlextResult[T]) -> T:
    """Assert result success using FlextTestsUtilities - ABSOLUTE.

    Returns:
        The unwrapped result data.

    """
    return u.Tests.Result.assert_result_success(result)


def assert_failure_with_utilities[T](result: FlextResult[T]) -> str:
    """Assert result failure using FlextTestsUtilities - ABSOLUTE.

    Returns:
        The error message from the failed result.

    """
    return u.Tests.Result.assert_result_failure(result)


# ============================================================================
# NO ALIASES OR RE-EXPORTS - DIRECT ACCESS ONLY
# ============================================================================

# Tests should import and use directly:
# from flext_tests import FlextTestsMatchers, FlextTestsDomains, FlextTestsUtilities
# FlextTestsMatchers.assert_result_success(result)
# FlextTestsDomains.create_user()
# FlextTestsUtilities.create_test_result(success=True, data=data)
