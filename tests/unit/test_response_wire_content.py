"""Public HTTP client contract for parsed and exact response payloads.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import cast

from tests import FlextApi, m, settings, tm


class TestsFlextApiResponseWireContent:
    """The public client preserves wire bytes beside the validated JSON body."""

    @staticmethod
    @contextmanager
    def _server(
        payload: bytes,
        seen: list[str] | None = None,
        status: int = 200,
    ) -> Generator[str]:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if seen is not None:
                    seen.append(self.path)
                self.send_response(status)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(payload)))
                self.end_headers()
                if payload:
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
            api = FlextApi(
                runtime_settings=settings.clone(Api={"base_url": base_url}),
            )
            result = api.request(m.Api.HttpRequest(url=base_url, method="GET"))

        tm.ok(result.success)
        tm.that(result.value.content, eq=payload)
        tm.that(result.value.body, eq={"answer": "ok"})

    def test_absolute_query_reaches_the_wire(self) -> None:
        """An absolute URL keeps its query instead of being rebased or emptied."""
        seen: list[str] = []
        with self._server(b'{"ok":true}', seen) as base_url:
            api = FlextApi(
                runtime_settings=settings.clone(Api={"base_url": base_url}),
            )
            result = api.request(m.Api.HttpRequest(url=f"{base_url}/extracts?pagina=2"))

        tm.ok(result.success)
        tm.that(seen, eq=["/extracts?pagina=2"])

    def test_request_wire_preserves_a_bodyless_non_200(self) -> None:
        """The raw wire contract keeps the status and empty content."""
        with self._server(b"", status=204) as base_url:
            api = FlextApi(
                runtime_settings=settings.clone(Api={"base_url": base_url}),
            )
            result = api.client.request_wire(m.Api.HttpRequest(url=base_url))

        tm.ok(result.success)
        tm.that(result.value.status_code, eq=204)
        tm.that(result.value.content, eq=b"")
