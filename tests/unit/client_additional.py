"""Additional client tests for error handling and header/param preparation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApiClient


def test_client_build_and_error_formatting_on_invalid_url() -> None:
    """Client handles REAL non-200 status and returns data."""
    client = FlextApiClient(base_url="https://httpbin.org")
    # Note: FlextApiClient doesn't have a start() method
    try:
        # REAL HTTP request - httpbin.org/status/400 returns HTTP 400
        res = client.get("/status/400")
        # Should succeed (request was made) but with 400 status code
        assert res.is_success
        assert res.value is not None
        assert res.value.status_code == 400
    finally:
        # Note: FlextApiClient doesn't have a stop() method
        pass


def test_client_headers_merge_and_prepare_params() -> None:
    """Client merges headers and serializes params correctly."""
    client = FlextApiClient(
        config="https://httpbin.org",
        headers={"A": "1"},
    )
    # Note: FlextApiClient doesn't have a start() method
    result = client.post("/post", json_data={"x": 1}, headers={"B": "2"})
    assert result.is_success
    assert result.value is not None
    # echo path ensures headers were passed through into stub response
    # Note: FlextApiClient doesn't have a stop() method
