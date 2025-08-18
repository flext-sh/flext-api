"""Test plugins and http."""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
)


class _CM:
    """Context manager for fake response."""

    def __init__(self, resp: _FakeResponse) -> None:
        """Initialize context manager with fake response."""
        self._resp = resp

    async def __aenter__(self) -> _FakeResponse:
        """Enter context manager."""
        return self._resp

    async def __aexit__(self, *_args: object, **_kwargs: object) -> None:
        """Exit context manager."""
        return


class _FakeResponse:
    def __init__(
        self,
        status: int,
        headers: dict[str, str],
        json_obj: object,
        text_value: str,
    ) -> None:
        self.status = status
        self.headers = headers
        self._json_obj = json_obj
        self._text_value = text_value

    async def json(self) -> object:
        if isinstance(self._json_obj, Exception):
            raise self._json_obj
        return self._json_obj

    async def text(self) -> str:
        return self._text_value


class _FakeSession:
    def __init__(self, resp: _FakeResponse) -> None:
        self._resp = resp
        self.closed = False

    def request(self, *_args: object, **_kwargs: object) -> _CM:
        return _CM(self._resp)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_perform_http_request_success_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test perform_http_request success json path."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example", timeout=5.0),
    )

    # Force network path
    monkeypatch.setattr(client, "_is_external_calls_disabled", lambda: False)
    resp = _FakeResponse(200, {"Content-Type": "application/json"}, {"ok": True}, "")
    client._session = _FakeSession(resp)

    req = FlextApiClientRequest(
        method="GET",
        url="https://api.example/x",
        params={"a": 1},
    )
    r = await client._perform_http_request(req)
    assert r.success
    assert r.data
    assert r.data.status_code == 200
    assert r.data.data == {"ok": True}


@pytest.mark.asyncio
async def test_perform_http_request_text_jsonlike(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test perform_http_request text jsonlike path."""
    client = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example", timeout=5.0),
    )
    monkeypatch.setattr(client, "_is_external_calls_disabled", lambda: False)
    resp = _FakeResponse(200, {"Content-Type": "text/plain"}, None, '{"x":1}')
    client._session = _FakeSession(resp)
    req = FlextApiClientRequest(method="GET", url="https://api.example/y")
    r = await client._perform_http_request(req)
    assert r.success
    assert isinstance(r.data, FlextApiClientResponse)
    assert r.data.data == {"x": 1}


class _PluginFail:
    """Plugin that fails before request."""

    enabled = True

    async def before_request(
        self,
        _request: object,
        _context: object = None,
    ) -> FlextResult:
        return FlextResult.fail("nope")


class _PluginModify:
    """Plugin that modifies request."""

    enabled = True

    async def before_request(
        self,
        request: FlextApiClientRequest,
        _context: object = None,
    ) -> FlextApiClientRequest:
        """Modify request headers."""
        new_headers = dict(request.headers)
        new_headers["X"] = "1"
        return FlextApiClientRequest(
            method=request.method,
            url=request.url,
            headers=new_headers,
            params=request.params,
            json_data=request.json_data,
            data=request.data,
            timeout=request.timeout,
        )


class _PluginAfterFail:
    """Plugin that fails after response."""

    enabled = True

    async def after_response(
        self,
        _response: object,
        _context: object = None,
    ) -> FlextResult:
        return FlextResult.fail("bad")


class _PluginAfterModify:
    """Plugin that modifies response."""

    enabled = True

    async def after_response(
        self,
        response: FlextApiClientResponse,
        _context: object = None,
    ) -> FlextResult:
        # modify data
        new_resp = FlextApiClientResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data={"mod": True},
            elapsed_time=response.elapsed_time,
        )
        return FlextResult.ok(new_resp)


@pytest.mark.usefixtures("monkeypatch")
@pytest.mark.asyncio
async def test_plugins_before_and_after_paths() -> None:
    """Test plugins before and after paths."""
    # before_request fail
    c1 = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example"),
        plugins=[_PluginFail()],
    )
    req = FlextApiClientRequest(method="GET", url="https://api.example/p")
    r1 = await c1._process_plugins_before_request(req, {})
    assert not r1.success
    assert "Plugin" in (r1.error or "")

    # before_request modify
    c2 = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example"),
        plugins=[_PluginModify()],
    )
    r2 = await c2._process_plugins_before_request(req, {})
    assert r2.success
    assert r2.data
    assert r2.data.headers.get("X") == "1"

    # after_response fail
    c3 = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example"),
        plugins=[_PluginAfterFail()],
    )
    base_resp = FlextApiClientResponse(status_code=200, data={})
    r3 = await c3._process_plugins_after_response(base_resp, {})
    assert not r3.success
    assert "Plugin" in (r3.error or "")

    # after_response modify
    c4 = FlextApiClient(
        FlextApiClientConfig(base_url="https://api.example"),
        plugins=[_PluginAfterModify()],
    )
    r4 = await c4._process_plugins_after_response(base_resp, {})
    assert r4.success
    assert r4.data
    assert r4.data.data == {"mod": True}


def test_format_request_error_variants() -> None:
    """Test format request error variants."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://api.example"))
    err1 = client._format_request_error(
        FlextResult.fail("HTTP session not available: x"),
        "GET",
    )
    assert not err1.success
    assert (err1.error or "").startswith("HTTP session not available")
    err2 = client._format_request_error(FlextResult.fail("boom"), "POST")
    assert not err2.success
    assert (err2.error or "").startswith("Failed to make POST request")


@pytest.mark.asyncio
async def test_build_stub_response_variants() -> None:
    """Test build_stub_response variants."""
    client = FlextApiClient(FlextApiClientConfig(base_url="https://httpbin.org"))
    # Invalid URL format
    bad_req = FlextApiClientRequest(method="GET", url="ftp://x")
    bad = client._build_stub_response(bad_req)
    assert not bad.success

    # DNS failure
    bad2 = client._build_stub_response(
        FlextApiClientRequest(method="GET", url="https://nonexistent-xyz.invalid/"),
    )
    assert not bad2.success

    # Status
    ok_status = client._build_stub_response(
        FlextApiClientRequest(method="GET", url="https://httpbin.org/status/404"),
    )
    assert ok_status.success
    assert ok_status.data.status_code == 404

    # JSON path
    ok_json = client._build_stub_response(
        FlextApiClientRequest(method="GET", url="https://httpbin.org/json"),
    )
    assert ok_json.success
    assert isinstance(ok_json.data.data, dict)

    # Headers echo
    ok_headers = client._build_stub_response(
        FlextApiClientRequest(
            method="GET",
            url="https://httpbin.org/headers",
            headers={"A": "1"},
        ),
    )
    assert ok_headers.success
    assert ok_headers.data.data == {"headers": {"A": "1"}}

    # Post json
    ok_post = client._build_stub_response(
        FlextApiClientRequest(
            method="POST",
            url="https://httpbin.org/post",
            json_data={"a": 1},
        ),
    )
    assert ok_post.success
    assert ok_post.data.data == {"json": {"a": 1}}

    # Delay path
    ok_delay = client._build_stub_response(
        FlextApiClientRequest(method="GET", url="https://httpbin.org/delay/1"),
    )
    assert ok_delay.success
    assert ok_delay.data.data == {"delay": 1}
