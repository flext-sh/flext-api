"""Real client functionality tests using flext_tests library.

Tests HTTP client with real network operations and JSON parsing.
Uses flext_tests FlextTestsMatchers and helpers for validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json

import pytest

from flext_api import FlextApiClient
from flext_tests import FlextTestsMatchers


@pytest.mark.asyncio
async def test_real_network_error_and_error_formatting() -> None:
    """Test real network error and error message formatting using FlextTestsMatchers."""
    # Use non-responsive localhost port to trigger real connection error
    client = FlextApiClient(
        base_url="http://127.0.0.1:65530",  # Port that won't respond
        timeout=1,  # Quick timeout
    )
    # Note: FlextApiClient doesn't have a start() method

    try:
        # Real network error triggers error path
        result = await client.get("/test")

        # Use FlextTestsMatchers for result validation
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "test" in result.error or "connection" in result.error.lower()
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_read_response_data_real_json_parsing() -> None:
    """Verify JSON parsing with real HTTP response using FlextTestsMatchers."""
    # Use real httpbin.org service for JSON response parsing
    client = FlextApiClient(base_url="https://httpbin.org")
    # Note: FlextApiClient doesn't have a start() method

    try:
        # Real JSON endpoint that returns structured data
        result = await client.get("/json")

        # Use FlextTestsMatchers for result validation
        FlextTestsMatchers.assert_result_success(result)
        response = result.value  # Get the actual response object

        # Verify JSON parsing worked correctly - use .body attribute
        assert isinstance(response.body, dict)
        # httpbin.org /json returns a slideshow example
        assert "slideshow" in json.dumps(response.body)
    finally:
        await client.close()
