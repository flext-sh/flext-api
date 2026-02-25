"""Comprehensive tests for protocol implementations.

Tests validate protocol implementation imports and exports.
No mocks - uses actual imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterator

import flext_api.protocol_impls.http as http_module
from flext_api import (
    BaseProtocolImplementation,
    FlextWebClientImplementation,
    FlextApiModels,
    FlextWebProtocolPlugin,
    RFCProtocolImplementation,
    SSEProtocolPlugin,
    StorageBackendImplementation,
    WebSocketProtocolPlugin,
)


class TestProtocolImpls:
    """Test protocol implementations imports."""

    def test_all_protocol_impls_importable(self) -> None:
        """Test that all protocol implementation classes are importable."""
        assert BaseProtocolImplementation is not None
        assert FlextWebClientImplementation is not None
        assert FlextWebProtocolPlugin is not None
        assert RFCProtocolImplementation is not None
        assert SSEProtocolPlugin is not None
        assert StorageBackendImplementation is not None
        assert WebSocketProtocolPlugin is not None


class _FakeStreamingResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self.chunk_sizes: list[int] = []

    def __enter__(self) -> _FakeStreamingResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        return None

    def iter_bytes(self, *, chunk_size: int) -> Iterator[bytes]:
        self.chunk_sizes.append(chunk_size)
        index = 0
        while index < len(self._payload):
            next_index = index + chunk_size
            yield self._payload[index:next_index]
            index = next_index


class _FakeHttpClient:
    def __init__(self, response: _FakeStreamingResponse, **kwargs: object) -> None:
        self.response = response
        self.client_kwargs = kwargs
        self.stream_call_count = 0

    def __enter__(self) -> _FakeHttpClient:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, str] | None,
        json: object | None,
        content: str | bytes | None,
        timeout: float | None,
    ) -> _FakeStreamingResponse:
        _ = method, url, headers, params, json, content, timeout
        self.stream_call_count += 1
        return self.response


def test_http_stream_request_is_deferred_and_yields_chunks(monkeypatch) -> None:
    fake_response = _FakeStreamingResponse(b"hello-world")
    created_clients: list[_FakeHttpClient] = []

    def fake_client_factory(*_args: object, **kwargs: object) -> _FakeHttpClient:
        client = _FakeHttpClient(fake_response, **kwargs)
        created_clients.append(client)
        return client

    monkeypatch.setattr(http_module.httpx, "Client", fake_client_factory)

    plugin = FlextWebProtocolPlugin()
    request = FlextApiModels.HttpRequest(
        method="GET",
        url="https://example.com/stream",
        headers={},
        body={},
        timeout=5.0,
    )

    result = plugin.stream_request(request, chunk_size=4)

    assert result.is_success
    assert result.value is not None
    assert created_clients == []

    stream_iter = result.value
    assert isinstance(stream_iter, Iterator)
    chunks = list(stream_iter)

    assert chunks == [b"hell", b"o-wo", b"rld"]
    assert len(created_clients) == 1
    assert created_clients[0].stream_call_count == 1
    assert fake_response.chunk_sizes == [4]


def test_http_stream_request_rejects_invalid_chunk_size() -> None:
    plugin = FlextWebProtocolPlugin()
    request = FlextApiModels.HttpRequest(
        method="GET",
        url="https://example.com/stream",
        headers={},
        body={},
        timeout=5.0,
    )

    result = plugin.stream_request(request, chunk_size=0)

    assert result.is_failure
    assert result.error == "chunk_size must be greater than 0"
