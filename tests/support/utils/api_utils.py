"""
API testing utilities for flext-api.

Provides common assertions and object creation for API testing.
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextResult

from flext_api import FlextApiClientRequest, FlextApiClientResponse


def assert_flext_result_success(result: FlextResult[Any], expected_value: Any = None) -> None:
    """Assert FlextResult is successful with optional value check."""
    assert result.success, f"Expected success but got error: {result.error}"
    if expected_value is not None:
        assert result.value == expected_value


def assert_flext_result_failure(result: FlextResult[Any], expected_error: str = None) -> None:
    """Assert FlextResult is failure with optional error message check."""
    assert not result.success, f"Expected failure but got success: {result.value}"
    if expected_error is not None:
        assert expected_error in str(result.error)


def create_test_request(
    method: str = "GET",
    url: str = "https://httpbin.org/get",
    **kwargs: Any,
) -> FlextApiClientRequest:
    """Create test request with sensible defaults."""
    return FlextApiClientRequest(
        method=method,
        url=url,
        **kwargs,
    )


def create_test_response(
    status_code: int = 200,
    data: Any = None,
    **kwargs: Any,
) -> FlextApiClientResponse:
    """Create test response with sensible defaults."""
    return FlextApiClientResponse(
        status_code=status_code,
        data=data or {"message": "success"},
        **kwargs,
    )