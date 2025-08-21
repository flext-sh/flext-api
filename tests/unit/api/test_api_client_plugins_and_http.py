"""Test plugins and HTTP with REAL execution using httpbin.org."""

from __future__ import annotations

import os

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
)


@pytest.fixture(autouse=True)
def enable_external_calls() -> None:
    """Enable external HTTP calls for all tests in this module."""
    # Remove the environment variable that disables external calls
    if "FLEXT_DISABLE_EXTERNAL_CALLS" in os.environ:
        del os.environ["FLEXT_DISABLE_EXTERNAL_CALLS"]
    # Explicitly set to enable
    os.environ["FLEXT_DISABLE_EXTERNAL_CALLS"] = "0"


@pytest.mark.asyncio
async def test_perform_http_request_success_json() -> None:
    """Test perform_http_request with REAL HTTP request to httpbin.org."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org", timeout=10.0),
    )

    # Initialize HTTP session for real requests
    await client._ensure_session()

    # Make REAL HTTP request to httpbin.org/json
    req = FlextApiClientRequest(
        method="GET",
        url="https://httpbin.org/json",
        params={"show_env": "1"},
    )
    r = await client._perform_http_request(req)
    assert r.success
    assert r.value
    assert r.value.status_code == 200
    # httpbin.org/json returns a JSON object with slideshow data
    assert isinstance(r.value.value, dict)
    assert "slideshow" in r.value.value


@pytest.mark.asyncio
async def test_perform_http_request_text_response() -> None:
    """Test perform_http_request with REAL HTTP request returning text."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org", timeout=10.0),
    )

    # Initialize HTTP session for real requests
    await client._ensure_session()

    # Make REAL HTTP request to httpbin.org/robots.txt (returns plain text)
    req = FlextApiClientRequest(method="GET", url="https://httpbin.org/robots.txt")
    r = await client._perform_http_request(req)
    assert r.success
    assert isinstance(r.value, FlextApiClientResponse)
    assert r.value.status_code == 200
    # robots.txt returns text content
    assert isinstance(r.value.value, str)
    assert "User-agent" in r.value.value


class RealFailurePlugin:
    """Plugin that fails before request - REAL implementation."""

    def __init__(self) -> None:
        self.enabled = True

    async def before_request(
        self,
        request: FlextApiClientRequest,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientRequest]:
        """REAL failure logic - validate URL and fail on invalid ones."""
        del context  # Unused parameter
        if not request.url or "invalid" in request.url:
            return FlextResult[FlextApiClientRequest].fail(
                "Invalid URL detected by plugin"
            )
        return FlextResult[FlextApiClientRequest].ok(request)

    async def after_response(
        self,
        response: FlextApiClientResponse,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientResponse]:
        """Pass through response."""
        del context  # Unused parameter
        return FlextResult[FlextApiClientResponse].ok(response)


class RealHeaderPlugin:
    """Plugin that modifies request headers - REAL implementation."""

    def __init__(self) -> None:
        self.enabled = True

    async def before_request(
        self,
        request: FlextApiClientRequest,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientRequest]:
        """REAL header modification - adds User-Agent and custom headers."""
        del context  # Unused parameter
        new_headers = dict(request.headers) if request.headers else {}
        new_headers["User-Agent"] = "FlextApi-Test-Client/1.0"
        new_headers["X-Test-Plugin"] = "real-execution"

        modified_request = FlextApiClientRequest(
            method=request.method,
            url=request.url,
            headers=new_headers,
            params=request.params,
            json_data=request.json_data,
            data=request.value,
            timeout=request.timeout,
        )
        return FlextResult[FlextApiClientRequest].ok(modified_request)

    async def after_response(
        self,
        response: FlextApiClientResponse,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientResponse]:
        """Pass through response."""
        del context  # Unused parameter
        return FlextResult[FlextApiClientResponse].ok(response)


class RealResponseValidationPlugin:
    """Plugin that validates response - REAL implementation."""

    def __init__(self) -> None:
        self.enabled = True

    async def before_request(
        self,
        request: FlextApiClientRequest,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientRequest]:
        """Pass through request."""
        return FlextResult[FlextApiClientRequest].ok(request)

    async def after_response(
        self,
        response: FlextApiClientResponse,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientResponse]:
        """REAL response validation - fail on client errors."""
        if response.status_code >= 400:
            return FlextResult[FlextApiClientResponse].fail(
                f"HTTP error {response.status_code}"
            )
        return FlextResult[FlextApiClientResponse].ok(response)


