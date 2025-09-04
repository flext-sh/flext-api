"""API testing utilities for flext-api.

Provides common assertions and object creation for API testing.
"""

from __future__ import annotations

from typing import TypeVar

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiModels,
)
from tests.support.factories.api_factories import ApiRequest, ApiResponse

# Type variable for generic FlextResult operations
T = TypeVar("T")


def assert_flext_result_success(
    result: FlextResult[T], expected_value: T | None = None
) -> None:
    """Assert FlextResult is successful with optional value check."""
    if not result.success:
        pytest.fail(f"Expected success but got error: {result.error}")
    if expected_value is not None and result.value != expected_value:
        pytest.fail(f"Expected value {expected_value} but got {result.value}")


def assert_flext_result_failure[T](
    result: FlextResult[T], expected_error: str | None = None
) -> None:
    """Assert FlextResult is failure with optional error message check."""
    if result.success:
        pytest.fail(f"Expected failure but got success: {result.value}")
    if expected_error is not None and expected_error not in str(result.error):
        pytest.fail(
            f"Expected error containing '{expected_error}' but got: {result.error}"
        )


def create_test_request(
    method: str = "GET",
    url: str = "https://httpbin.org/get",
    headers: dict[str, str] | None = None,
    params: dict[str, object] | None = None,
    timeout: float = 30.0,
) -> FlextApiModels.ApiRequest:
    """Create test request - MODERN Builder Pattern using flext-core patterns."""
    # Use the modern Builder Pattern to eliminate parameter complexity

    builder = ApiRequest().with_method(method).with_url(url).with_timeout(timeout)

    if headers is not None:
        builder = builder.with_headers(headers)
    if params is not None:
        builder = builder.with_params(params)

    return builder.build()


def create_test_response(
    status_code: int = 200,
    data: dict[str, object] | list[object] | str | bytes | None = None,
    headers: dict[str, str] | None = None,
    elapsed_time: float = 0.5,
    request_id: str | None = None,
    *,
    from_cache: bool = False,
) -> FlextApiModels.HttpResponse:
    """Create test response - MODERN Builder Pattern using flext-core patterns."""
    # Use the modern Builder Pattern to eliminate parameter complexity

    builder = (
        ApiResponse()
        .with_status_code(status_code)
        .with_elapsed_time(elapsed_time)
        .with_cache(from_cache)
    )

    if headers is not None:
        builder = builder.with_headers(headers)
    if data is not None:
        builder = builder.with_data(data)
    if request_id is not None:
        builder = builder.with_request_id(request_id)

    return builder.build()
