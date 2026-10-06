"""The public HTTP class contracts own httpx construction and exception identity.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx
from flext_tests import tm

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


class TestsFlextApiHttpxContracts:
    """Observable construction and exception contracts of the HTTP owner."""

    @staticmethod
    def test_client_primitives_are_the_owner_types() -> None:
        """Client factories and response type are the httpx owner types."""
        tm.that(HttpxClient is httpx.Client, eq=True)
        tm.that(HttpxAsyncClient is httpx.AsyncClient, eq=True)
        tm.that(HttpxResponse is httpx.Response, eq=True)

    @staticmethod
    def test_exception_primitives_are_the_owner_types() -> None:
        """Exception types match the httpx owner for consumer except clauses."""
        tm.that(HttpxHTTPError is httpx.HTTPError, eq=True)
        tm.that(HttpxHTTPStatusError is httpx.HTTPStatusError, eq=True)
        tm.that(HttpxRequestError is httpx.RequestError, eq=True)
        tm.that(HttpxTimeoutException is httpx.TimeoutException, eq=True)

    @staticmethod
    def test_conflict_status_is_derived_from_the_owner() -> None:
        """The conflict constant stays int-typed and equals the httpx owner."""
        conflict = p.Api.Httpx.CONFLICT
        tm.that(type(conflict), eq=int)
        tm.that(conflict, eq=int(httpx.codes.CONFLICT))

    @staticmethod
    def test_client_constructs_through_the_public_contract() -> None:
        """A real client constructs and closes through the owner type."""
        client = HttpxClient(timeout=2.0)
        try:
            tm.that(client.is_closed, eq=False)
        finally:
            client.close()
        tm.that(client.is_closed, eq=True)
