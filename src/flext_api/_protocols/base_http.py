"""HTTP client protocol shard."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_api import c, p, t


class FlextApiProtocolsHttpClient:
    """HTTP client protocol shard."""

    @runtime_checkable
    class HttpClient(Protocol):
        """Protocol for generic HTTP client implementations."""

        def delete(
            self, url: str, **kwargs: t.JsonValue
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP DELETE request."""
            ...

        def get(
            self, url: str, **kwargs: t.JsonValue
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP GET request."""
            ...

        def post(
            self, url: str, **kwargs: t.JsonValue
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP POST request."""
            ...

        def put(
            self, url: str, **kwargs: t.JsonValue
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP PUT request."""
            ...

        def request(
            self, method: c.Api.Method | str, url: str, **kwargs: t.JsonValue
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute an HTTP request."""
            ...


__all__: list[str] = ["FlextApiProtocolsHttpClient"]
