"""The public HTTP class contracts own httpx construction and exception identity."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from flext_api import (
    HttpxAsyncClient,
    HttpxClient,
    HttpxHTTPError,
    HttpxHTTPStatusError,
    HttpxRequestError,
    HttpxResponse,
    HttpxTimeoutException,
    p,
)

if TYPE_CHECKING:
    from flext_core import t


class TestsFlextApiHttpxContracts:
    """Observable construction and exception contracts of the HTTP owner."""

    def test_client_primitives_are_the_owner_types(self) -> None:
        """Client factories and response type are the httpx owner types."""
        assert HttpxClient is httpx.Client
        assert HttpxAsyncClient is httpx.AsyncClient
        assert HttpxResponse is httpx.Response

    def test_exception_primitives_are_the_owner_types(self) -> None:
        """Exception types match the httpx owner for consumer except clauses."""
        assert HttpxHTTPError is httpx.HTTPError
        assert HttpxHTTPStatusError is httpx.HTTPStatusError
        assert HttpxRequestError is httpx.RequestError
        assert HttpxTimeoutException is httpx.TimeoutException

    def test_conflict_status_is_derived_from_the_owner(self) -> None:
        """The conflict constant stays int-typed and equals the httpx owner."""
        conflict = p.Api.Httpx.CONFLICT
        assert isinstance(conflict, int)
        assert conflict == int(httpx.codes.CONFLICT)

    def test_client_constructs_through_the_public_contract(self) -> None:
        """A real client constructs and closes through the owner type."""
        client = HttpxClient(timeout=2.0)
        try:
            assert not client.is_closed
        finally:
            client.close()
        assert client.is_closed


__all__: t.VariadicTuple[str] = ("TestsFlextApiHttpxContracts",)