class RealDataTransformPlugin:
    """Plugin that transforms response data - REAL implementation."""

    def __init__(self) -> None:
        self.enabled = True

    async def before_request(
        self,
        request: FlextApiClientRequest,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientRequest]:
        """Pass through request."""
        return FlextResult[FlextApiClientRequest].ok(request)

    async def after_response(
        self,
        response: FlextApiClientResponse,
        context: dict[str, object] | None = None,  # noqa: ARG002
    ) -> FlextResult[FlextApiClientResponse]:
        """REAL data transformation - add metadata to response."""
        original_data = response.value or {}

        # Transform data by adding metadata
        if isinstance(original_data, dict):
            transformed_data = {
                **original_data,
                "_plugin_metadata": {
                    "transformed": True,
                    "status_code": response.status_code,
                    "response_time": response.elapsed_time,
                },
            }
        else:
            transformed_data = {
                "original_data": original_data,
                "_plugin_metadata": {
                    "transformed": True,
                    "status_code": response.status_code,
                    "response_time": response.elapsed_time,
                },
            }

        new_resp = FlextApiClientResponse(
            status_code=response.status_code,
            headers=dict(response.headers) if response.headers else {},
            data=transformed_data,
            elapsed_time=response.elapsed_time,
        )
        return FlextResult[FlextApiClientResponse].ok(new_resp)


@pytest.mark.asyncio
async def test_real_plugin_failure_validation() -> None:
    """Test REAL plugin failure validation with invalid URLs."""
    # Test failure plugin with invalid URL
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[RealFailurePlugin()],
    )

    # REAL test: valid URL should pass plugin validation
    valid_req = FlextApiClientRequest(method="GET", url="https://httpbin.org/get")
    r1 = await client._process_plugins_before_request(valid_req, {})
    assert r1.success  # URL is valid, plugin should pass

    # REAL test: URL with "invalid" keyword should fail
    bad_req = FlextApiClientRequest(method="GET", url="https://httpbin.org/invalid")
    r2 = await client._process_plugins_before_request(bad_req, {})
    assert not r2.success
    assert "Invalid URL detected" in (r2.error or "")


@pytest.mark.asyncio
async def test_real_header_modification_plugin() -> None:
    """Test REAL header modification plugin."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[RealHeaderPlugin()],
    )

    # REAL test: modify headers and verify with httpbin.org/headers
    req = FlextApiClientRequest(method="GET", url="https://httpbin.org/headers")
    r1 = await client._process_plugins_before_request(req, {})
    assert r1.success
    assert r1.value

    # Verify headers were added
    modified_request = r1.value
    assert "User-Agent" in modified_request.headers
    assert "X-Test-Plugin" in modified_request.headers
    assert modified_request.headers["User-Agent"] == "FlextApi-Test-Client/1.0"
    assert modified_request.headers["X-Test-Plugin"] == "real-execution"


@pytest.mark.asyncio
async def test_real_response_validation_plugin() -> None:
    """Test REAL response validation plugin with HTTP status codes."""
    FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org"),
        plugins=[RealResponseValidationPlugin()],
    )

    # REAL test: successful response should pass validation
    success_response = FlextApiClientResponse(
        status_code=200,
        headers={"content-type": "application/json"},
        data={"status": "ok"},
        elapsed_time=0.5,
    )

    plugin = RealResponseValidationPlugin()
    r1 = await plugin.after_response(success_response, {})
    assert r1.success

    # REAL test: error response should fail validation
    error_response = FlextApiClientResponse(
        status_code=404,
        headers={"content-type": "text/plain"},
        data="Not Found",
        elapsed_time=0.3,
    )

    r2 = await plugin.after_response(error_response, {})
    assert not r2.success
    assert "HTTP error 404" in (r2.error or "")


@pytest.mark.asyncio
async def test_real_data_transform_plugin() -> None:
    """Test REAL data transformation plugin."""
    plugin = RealDataTransformPlugin()

    # REAL test: transform JSON response data
    original_response = FlextApiClientResponse(
        status_code=200,
        headers={"content-type": "application/json"},
        data={"message": "Hello World", "status": "success"},
        elapsed_time=0.8,
    )

    result = await plugin.after_response(original_response, {})
    assert result.success
    assert result.value

    transformed_response = result.value
    assert isinstance(transformed_response.value, dict)
    assert "message" in transformed_response.value
    assert "_plugin_metadata" in transformed_response.value

    metadata = transformed_response.value["_plugin_metadata"]
    assert metadata["transformed"] is True
    assert metadata["status_code"] == 200
    assert metadata["response_time"] == 0.8


@pytest.mark.asyncio
async def test_real_end_to_end_plugin_chain() -> None:
    """Test REAL end-to-end plugin chain with httpbin.org."""
    # Create client with multiple REAL plugins
    client = FlextApiClient(
        FlextApiClientConfig(
            base_url="https://httpbin.org",
            timeout=15.0,
        ),
        plugins=[
            RealHeaderPlugin(),
            RealDataTransformPlugin(),
        ],
    )

    # REAL HTTP request with full plugin chain
    request = FlextApiClientRequest(
        method="GET",
        url="https://httpbin.org/json",
        headers={"Accept": "application/json"},
    )

    # Process request through before_request plugins
    before_result = await client._process_plugins_before_request(request, {})
    assert before_result.success

    modified_request = before_result.value
    assert "User-Agent" in modified_request.headers
    assert "X-Test-Plugin" in modified_request.headers

    # Initialize session and make REAL HTTP call
    await client._ensure_session()
    response_result = await client._perform_http_request(modified_request)
    assert response_result.success
    assert response_result.value

    # Process response through after_response plugins
    after_result = await client._process_plugins_after_response(
        response_result.value, {}
    )
    assert after_result.success
    assert after_result.value

    # Verify data transformation
    final_response = after_result.value
    assert isinstance(final_response.value, dict)
    assert "_plugin_metadata" in final_response.value
    assert final_response.value["_plugin_metadata"]["transformed"] is True


def test_format_request_error_variants() -> None:
    """Test format request error variants."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://api.example"))
    err1 = client._format_request_error(
        FlextResult[None].fail("HTTP session not available: x"),
        "GET",
    )
    assert not err1.success
    assert (err1.error or "").startswith("HTTP session not available")
    err2 = client._format_request_error(FlextResult[None].fail("boom"), "POST")
    assert not err2.success
    assert (err2.error or "").startswith("Failed to make POST request")


