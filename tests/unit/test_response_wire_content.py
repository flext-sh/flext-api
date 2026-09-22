"""Public HTTP client contract for parsed and exact response payloads."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import cast

from flext_tests import tm

from flext_api import FlextApiClient, FlextApiSettings, m


class TestsFlextApiResponseWireContent:
    """The public client preserves wire bytes beside the validated JSON body."""

    @staticmethod
    @contextmanager
    def _server(payload: bytes) -> Generator[str]:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = cast("tuple[str, int]", server.server_address)
            yield f"http://{host}:{port}"
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def test_request_preserves_wire_content_and_typed_body(self) -> None:
        """A real local exchange exposes both raw bytes and parsed JSON."""
        payload = b'{"answer":"ok"}'
        with self._server(payload) as base_url:
            client = FlextApiClient(
                runtime_settings=FlextApiSettings(base_url=base_url)
            )
            result = client.request(m.Api.HttpRequest(url=base_url, method="GET"))

        tm.that(result.success, eq=True)
        tm.that(result.value.content, eq=payload)
        tm.that(result.value.body, eq={"answer": "ok"})


__all__: list[str] = ["TestsFlextApiResponseWireContent"]
