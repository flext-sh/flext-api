"""Additional client coverage tests for offline stub and parsing fallbacks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json

import pytest

from flext_api import (
    FlextApiClient,
)


@pytest.mark.asyncio
async def test_real_network_error_and_error_formatting() -> None:
    """Test real network error and error message formatting."""
    # Use non-responsive localhost port to trigger real connection error
    client = FlextApiClient(
        base_url="http://127.0.0.1:65530",  # Port that won't respond
        timeout=0.3,  # Quick timeout
    )
    await client.start()

    try:
        # Real network error triggers error path
        result = await client.get("/test")
        assert not result.success

        # Check error contains expected information
        assert result.error is not None
        assert "test" in result.error or "connection" in result.error.lower()
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_read_response_data_real_json_parsing() -> None:
    """Verify JSON parsing with real HTTP response."""
    # Use real httpbin.org service for JSON response parsing
    client = FlextApiClient(base_url="https://httpbin.org")
    await client.start()

    try:
        # Real JSON endpoint that returns structured data
        res = await client.get("/json")
        assert res.success
        response = res.value  # FlextResult[FlextApiModels.ApiResponse] -> response

        # Verify JSON parsing worked correctly
        assert isinstance(response.data, dict)
        # httpbin.org /json returns a slideshow example
        assert "slideshow" in json.dumps(response.data)
    finally:
        await client.close()