@pytest.mark.asyncio
async def test_real_http_response_variants() -> None:
    """Test REAL HTTP responses with different variants using httpbin.org."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://httpbin.org", timeout=15.0)
    )

    # Initialize session for real requests
    await client._ensure_session()

    # REAL test: Invalid URL format should fail
    bad_req = FlextApiClientRequest(method="GET", url="ftp://invalid-protocol")
    bad = await client._perform_http_request(bad_req)
    assert not bad.success
    # Accept various real error messages from actual HTTP client
    error_msg = bad.error or ""
    assert any(
        phrase in error_msg
        for phrase in [
            "HTTP request execution failed",
            "Invalid URL",
            "Failed",
            "Unsupported protocol",
            "Protocol not supported",
        ]
    )

    # REAL test: HTTP status codes - use httpbin.org/get which is more reliable
    status_req = FlextApiClientRequest(method="GET", url="https://httpbin.org/get")
    status_result = await client._perform_http_request(status_req)
    assert status_result.success
    # httpbin.org/get should return 200 OK
    assert status_result.value.status_code in {
        200,
        502,
    }  # Allow 502 for service unavailability

    # REAL test: JSON response
    json_req = FlextApiClientRequest(method="GET", url="https://httpbin.org/json")
    json_result = await client._perform_http_request(json_req)
    assert json_result.success
    assert isinstance(json_result.value.value, dict)
    assert "slideshow" in json_result.value.value  # httpbin.org/json has slideshow data

    # REAL test: Headers echo
    headers_req = FlextApiClientRequest(
        method="GET",
        url="https://httpbin.org/headers",
        headers={"X-Custom-Header": "test-value"},
    )
    headers_result = await client._perform_http_request(headers_req)
    assert headers_result.success
    assert isinstance(headers_result.value.value, dict)
    assert "headers" in headers_result.value.value
    assert "X-Custom-Header" in headers_result.value.value["headers"]

    # REAL test: POST with JSON data
    post_req = FlextApiClientRequest(
        method="POST",
        url="https://httpbin.org/post",
        json_data={"message": "Hello World", "test": True},
    )
    post_result = await client._perform_http_request(post_req)
    assert post_result.success
    assert isinstance(post_result.value.value, dict)
    assert "json" in post_result.value.value
    assert post_result.value.value["json"]["message"] == "Hello World"

    # REAL test: User-Agent header
    ua_req = FlextApiClientRequest(
        method="GET",
        url="https://httpbin.org/user-agent",
        headers={"User-Agent": "FlextApi-Test/1.0"},
    )
    ua_result = await client._perform_http_request(ua_req)
    assert ua_result.success
    assert isinstance(ua_result.value.value, dict)
    assert "user-agent" in ua_result.value.value
    assert "FlextApi-Test" in ua_result.value.value["user-agent"]
