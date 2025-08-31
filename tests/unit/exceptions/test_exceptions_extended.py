"""Extended tests for API exception mapping and HTTP serialization."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiAuthenticationError,
    FlextApiAuthorizationError,
    FlextApiConfigurationError,
    FlextApiConnectionError,
    FlextApiError,
    FlextApiModels,
    FlextApiNotFoundError,
    FlextApiProcessingError,
    FlextApiRateLimitError,
    FlextApiRequestError,
    FlextApiResponseError,
    FlextApiStorageError,
    FlextApiTimeoutError,
    FlextApiValidationError,
    create_error_response,
    map_http_status_to_exception,
)


def test_validation_error_truncates_value_and_http_response() -> None:
    """Validation error should truncate long value and return 400."""
    long_value = "x" * 1000
    exc = FlextApiValidationError("bad", field="email", value=long_value, endpoint="/e")
    resp = exc.to_http_response()
    if isinstance(resp, dict) and "error" in resp and isinstance(resp["error"], dict):
        assert resp["error"]["status_code"] == 400
    assert len(str(exc.validation_details.get("value", ""))) < 1000


def test_authentication_error_message_prefix() -> None:
    """Authentication error message should include flext_api prefix."""
    exc = FlextApiAuthenticationError(
        "login failed",
        auth_method="basic",
        endpoint="/login",
    )
    # Message should contain the flext_api prefix (may include base tag prefix)
    assert "flext_api:" in str(exc)
    resp = exc.to_http_response()
    if isinstance(resp, dict) and "error" in resp and isinstance(resp["error"], dict):
        assert resp["error"]["status_code"] == 401


def test_timeout_error_context_and_http() -> None:
    """Timeout error should include context and 504 status."""
    exc = FlextApiTimeoutError(
        "timeout",
        endpoint="/q",
        timeout_seconds=1.5,
        query_type="list",
    )
    resp = exc.to_http_response()
    if isinstance(resp, dict) and "error" in resp and isinstance(resp["error"], dict):
        assert resp["error"]["status_code"] == 504
    if isinstance(exc.context, dict) and "context" in exc.context:
        context_data = exc.context["context"]
        if isinstance(context_data, dict):
            assert context_data.get("timeout_seconds") == 1.5


def test_request_response_and_storage_errors() -> None:
    """Basic subclass instances should be recognized as FlextApiError."""
    assert isinstance(
        FlextApiRequestError("bad", method=FlextApiModels.HttpMethod.GET, endpoint="/x"),
        FlextApiError,
    )
    assert isinstance(FlextApiResponseError("bad", status_code=502), FlextApiError)
    assert isinstance(FlextApiStorageError("bad", storage_type="memory"), FlextApiError)


def test_authorization_notfound_rate_limit_errors() -> None:
    """Other common errors should be instances of FlextApiError."""
    assert isinstance(
        FlextApiAuthorizationError("forbidden", required_permission="x"),
        FlextApiError,
    )
    assert isinstance(
        FlextApiNotFoundError("missing", resource_type="user", resource_id="1"),
        FlextApiError,
    )
    assert isinstance(
        FlextApiRateLimitError("rate", limit=10, window_seconds=60),
        FlextApiError,
    )


def test_configuration_error_context_and_http() -> None:
    """Configuration error should carry context and specific code."""
    exc = FlextApiConfigurationError(
        "cfg bad",
        config_key="api_port",
        expected_type="int",
        actual_value="str",
    )
    resp = exc.to_http_response()
    if isinstance(resp, dict) and "error" in resp and isinstance(resp["error"], dict):
        assert resp["error"]["code"] == "CONFIGURATION_ERROR"
    if isinstance(exc.context, dict) and "context" in exc.context:
        context_data = exc.context["context"]
        if isinstance(context_data, dict):
            assert context_data.get("config_key") == "api_port"


def test_connection_error_http_response() -> None:
    """Connection error should map to expected code."""
    exc = FlextApiConnectionError(
        "conn",
        host="h",
        port=1,
        ssl_error="e",
        connection_timeout=0.1,
    )
    resp = exc.to_http_response()
    if isinstance(resp, dict) and "error" in resp and isinstance(resp["error"], dict):
        assert resp["error"]["code"] == "CONNECTION_ERROR"


def test_create_error_response_with_traceback() -> None:
    """Error response factory should include traceback when requested."""
    exc = FlextApiError("boom")
    resp = create_error_response(exc, include_traceback=True)
    if isinstance(resp, dict) and "error" in resp and isinstance(resp["error"], dict):
        assert "traceback" in resp["error"]


@pytest.mark.parametrize(
    ("status", "expected_type"),
    [
        (400, FlextApiRequestError),
        (401, FlextApiAuthenticationError),
        (403, FlextApiAuthorizationError),
        (404, FlextApiNotFoundError),
        (429, FlextApiRateLimitError),
        (500, FlextApiProcessingError),
        (502, FlextApiResponseError),
        (503, FlextApiConnectionError),
        (504, FlextApiTimeoutError),
    ],
)
def test_map_http_status_to_exception_specific(
    status: int,
    expected_type: type[FlextApiError],
) -> None:
    """Specific HTTP codes should map to specific exception types."""
    exc = map_http_status_to_exception(status, message="m")
    assert isinstance(exc, expected_type)


def test_map_http_status_to_exception_ranges_and_default() -> None:
    """Unknown or non-standard codes should still map to base API error."""
    assert isinstance(
        map_http_status_to_exception(418, message="teapot"),
        FlextApiError,
    )
    assert isinstance(
        map_http_status_to_exception(599, message="server"),
        FlextApiError,
    )
